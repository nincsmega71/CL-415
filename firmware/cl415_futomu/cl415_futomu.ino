// =====================================================================
//  CL-415 RC – futómű-vezérlő (főfutó v2 + orrfutó)
//  Board:  Seeed XIAO RP2040  (arduino-pico core, Earle Philhower)
//
//  Mit csinál:
//   - a vevő CH5 (futómű) PWM jelét olvassa;
//   - a főfutó 2 behúzó és 2 reteszelő szervóját együtt mozgatja egy táblázat
//     szerint (mozgas_tabla.h, a cad/gen_futomu_v2.py számolja), hogy a láb,
//     a lengőkar és a merevítő ne feszüljön egymásnak;
//   - az orrfutó szervóját ugyanazzal az ütemmel mozgatja;
//   - jelvesztéskor kiengedi a futót.
//
//  Bekötés:
//   D7  <- vevő CH5 jel (fehér/sárga) osztón át: 4,7 kΩ sorosan, 10 kΩ a D7-ről GND-re
//          (az RP2040 lába nem bírja az 5 V-ot)
//   D0  -> behúzó szervók (Y-kábel, a két szervó tükrözve beépítve)
//   D1  -> reteszelő szervók (Y-kábel, tükrözve)
//   D2  -> orrfutó szervó
//   5V / GND: a szervók és a XIAO 5V lába külön 5 V-os BEC-ről kapják a tápot
//             (min. 3 A, mert az 5 szervó egyszerre mozog); közös GND a vevővel.
// =====================================================================
#include <Arduino.h>
#include <Servo.h>
#include "mozgas_tabla.h"

// ----------------------------------------------------------- beállítások
const pin_size_t PIN_CH5     = D7;
const pin_size_t PIN_BEHUZO  = D0;
const pin_size_t PIN_RETESZ  = D1;
const pin_size_t PIN_ORR     = D2;

// CH5: melyik állás jelenti a kiengedett futót
const bool  KI_HA_ALACSONY   = true;     // true: 1500 µs alatt kiengedve
const int   KUSZOB_US        = 1500;
const int   HISZTEREZIS_US   = 100;

// a teljes mozgás ideje (behúzott <-> kiengedett)
const uint32_t MOZGAS_IDO_MS = 4000;

// szervók: középállás (µs), µs/fok, irány (+1 / -1)
// MG90S: kb. 10–11 µs/fok. Az irányt az első próbánál állítsd be (lásd a leírást).
const float BEHUZO_KOZEP_US  = 1500.0f;
const float RETESZ_KOZEP_US  = 1500.0f;
const float US_PER_FOK       = 10.6f;
const int   BEHUZO_IRANY     = +1;
const int   RETESZ_IRANY     = +1;
// finomhangolás a két végállásban (fok): a reteszelt (kiengedett) helyzetben
// a merevítő 2–3 fokkal túl legyen az egyenesen, az ütközőn.
const float RETESZ_KI_TRIM   = 0.0f;
const float RETESZ_BE_TRIM   = 0.0f;
const float BEHUZO_KI_TRIM   = 0.0f;
const float BEHUZO_BE_TRIM   = 0.0f;

// orrfutó: impulzus behúzva / kiengedve
const int   ORR_BE_US        = 1900;
const int   ORR_KI_US        = 1100;

// jelvesztés: ennyi ideig nincs érvényes impulzus -> kiengedés
const uint32_t JELVESZTES_MS = 500;

// ----------------------------------------------------------- PWM mérés
volatile uint32_t emelkedes_us = 0;
volatile uint16_t impulzus_us = 0;
volatile uint32_t utolso_jel_ms = 0;

void ch5Megszakitas() {
  uint32_t most = micros();
  if (digitalRead(PIN_CH5)) {
    emelkedes_us = most;
  } else {
    uint32_t sz = most - emelkedes_us;
    if (sz >= 800 && sz <= 2200) {
      impulzus_us = (uint16_t)sz;
      utolso_jel_ms = millis();
    }
  }
}

// ----------------------------------------------------------- mozgás
Servo behuzo, retesz, orr;
float t = 1.0f;          // 0 = behúzva, 1 = kiengedve
float cel = 1.0f;
uint32_t elozo_ms = 0;

float tablaErtek(const float *tabla, float tt) {
  float x = tt * (MOZGAS_PONTOK - 1);
  int i = (int)x;
  if (i >= MOZGAS_PONTOK - 1) return tabla[MOZGAS_PONTOK - 1];
  if (i < 0) return tabla[0];
  float f = x - i;
  return tabla[i] + (tabla[i + 1] - tabla[i]) * f;
}

void szervokKi(float tt) {
  float b = tablaErtek(BEHUZO_SZOG, tt) + BEHUZO_BE_TRIM * (1 - tt) + BEHUZO_KI_TRIM * tt;
  float r = tablaErtek(RETESZ_SZOG, tt) + RETESZ_BE_TRIM * (1 - tt) + RETESZ_KI_TRIM * tt;
  behuzo.writeMicroseconds((int)(BEHUZO_KOZEP_US + BEHUZO_IRANY * b * US_PER_FOK));
  retesz.writeMicroseconds((int)(RETESZ_KOZEP_US + RETESZ_IRANY * r * US_PER_FOK));
  orr.writeMicroseconds((int)(ORR_BE_US + (ORR_KI_US - ORR_BE_US) * tt));
}

float celAJelbol(uint16_t us, float elozo) {
  bool alacsony;
  if (us < KUSZOB_US - HISZTEREZIS_US) alacsony = true;
  else if (us > KUSZOB_US + HISZTEREZIS_US) alacsony = false;
  else return elozo;                                   // holtsáv: marad
  bool ki = (alacsony == KI_HA_ALACSONY);
  return ki ? 1.0f : 0.0f;
}

void setup() {
  pinMode(PIN_CH5, INPUT);
  attachInterrupt(digitalPinToInterrupt(PIN_CH5), ch5Megszakitas, CHANGE);
  pinMode(LED_BUILTIN, OUTPUT);

  // indításkor 1 másodpercig várjuk a jelet, és mozgás nélkül a kért állásba állunk
  uint32_t kezd = millis();
  while (millis() - kezd < 1000 && impulzus_us == 0) delay(10);
  if (impulzus_us != 0) cel = celAJelbol(impulzus_us, 1.0f);
  t = cel;

  behuzo.attach(PIN_BEHUZO, 500, 2500);
  retesz.attach(PIN_RETESZ, 500, 2500);
  orr.attach(PIN_ORR, 500, 2500);
  szervokKi(t);
  elozo_ms = millis();
}

void loop() {
  uint32_t most = millis();
  noInterrupts();
  uint16_t us = impulzus_us;
  uint32_t jel = utolso_jel_ms;
  interrupts();

  if (us == 0 || most - jel > JELVESZTES_MS) cel = 1.0f;   // jelvesztés: kiengedés
  else cel = celAJelbol(us, cel);

  float dt = (most - elozo_ms) / (float)MOZGAS_IDO_MS;
  elozo_ms = most;
  if (t < cel) t = min(cel, t + dt);
  else if (t > cel) t = max(cel, t - dt);

  szervokKi(t);
  digitalWrite(LED_BUILTIN, (t != cel) ? LOW : HIGH);    // a XIAO LED-je mozgás közben világít
  delay(10);
}
