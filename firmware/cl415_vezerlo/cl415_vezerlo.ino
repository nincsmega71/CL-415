// =====================================================================
//  CL-415 RC – fedélzeti vezérlő (fények + víz funkció + telemetria)
//  Board:  Seeed XIAO RP2040
//  Core:   "Raspberry Pi Pico/RP2040" (Earle Philhower), Arduino IDE
//  Vevő:   FlySky FS-iA10B, adó: Turnigy TGY-i10
//
//  Mit csinál:
//   1. i-BUS SERVO: egyetlen vezetéken olvassa mind a 10 csatornát.
//   2. Fények: helyzetfény, villogó, strobe, leszállófény a csatornák szerint.
//   3. Víz: töltőnyílás (merítő) és ürítőajtó – két külön szervó egy csatornáról:
//      CH9 alsó állás = töltőnyílás nyitva, középső = mindkettő zárva,
//      felső = ürítőajtó nyitva.
//   4. i-BUS SENS: saját szenzorként adatokat küld az i10 kijelzőjére.
//   5. Jelvesztés: tartály zárva, fények keresési módban.
//
//  Lábkiosztás (XIAO RP2040):
//   D0  (ADC)  akkufeszültség, 33k/10k osztón át
//   D1  (ADC)  vízszint-érzékelő elektróda (opcionális)
//   D2         Q1 villogó (piros, törzs teteje)
//   D3         Q2 strobe (fehér, szárnyvégek)
//   D4         Q4 helyzetfények (piros, zöld, fehér farok)
//   D5         ürítőajtó szervó jel
//   D6  (TX)   SENS busz – 1N4148 diódán át (katód a D6 felé)
//   D7  (RX)   SENS busz – közvetlenül
//   D8         Q3 leszállófény
//   D9         merítőcső szervó jel
//   D10        i-BUS SERVO bemenet (1 kΩ soros ellenálláson át)
// =====================================================================

#include <Arduino.h>
#include <Servo.h>
#include <SerialPIO.h>

// ---------------------------------------------------------------------
//  BEÁLLÍTÁSOK – ezeket nyugodtan módosíthatod
// ---------------------------------------------------------------------

// Teszt mód: a XIAO 5 különböző szenzortípust küld ismert értékekkel.
// Az i10 Sensors menüjében írd fel, melyik jelenik meg, és ennek alapján
// állítsd be lent a CELLA_TIPUS és TARTALY_TIPUS értékét.
//   ext. feszültség 12.34 V | cella 4.12 V | üzemanyag 55 % | hőm. 25.0 °C | ford. 1234
const bool TESZT_MOD = false;

// A SENS láncban a XIAO elé kötött gyári szenzorok száma
// (CVT01, CTM01, CPD01 = 3). A XIAO a következő címeket kapja.
const uint8_t KULSO_SZENZOROK = 3;

// i-BUS szenzortípus-azonosítók
const uint8_t T_HOMERSEKLET = 0x01;   // érték = °C*10 + 400
const uint8_t T_FORDULAT    = 0x02;   // érték = szám
const uint8_t T_KULSO_FESZ  = 0x03;   // érték = V*100
const uint8_t T_CELLA_FESZ  = 0x04;   // érték = V*100
const uint8_t T_UZEMANYAG   = 0x06;   // érték = %

// A teszt eredménye szerint állítandó (ha az i10 nem ismeri a cella vagy
// üzemanyag típust, írd át T_KULSO_FESZ-re, illetve T_HOMERSEKLET-re).
const uint8_t CELLA_TIPUS   = T_CELLA_FESZ;
const uint8_t TARTALY_TIPUS = T_UZEMANYAG;

// Csatornák (1-től számozva, ahogy az adón)
const uint8_t CH_FUTO   = 5;   // futómű, SwB
const uint8_t CH_FLAP   = 6;   // fékszárny, SwA (3 állás)
const uint8_t CH_VIZ    = 9;   // víz funkció, SwF (3 állás): alsó merítés / közép zárva / felső ürítés
const bool VIZ_KAPCSOLO_FORDITVA = false;  // true, ha a kapcsolón fordítva jön ki az alsó és a felső állás
const uint8_t CH_FENY   = 10;  // fénymód, VrA tekerő

