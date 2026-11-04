// CL-415 RC – jelzőfény-vezérlő
// Board: Seeed XIAO RP2040 (Arduino IDE, "Raspberry Pi Pico/RP2040" core, Earle Philhower)
//
// Bemenet:  D0 – CH5 (futómű) PWM jel a vevőtől, Y-kábelen, feszültségosztón át (4,7k soros / 10k GND)
// Kimenetek (AO3400 MOSFET gate-ekre, 100 ohm soros + 100k lehúzó):
//   D1 – piros villogó (beacon) a törzs tetején
//   D2 – fehér strobe-ok a szárnyvégeken (dupla villanás)
//   D3 – leszállófények (égnek, ha a futó kint van, lágy fel-/lefutással)
// A helyzetfények (piros/zöld/fehér) nem MCU-ról mennek: közvetlenül 5 V-ról, ellenálláson át égnek.

#include <Arduino.h>

// ---- Lábkiosztás ----
const uint8_t PIN_CH5     = D0;
const uint8_t PIN_BEACON  = D1;
const uint8_t PIN_STROBE  = D2;
const uint8_t PIN_LANDING = D3;

// ---- Futómű csatorna ----
const uint16_t GEAR_THRESHOLD_US = 1500;  // a kapcsoló két állása közti határ
const bool     GEAR_DOWN_IS_HIGH = true;  // ha a fény fordítva működik, írd false-ra
const uint32_t SIGNAL_TIMEOUT_MS = 500;   // ennyi jel nélkül -> leszállófény ki

// ---- Villogási minták (ms) ----
const uint16_t BEACON_PERIOD_MS = 1000;   // kb. 60 villanás/perc
const uint16_t BEACON_ON_MS     = 120;

const uint16_t STROBE_PERIOD_MS = 1200;   // dupla villanás 1,2 s-onként
const uint16_t STROBE_FLASH_MS  = 50;
const uint16_t STROBE_GAP_MS    = 80;
const uint16_t STROBE_OFFSET_MS = 500;    // eltolva a beacon-hoz képest

const uint16_t LANDING_FADE_MS  = 600;    // leszállófény fel-/lefutás ideje

// ---- CH5 pulzusmérés megszakításból ----
volatile uint32_t riseUs      = 0;
volatile uint16_t pulseUs     = 0;
volatile uint32_t lastPulseMs = 0;

void onCh5Change() {
  uint32_t now = micros();
  if (digitalRead(PIN_CH5)) {
    riseUs = now;
  } else {
    uint32_t w = now - riseUs;
    if (w >= 800 && w <= 2200) {          // csak érvényes szervójel
      pulseUs = (uint16_t)w;
      lastPulseMs = millis();
    }
  }
}

void setup() {
  pinMode(PIN_CH5, INPUT);
  pinMode(PIN_BEACON, OUTPUT);
  pinMode(PIN_STROBE, OUTPUT);
  pinMode(PIN_LANDING, OUTPUT);
  digitalWrite(PIN_BEACON, LOW);
  digitalWrite(PIN_STROBE, LOW);
  analogWrite(PIN_LANDING, 0);
  attachInterrupt(digitalPinToInterrupt(PIN_CH5), onCh5Change, CHANGE);
}

void loop() {
  uint32_t now = millis();

  // Beacon: rövid piros villanás másodpercenként
  digitalWrite(PIN_BEACON, (now % BEACON_PERIOD_MS) < BEACON_ON_MS);

  // Strobe: dupla fehér villanás
  uint32_t s = (now + STROBE_OFFSET_MS) % STROBE_PERIOD_MS;
  bool strobeOn = (s < STROBE_FLASH_MS) ||
                  (s >= STROBE_FLASH_MS + STROBE_GAP_MS &&
                   s <  2 * STROBE_FLASH_MS + STROBE_GAP_MS);
  digitalWrite(PIN_STROBE, strobeOn);

  // Futómű állapot a CH5-ből
  noInterrupts();
  uint16_t p    = pulseUs;
  uint32_t last = lastPulseMs;
  interrupts();

  bool signalOk = (pulseUs != 0) && (now - last) < SIGNAL_TIMEOUT_MS;
  bool gearDown = signalOk && ((p > GEAR_THRESHOLD_US) == GEAR_DOWN_IS_HIGH);

  // Leszállófény lágy fel-/lefutással
  static float    level = 0.0f;
  static uint32_t lastT = 0;
  uint32_t dt = now - lastT;
  lastT = now;
  float stepAmt = dt * 255.0f / LANDING_FADE_MS;
  float target  = gearDown ? 255.0f : 0.0f;
  if (level < target) level = min(level + stepAmt, target);
  else if (level > target) level = max(level - stepAmt, target);
  analogWrite(PIN_LANDING, (int)level);

  delay(2);
}
