# CL-415 – Alkatrészlista (BOM)

A kapcsolási rajz és a jelölések: [SZERELESI_UTMUTATO.md](SZERELESI_UTMUTATO.md#4-a-fénypanel-megépítése).

## Fényvezérlő

A szárnyban lévő LED-ek előtét-ellenállásai (R10–R15) a szárnyba, a LED mellé kerülnek.

| Jel | Megnevezés | Érték / típus | Db | Megjegyzés |
|---|---|---|--:|---|
| U1 | Mikrokontroller panel | Seeed XIAO RP2040 | 1 | USB-C, Arduino IDE |
| U2 | Step-down modul | MP1584EN, 5,0 V-ra állítva, 3 A | 1 | bemenet 3S (max. 12,6 V) |
| F1 | Önvisszaálló biztosító | PTC 1,5 A | 1 | az akku + ágában |
| C1 | Elektrolit kondenzátor | 220 µF / 10 V | 1 | az 5 V-os sínre, a panel mellé |
| R1 | Ellenállás | 4,7 kΩ 0,25 W | 1 | CH5 osztó, soros |
| R2 | Ellenállás | 10 kΩ 0,25 W | 1 | CH5 osztó, GND felé |
| R3–R5 | Ellenállás | 100 Ω 0,25 W | 3 | gate soros |
| R6–R8 | Ellenállás | 100 kΩ 0,25 W | 3 | gate lehúzó |
| Q1–Q3 | N-csatornás MOSFET | AO3400A, SOT-23 | 3 | 3,3 V-ról teljesen nyit; SOT-23 → DIP adapterre forrasztható |
| R9 | Ellenállás | 10 Ω 1 W | 1 | villogó, kb. 280 mA |
| R10, R11 | Ellenállás | 5,6 Ω 1 W | 2 | strobe, a szárnyvégbe a LED mellé |
| R12, R13 | Ellenállás | 6,8 Ω 1 W | 2 | leszállófény, kb. 260 mA folyamatos |
| R14, R15 | Ellenállás | 150 Ω 0,25 W | 2 | piros és zöld helyzetfény, a szárnyba |
| R16 | Ellenállás | 100 Ω 0,25 W | 1 | fehér farokfény |
| D1 | Teljesítmény-LED | 1 W piros, alu csillagon | 1 | villogó a törzs tetején |
| D2, D3 | Teljesítmény-LED | 1 W hideg fehér, alu csillagon | 2 | strobe, szárnyvégek |
| D4, D5 | Teljesítmény-LED | 1 W fehér, alu csillagon | 2 | leszállófény, belépőél, hűtés kell |
| D6 | LED | 5 mm piros, nagy fényerejű | 1 | bal szárnyvég |
| D7 | LED | 5 mm zöld, nagy fényerejű | 1 | jobb szárnyvég |
| D8 | LED | 5 mm fehér | 1 | farok |
| J1 | Szervókábel / Y-kábel | JR/Futaba, 3 eres | 1 | csak jel és GND, a piros eret kihúzni |
| J2 | Akku leágazás | XT60 Y-kábel vagy forrasztott leágazás | 1 | a főakkuról |
| J3, J4 | Csatlakozópár | JST-PH 2,0, 3 pólusú | 2 | külső szárnyfelek |
| J5 | Csatlakozópár | JST-PH 2,0, 4 pólusú | 1 | szárny ↔ törzs |
| – | Szilikon vezeték | 26 AWG, piros/fekete/sárga | 6 | méter, becslés |
| – | Lyukraszteres panel | kb. 30×50 mm | 1 | vagy saját NYÁK |
| – | Zsugorcső, UV-ragasztó | vegyes | 1 | csomag; vízzárás |

## Teljes gép

A mennyiségek a 180 cm-es Paper-Replika tervhez szólnak. A habmennyiség és a vezetékhossz becslés, kb. 30% tartalékkal.

| Tétel | Megnevezés | Érték / típus | Db | Megjegyzés |
|---|---|---|--:|---|
| **Szerkezet** | | | | |
| – | XPS padlóalátét | 5 mm, sima, fólia nélküli lapok | 4 | m², becslés +30% |
| – | Rétegelt lemez | 3 mm nyír | 1 | tábla (formerek, motortartók, futótalpak) |
| – | Főtartó | a Paper-Replika terv szerint | 1 | készlet |
| – | PP hullámlemez (coroplast) | 2–3 mm | 1 | tábla, a hajótest aljára és a lépcsőre |
| – | Üvegszövet | 25–50 g/m² | 1 | m², hajótest alja |
| – | Laminálóepoxi | 2 komponensű | 200 | g |
| – | Kontaktragasztó | UHU Por | 2 | tubus |
| – | Pillanatragasztó | hab-barát (UHU Por-kompatibilis) + aktivátor | 1 | készlet; sima CA oldja az XPS-t |
| – | Gyorsepoxi | 5 perces | 1 | készlet |
| – | Festék és lakk | vízbázisú akril (sárga, piros) + vízbázisú lakk | 1 | készlet; spray és oldószeres festék tilos |
| – | Kormánylap-zsanér | CA-zsanér vagy erős szalag | 1 | csomag |
| – | Tolórúd + bowdencső | 1,2 mm acél, 2 mm cső | 3 | méter |
| – | Kormánykar | műanyag, csavaros | 8 | db |
| – | Csavarok | M3 csavar + önzáró anya, vegyes | 1 | készlet; orrfutó és motortartó rögzítés |
| **Hajtás** | | | | |
| M1, M2 | Kefe nélküli motor | 2830 méret, 1000–1100 kV | 2 | a Paper-Replika szerint |
| ESC1, ESC2 | Fordulatszabályzó | 40 A | 2 | BEC piros ere megszakítva |
| – | Légcsavar CW | 8×6 négytollú | 2 | egy tartalék |
| – | Légcsavar CCW | 8×6 négytollú | 2 | egy tartalék; ellentétes forgású pár |
| – | Akku | 3S LiPo 2200–3300 mAh, XT60 | 2 | a nehézségi pont szerint választva |
| – | ESC Y-kábel | JR, gázcsatornára | 1 | CH3 |
| **RC és tápellátás** | | | | |
| – | Adó | Turnigy TGY-i10 | 1 | **meglévő** |
| – | Vevő | FlySky FS-iA10B, 10 csatorna, i-BUS | 1 | a TGY-iA6B helyett |
| – | UBEC | 5–6 V, min. 5 A | 1 | a vevő és a szervók tápja |
| – | Szervó | 9 g, műanyag fogaskerekes | 7 | 2 csűrő, 1 magassági, 1 oldal, 1 vízikormány, 2 fékszárny |
| – | Y-kábel | JR | 3 | csűrő, fékszárny, oldal + vízikormány |
| – | Elosztó a CH5-re | JR, 1→4 | 1 | 3 futószervó + fénypanel jele |
| – | Szervó hosszabbító | 30 cm | 6 | a szárnyba |
| **Futómű** | | | | |
| – | Vízálló szervó | 9–12 g, fém fogaskerekes | 3 | futók mozgatása a száraz térből |
| – | Futószár | 3 mm rugóacél drót | 1 | méter |
| – | Főkerék | 45–55 mm, könnyű habkerék | 2 | db |
| – | Orrkerék | 35–45 mm, könnyű habkerék | 1 | db |
| – | Tömítő átvezetés | zsírozott sárgaréz cső + szilikon | 3 | tolórúd az aknafalon át |
| **Telemetria** | | | | |
| – | Feszültségszenzor | TGY-CVT01 | 1 | **meglévő** |
| – | Hőmérsékletszenzor | TGY-CTM01 | 1 | **meglévő** ESC hűtőbordára |
| – | Fordulatszám-szenzor | TGY-CPD01 mágneses | 1 | **meglévő** mágnes a motorharangra |
| **Jelzőfények** | | | | |
| – | Fényvezérlő | lásd a fényvezérlő BOM-ot | 1 | készlet |