const bool FUTO_LENT_HA_MAGAS = true;   // ha fordítva működik: false
const uint16_t FLAP_LESZALLO_FELETT = 1700;  // ennél nagyobb = leszálló fékszárny

// Víztartály
const float TARTALY_ML         = 500.0f;  // tartály hasznos térfogata
const float MERITES_ML_PER_S   = 120.0f;  // becsült töltési sebesség merítéskor (próbával pontosítsd)
const float URITES_ML_PER_S    = 1500.0f; // becsült ürítési sebesség
const bool  VIZSZINT_ERZEKELO  = false;   // true, ha be van szerelve az elektróda
const int   VIZSZINT_KUSZOB    = 2000;    // ADC érték alatt: víz éri az elektródát

// Szervóállások (µs)
const int AJTO_ZARVA  = 1100, AJTO_NYITVA  = 1900;
const int MERITO_BE   = 1100, MERITO_KI    = 1800;

// Akku mérés: 33k / 10k osztó, 3 cella
const float OSZTO_ARANY = (33.0f + 10.0f) / 10.0f;
const float AKKU_KALIB  = 1.000f;   // multiméterrel összevetve finomítható
const uint8_t CELLASZAM = 3;

// Időzítések
const uint32_t JELVESZTES_MS    = 500;
const uint16_t BEACON_PERIOD_MS = 1000, BEACON_ON_MS = 120;
const uint16_t BEACON_GYORS_MS  = 250;   // ürítés közben
const uint16_t STROBE_PERIOD_MS = 1200, STROBE_FLASH_MS = 50, STROBE_GAP_MS = 80;
const uint16_t STROBE_GYORS_MS  = 300;   // keresési mód
const uint16_t LANDING_FADE_MS  = 600;

// ---------------------------------------------------------------------
//  Lábak
// ---------------------------------------------------------------------
const pin_size_t PIN_AKKU     = D0;
const pin_size_t PIN_VIZSZINT = D1;
const pin_size_t PIN_BEACON   = D2;
const pin_size_t PIN_STROBE   = D3;
const pin_size_t PIN_NAV      = D4;
const pin_size_t PIN_AJTO     = D5;
const pin_size_t PIN_SENS_TX  = D6;
const pin_size_t PIN_SENS_RX  = D7;
const pin_size_t PIN_LANDING  = D8;
const pin_size_t PIN_MERITO   = D9;
const pin_size_t PIN_IBUS_RX  = D10;

SerialPIO ibusServo(NOPIN, PIN_IBUS_RX);   // csak vétel
Servo ajtoSzervo, meritoSzervo;

// ---------------------------------------------------------------------
//  i-BUS SERVO: csatornák vétele
//  Keret: 0x20 0x40 + 14 csatorna (2 bájt, little endian) + 2 bájt ellenőrzőösszeg
// ---------------------------------------------------------------------
uint16_t csatorna[14];
uint32_t utolsoKeretMs = 0;
bool     voltKeret = false;
uint8_t  ibBuf[32];
uint8_t  ibIdx = 0;

void ibusServoOlvas() {
  while (ibusServo.available()) {
    uint8_t b = ibusServo.read();
    if (ibIdx == 0) {
      if (b == 0x20) { ibBuf[0] = b; ibIdx = 1; }
      continue;
    }
    if (ibIdx == 1) {
      if (b == 0x40) { ibBuf[1] = b; ibIdx = 2; }
      else if (b == 0x20) { ibBuf[0] = b; ibIdx = 1; }
      else ibIdx = 0;
      continue;
    }
    ibBuf[ibIdx++] = b;
    if (ibIdx == 32) {
      ibIdx = 0;
      uint16_t osszeg = 0xFFFF;
      for (int i = 0; i < 30; i++) osszeg -= ibBuf[i];
      if (osszeg == (uint16_t)(ibBuf[30] | (ibBuf[31] << 8))) {
        for (int c = 0; c < 14; c++)
          csatorna[c] = (ibBuf[2 + c * 2] | (ibBuf[3 + c * 2] << 8)) & 0x0FFF;
        utolsoKeretMs = millis();
        voltKeret = true;
      }
    }
  }
}

