# Turnigy/FlySky i10 – a gyári firmware vizsgálata

Cél: kideríteni, hogy a gyári szoftver módosítható-e (grafika, kijelzett adatok, menük).

A vizsgált fájl a FlySky hivatalos frissítőprogramja: `Flysky_i10-US_1.1.0.2_Update firmware.exe`, a gyártó saját nyilvános GitHub-tárolójából ([flysky-rc/FLYSKY-ProductInformationDownload](https://github.com/flysky-rc/FLYSKY-ProductInformationDownload/tree/master/Transmitter/FS-i10)). A programot nem futtattam, csak a tartalmát elemeztem.

---

## 1. Mi van a frissítőprogramban

A Windowsos program USB HID-en (mint egy játékvezérlő) beszél az adóval, és két beépített csomagot tölt fel:

| Csomag | Eredeti név a programban | Méret kicsomagolva | Tartalom |
|---|---|---|---|
| program | `FS_i10_US_Code.binz` | 353 KB | maga az adó szoftvere (menük, logika, telemetria) |
| adatok | `FS_i10_US_Data.binz` | 4 MB | a külső flash-memória teljes tartalma: grafikák, súgószövegek |

**Egyik sincs titkosítva**, csak zlib-bel tömörítve. Az adatcsomag 4 KB-os, egyenként tömörített blokkokból áll (1024 db), ez egy 4 MB-os soros flash chip pontos képe.

A program szövegei szerint a frissítés lépései: a flash törlése, programozása és visszaellenőrzése. A program CRC32 ellenőrzőösszeget is tartalmaz. A program három külön bootloader-fájl nevét is ismeri; a bootloader tehát külön rész, amit a normál frissítés valószínűleg nem ír felül.

## 2. A grafika

Az adatcsomagban a képek **tömörítetlen RGB565 formátumban** vannak (16 bit/képpont, a kijelző saját formátuma). Az átlátszó részeket bíborszín (magenta) jelöli. Felismerhetően megvannak benne:
- a kezdőképernyő trimm- és tekerőkijelzői (F/B, L/R, TX feliratok);
- a gombok és a menüsávok;
- a görbeszerkesztők rácsai;
- a szervó- és adó-ikonok;
- az „Igen/Nem” párbeszédablakok.

Mellette egyszerű szövegként vannak a súgószövegek („Airplane structure”, „Reverse”, „RX setup” stb.).

**Következmény:** a grafikák és a szövegek elvileg cserélhetők: azonos méretű képet ugyanarra a helyre írva, a programhoz nem kell hozzányúlni. Például saját indítókép, más színvilág, átrajzolt ikonok, magyar súgó.

### 2.1 A képtáblázat megvan

A programkódban a képeket 16 bájtos leírók írják le (ugyanaz az elv, mint a régi sprite-lapoknál):

| Mező | Méret | Jelentés |
|---|---|---|
| cím | 4 bájt | a kép kezdete a flash-ben; a processzor a flash-t a **0x40000000** címtől látja |
| szélesség | 4 bájt | képpont |
| magasság | 4 bájt | képpont |
| átlátszó szín | 4 bájt | általában 0xA897 (ez a szín nem rajzolódik ki) |

A kép adata a megadott címtől kezdve soronként, szélesség × magasság × 2 bájt, tömörítetlen RGB565.

**Eredmény:** 305 kép leírója, a 4 MB-os flash kb. 76%-a. A képek többsége hibátlanul kiexportálható: menüikonok, gombok, kapcsolók, mérőórák, görberácsok, a helikopter-tányérok rajzai, a repülőgép-típusválasztó képek, még a beépített 2,4 GHz-es spektrumelemző háttere is. Kb. 40–50 leíró hibás képet ad: ezek vagy nem képleírók (véletlen egyezés), vagy más formátumú (pl. betűkészlet vagy maszk) adatok. Ezeket külön kell majd megvizsgálni.

**Mit jelent ez:** egy képcserélő eszköz megírható. A leíró megmondja, melyik képet hová és milyen méretben kell visszaírni, így a lecserélt kép pontosan a helyére kerül.

### 2.2 A Turnigy-változat (a saját adón futó firmware)

Az adón: **TGY-i10, szoftver 1.08-TGY (2016.05.11.), hardver 2.1.** A FlySky frissítője a Turnigy-márkás adót nem ismeri fel (más a gyártói kód), ezért a Turnigy saját frissítőjét vizsgáltam: `Turnigy TGY-i10 firmware 1.0.8.0 update.exe`.

- Ugyanaz a felépítés: `HK-i10_Code.binz` (program, 357 KB) és `HK-i10_Data.binz` (4 MB adat), titkosítás nélkül, zlib-tömörítéssel.
- Ugyanaz a 16 bájtos képleíró formátum: **302 kép**, a menük, ikonok, mérőórák, görberácsok és a kezdőképernyő (RX/TX telemetria-háttér) hibátlanul kiexportálható. A Turnigy-változatban a multikopter-típus képei is benne vannak.
- **A képek címei teljesen eltérnek a FlySky-változattól** (egyetlen közös cím sincs, mind az 1024 blokk különbözik). A képcserélő eszköznek ezért a Turnigy-firmware saját táblázatával kell dolgoznia.
- A frissítő ugyanúgy tiltja a régebbi verzió feltöltését. A saját adódon már ugyanez az 1.0.8.0 fut; hogy azonos verziót újra feltölt-e, azt még ki kell deríteni.

## 3. A program (a menük és a kijelzett adatok)

- A kód **ARM (32 bites, nem Thumb) utasításkészletű**, és a 0x30000000-s címtől fut (külső RAM). Ez nem egy STM32 Cortex-M mikrovezérlő jellemzője, hanem egy erősebb, ARM7/ARM9 osztályú processzoré. Lehet, hogy mellette van egy STM32 is (pl. a botokhoz vagy a rádióhoz), de a kijelzőt és a menüket ez az ARM processzor futtatja.
- A formázó szövegek alapján a szoftver már most is tud: feszültséget (V), százalékot, sebességet (km/h), magasságot (m), GPS koordinátát, jelerősséget (dBm), RX ID-t, időt kijelezni.
- **Új menü vagy több kijelzett adat** a programkód módosítását igényelné. Ehhez a 353 KB-os gépi kódot vissza kellene fejteni (pl. Ghidra-val). Ez lehetséges, de sok hét munka.

## 4. Akadályok és kockázatok

| Akadály | Mit jelent |
|---|---|
| **Gyártói kód (Company code)** | A frissítő kiolvassa és kijelzi az adó gyártói kódját. A FlySky szerint az AU, IT és német változatok nem frissíthetők; nagy valószínűséggel ez a kód szűri ki őket. A Turnigy-márkás i10 kódja ismeretlen. |
| **Visszaléptetés tiltva** | „Firmware cannot be downgraded”: régebbi verzió nem tölthető fel. |
| **Ellenőrzés** | A frissítő visszaolvassa és ellenőrzi a flash tartalmát. Ez a módosított, de helyesen feltöltött tartalmat nem akadályozza, a hibásan feltöltöttet jelzi. |
| **Visszaállítás** | Nem tudjuk, hogy egy félresikerült frissítés után a bootloader életben marad-e. Ha igen, az eredeti firmware visszatölthető; ha nem, az adó használhatatlanná válhat. |

## 5. Biztonságos következő lépés: csak kiolvasás

A frissítő **a csatlakoztatás után az „Update” gomb megnyomása nélkül** kijelzi az adó adatait. Ezzel kockázat nélkül kiderül, hogy a Turnigy i10 egyáltalán szóba áll-e a FlySky frissítővel:

1. Windowson indítsd el a frissítőt (hivatalos FlySky program).
2. Az i10-et a kézikönyv szerint kapcsold frissítő módba, és kösd USB-re.
3. Írd fel: **Company code, Transmitter ID, SW version, HW version, és hogy 16 vagy 32 hops**.
4. **Az „Update” gombot ne nyomd meg.** Zárd be a programot.

Ha a frissítő felismeri az adót és megjeleníti az adatokat, a grafika cseréje reális. Ha nem ismeri fel, vagy más a gyártói kód, akkor a frissítőprogramot is módosítani kellene, és a kockázat jelentősen nő.

## 6. Összegzés

| Cél | Megvalósítható? | Nehézség |
|---|---|---|
| Saját grafika, színek, ikonok | igen, a képtáblázat ismert | közepes; képcsere azonos méretben, saját frissítővel |
| Magyar súgó | valószínűleg igen | közepes; a szövegek hossza kötött |
| Több kijelzett adat, új menük | elvileg igen | nagy; gépi kód visszafejtése |
| Teljesen saját firmware | ebből az adóból nem reális | nagyon nagy |