uint16_t ch(uint8_t n) { return csatorna[n - 1]; }   // 1-től számozva

// 3 állású érték: 0 = alsó, 1 = közép, 2 = felső
uint8_t harmad(uint16_t v) { return v < 1300 ? 0 : (v > 1700 ? 2 : 1); }

// ---------------------------------------------------------------------
//  i-BUS SENS: saját szenzorok
//  Kérés (vevő):  0x04, parancs|cím, chk lo, chk hi
//    0x80 = keresés, 0x90 = típus, 0xA0 = érték
//  Válasz:        0x04/0x06, parancs|cím, [típus, 0x02] vagy [érték lo, hi], chk
// ---------------------------------------------------------------------
struct Szenzor { uint8_t tipus; uint16_t ertek; };
const uint8_t MAX_SZENZOR = 5;
Szenzor szenzor[MAX_SZENZOR];
uint8_t szenzorDb = 4;
const uint8_t ELSO_CIM = KULSO_SZENZOROK + 1;

uint8_t  snBuf[8];
uint8_t  snIdx = 0, snHossz = 0;
uint32_t snUtolsoBajtUs = 0;
uint8_t  visszhangKihagy = 0;   // a saját adásunk visszhangja

void sensKuld(uint8_t *d, uint8_t hossz) {
  uint16_t osszeg = 0xFFFF;
  for (uint8_t i = 0; i < hossz - 2; i++) osszeg -= d[i];
  d[hossz - 2] = osszeg & 0xFF;
  d[hossz - 1] = osszeg >> 8;
  Serial1.write(d, hossz);
  Serial1.flush();
  visszhangKihagy = hossz;
}

void sensFeldolgoz() {
  while (Serial1.available()) {
    uint8_t b = Serial1.read();
    if (visszhangKihagy) { visszhangKihagy--; continue; }

    uint32_t most = micros();
    if (most - snUtolsoBajtUs > 1500) snIdx = 0;   // szünet = új üzenet
    snUtolsoBajtUs = most;

    if (snIdx == 0) {
      if (b != 0x04 && b != 0x06) continue;
      snHossz = b;
    }
    snBuf[snIdx++] = b;
    if (snIdx < snHossz) continue;
    snIdx = 0;
    if (snHossz != 4) continue;          // csak a vevő 4 bájtos kéréseire felelünk

    uint16_t osszeg = 0xFFFF - snBuf[0] - snBuf[1];
    if (osszeg != (uint16_t)(snBuf[2] | (snBuf[3] << 8))) continue;

    uint8_t parancs = snBuf[1] & 0xF0, cim = snBuf[1] & 0x0F;
    if (cim < ELSO_CIM || cim >= ELSO_CIM + szenzorDb) continue;
    Szenzor &sz = szenzor[cim - ELSO_CIM];

    if (parancs == 0x80) {
      uint8_t v[4] = {0x04, (uint8_t)(0x80 | cim)};
      sensKuld(v, 4);
    } else if (parancs == 0x90) {
      uint8_t v[6] = {0x06, (uint8_t)(0x90 | cim), sz.tipus, 0x02};
      sensKuld(v, 6);
    } else if (parancs == 0xA0) {
      uint8_t v[6] = {0x06, (uint8_t)(0xA0 | cim), (uint8_t)(sz.ertek & 0xFF), (uint8_t)(sz.ertek >> 8)};
      sensKuld(v, 6);
    }
  }
}

uint16_t homErtek(float c) { return (uint16_t)(c * 10.0f + 400.0f); }

// ---------------------------------------------------------------------
//  Állapot
// ---------------------------------------------------------------------
enum VizAllapot { ZARVA, MERITES, URITES };
VizAllapot viz = ZARVA;
float    tartalyMl = 0;
uint16_t uritesekSzama = 0;
bool     megtelt = false;

float cellaFesz = 0;
float landingSzint = 0;

void setup() {
  pinMode(PIN_BEACON, OUTPUT);
  pinMode(PIN_STROBE, OUTPUT);
  pinMode(PIN_NAV, OUTPUT);
  pinMode(PIN_LANDING, OUTPUT);
  digitalWrite(PIN_BEACON, LOW);
  digitalWrite(PIN_STROBE, LOW);
  digitalWrite(PIN_NAV, LOW);
  analogWrite(PIN_LANDING, 0);
  analogReadResolution(12);
  pinMode(PIN_VIZSZINT, INPUT_PULLUP);

  ajtoSzervo.attach(PIN_AJTO, 900, 2100);
  meritoSzervo.attach(PIN_MERITO, 900, 2100);
  ajtoSzervo.writeMicroseconds(AJTO_ZARVA);
  meritoSzervo.writeMicroseconds(MERITO_BE);

  for (int c = 0; c < 14; c++) csatorna[c] = 1500;

  ibusServo.begin(115200);
  Serial1.setTX(PIN_SENS_TX);
  Serial1.setRX(PIN_SENS_RX);
  Serial1.begin(115200);

  if (TESZT_MOD) {
    szenzorDb = 5;
    szenzor[0] = {T_KULSO_FESZ, 1234};
    szenzor[1] = {T_CELLA_FESZ, 412};
    szenzor[2] = {T_UZEMANYAG, 55};
    szenzor[3] = {T_HOMERSEKLET, homErtek(25.0f)};
    szenzor[4] = {T_FORDULAT, 1234};
  } else {
    szenzorDb = 4;
    szenzor[0] = {CELLA_TIPUS, 0};     // akku átlagos cellafeszültség
    szenzor[1] = {TARTALY_TIPUS, 0};   // tartály töltöttsége %
    szenzor[2] = {T_HOMERSEKLET, 0};   // XIAO (fénypanel) hőmérséklete
    szenzor[3] = {T_FORDULAT, 0};      // ürítések száma
  }
}

void loop() {
  ibusServoOlvas();
  sensFeldolgoz();

  static uint32_t elozoMs = 0;
  uint32_t most = millis();
  uint32_t dt = most - elozoMs;
  if (dt < 2) return;                  // kb. 500 Hz-es frissítés, a buszok közben is futnak
  elozoMs = most;
  float dtS = dt / 1000.0f;

  bool jelVan   = voltKeret && (millis() - utolsoKeretMs) < JELVESZTES_MS;
  bool keresesi = voltKeret && !jelVan;   // volt jel, de elveszett

  // ---------------- Víz funkció ----------------
  // CH9: alsó = merítés (töltőnyílás nyitva), közép = zárva, felső = ürítés
  VizAllapot uj = ZARVA;
  if (jelVan) {
    uint8_t h = harmad(ch(CH_VIZ));
    if (VIZ_KAPCSOLO_FORDITVA) h = 2 - h;
    uj = (h == 0) ? MERITES : (h == 2 ? URITES : ZARVA);
  }
  if (uj == URITES && viz != URITES) uritesekSzama++;
  if (uj != MERITES) megtelt = false;
  viz = uj;

  bool vizetErzekel = VIZSZINT_ERZEKELO && analogRead(PIN_VIZSZINT) < VIZSZINT_KUSZOB;

  switch (viz) {
    case ZARVA:
      ajtoSzervo.writeMicroseconds(AJTO_ZARVA);
      meritoSzervo.writeMicroseconds(MERITO_BE);
      break;
    case MERITES:
      ajtoSzervo.writeMicroseconds(AJTO_ZARVA);
      if (!megtelt) tartalyMl += MERITES_ML_PER_S * dtS;
      if (vizetErzekel) tartalyMl = TARTALY_ML;
      if (tartalyMl >= TARTALY_ML) { tartalyMl = TARTALY_ML; megtelt = true; }
      // tele tartálynál a cső magától behúzódik (kisebb fékezés)
      meritoSzervo.writeMicroseconds(megtelt ? MERITO_BE : MERITO_KI);
      break;
    case URITES:
      meritoSzervo.writeMicroseconds(MERITO_BE);
      ajtoSzervo.writeMicroseconds(AJTO_NYITVA);
      tartalyMl -= URITES_ML_PER_S * dtS;
      if (tartalyMl < 0) tartalyMl = 0;
      break;
  }

  // ---------------- Fények ----------------
  uint8_t mod = jelVan ? harmad(ch(CH_FENY)) : 2;   // 0 ki, 1 normál, 2 mind
  bool futoLent    = (ch(CH_FUTO) > 1500) == FUTO_LENT_HA_MAGAS;
  bool flapLeszall = ch(CH_FLAP) > FLAP_LESZALLO_FELETT;

  bool nav = false, beacon = false, strobe = false;
  float landingCel = 0;

  if (!voltKeret) {
    // indulás: még nincs i-BUS adat – csak helyzetfény és lassú villogó
    nav = true;
    beacon = (most % 2000) < BEACON_ON_MS;
  } else if (keresesi) {
    // jelvesztés: minden ég, gyors strobe, hogy könnyű legyen megtalálni
    nav = true;
    beacon = (most % BEACON_GYORS_MS) < (BEACON_GYORS_MS / 2);
    strobe = (most % STROBE_GYORS_MS) < STROBE_FLASH_MS;
    landingCel = 255;
  } else if (mod > 0) {
    nav = true;
    uint16_t bPer = (viz == URITES) ? BEACON_GYORS_MS : BEACON_PERIOD_MS;
    beacon = (most % bPer) < (viz == URITES ? bPer / 2 : BEACON_ON_MS);
    uint32_t s = (most + 500) % STROBE_PERIOD_MS;
    strobe = (s < STROBE_FLASH_MS) ||
             (s >= STROBE_FLASH_MS + STROBE_GAP_MS && s < 2 * STROBE_FLASH_MS + STROBE_GAP_MS);
    if (mod == 2 || futoLent || flapLeszall) landingCel = 255;
  }

  digitalWrite(PIN_NAV, nav);
  digitalWrite(PIN_BEACON, beacon);
  digitalWrite(PIN_STROBE, strobe);

  float lepes = dt * 255.0f / LANDING_FADE_MS;
  if (landingSzint < landingCel) landingSzint = min(landingSzint + lepes, landingCel);
  else if (landingSzint > landingCel) landingSzint = max(landingSzint - lepes, landingCel);
  analogWrite(PIN_LANDING, (int)landingSzint);

  // ---------------- Telemetria értékek ----------------
  float v = analogRead(PIN_AKKU) * 3.3f / 4095.0f * OSZTO_ARANY * AKKU_KALIB / CELLASZAM;
  cellaFesz = (cellaFesz == 0) ? v : cellaFesz * 0.98f + v * 0.02f;   // simítás

  if (!TESZT_MOD) {
    szenzor[0].ertek = (uint16_t)(cellaFesz * 100.0f + 0.5f);
    uint16_t szazalek = (uint16_t)(tartalyMl * 100.0f / TARTALY_ML + 0.5f);
    szenzor[1].ertek = (TARTALY_TIPUS == T_HOMERSEKLET) ? homErtek(szazalek) : szazalek;
    static uint32_t homMs = 0;
    if (most - homMs > 1000) { homMs = most; szenzor[2].ertek = homErtek(analogReadTemp()); }
    szenzor[3].ertek = uritesekSzama;
  }
}
