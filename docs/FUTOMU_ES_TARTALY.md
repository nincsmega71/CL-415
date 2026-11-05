# Futómű és víztartály – méretezett terv

Ez a fejezet a behúzható futóművet és az 500 ml-es víztartályt írja le úgy, hogy SolidWorksben (vagy bármilyen CAD-ben) tovább lehessen modellezni:

- méretezett rajzok (`docs/img/`);
- a sík alkatrészek DXF-ben (`cad/dxf/`), 1:1 méretben, mm-ben;
- 3D alkatrészek és összeállítások STEP-ben (`cad/step/`), a nyomtatható részek STL-ben is;
- paraméterlista a SolidWorks egyenletkezelőjéhez (`cad/cl415_parameterek.txt`);
- a generáló programok (`cad/gen_futomu_tartaly.py` a rajzokhoz és DXF-hez, `cad/gen_step.py` a STEP-hez). Ha egy méret változik, ezzel minden rajz és DXF újra előállítható.

A törzs méretei a Paper-Replika terv formereiből vannak lemérve (belső szélesség 155 mm, V-fenék kb. 24°-os hajlással, a chine kb. 34 mm-rel a gerinc felett).

---

## 1. Koordináta-rendszer

Minden rajz és DXF ugyanazt használja, hogy a SolidWorks-összeállításban egyszerű legyen illeszteni.

| Tengely | Nullpont | Irány |
|---|---|---|
| x (oldalirány) | a törzs középsíkja | jobbra pozitív (elölnézetben) |
| y (függőleges) | a gerinc legalsó pontja a futómű-formernél | felfelé pozitív |
| hossz | a súlypont (SP) | hátrafelé pozitív |

## 2. Főfutó

![Főfutó elölnézetben](img/futomu_elol.svg)

### 2.1 Működés

Párhuzamos karos (paralelogramma) mechanizmus a hajótest oldalán, mint az igazi CL-415-ön:

- két egyforma kar oldalanként, a hajótest külső oldalára ragasztott konzolon forog;
- a láb a karok végén függőleges marad, a kerék mindig függőlegesen áll;
- **behúzva** a kerék a hajótest oldalán, a vízvonal felett van, ezért a főfutónak nem kell akna;
- **kiengedve** a kerék oldalra és lefelé kilendül, a nyomtáv kb. 331 mm (az igazi gép 5,28 m-es nyomtávja 1:15,9 arányban).

### 2.2 Fő méretek

| Méret | Érték |
|---|---|
| Felső csukló a falon | x = 86, y = 90 mm |
| Alsó csukló a falon | x = 86, y = 66 mm |
| Kar csuklótávolsága | 70 mm (mindkét kar) |
| Kar szöge behúzva / kiengedve | +85° / −25° (110°-os elfordulás) |
| Láb csuklói a tengely felett | 60 és 36 mm |
| Tengely a láb vonalától kifelé | 16 mm |
| Tengely behúzva | x = 108, y = 100 mm (a kerék alja kb. 69 mm-rel a gerinc felett) |
| Tengely kiengedve | x = 165, y = 0 mm |
| Főkerék | 62 mm átmérő, 22 mm széles |
| Gerinc magassága a talaj felett | kb. 30 mm |

### 2.3 Mozgatás

- **Egy közös szervó** középen, a futómű-formeren (száraz tér). Két tolórúd megy belőle a két oldalra.
- A tolórudak a hajótest oldalán, a vízvonal felett (y = 74–98 mm) kis résen jutnak ki. A rést gumiharang zárja.
- A tolórúd a felső kar 10 mm-es fülére kapcsolódik; a szervókar kb. 11 mm-es.
- **Reteszelés:** kiengedett helyzetben a szervókar és a tolórúd egy vonalba áll (holtpont). Így leszálláskor a terhelés nem a szervó fogaskerekeit nyomja.
- Szervó: MG90S vagy hasonló, fém fogaskerekes, 9–12 g. Nem kell vízálló, mert a száraz térben van.

### 2.4 Anyagok

| Alkatrész | Anyag | Darab | DXF |
|---|---|---|---|
| Alsó kar | 2 mm alumínium, 10 mm széles | 2 | `fofuto_kar_also.dxf` |
| Felső kar füllel | 2 mm alumínium | 2 | `fofuto_kar_felso.dxf` |
| Konzolfül | 3 mm rétegelt lemez | 4 (oldalanként 2) | `fofuto_konzol_ful.dxf` |
| Láb | 8×8 mm alumínium zártszelvény, 68 mm | 2 | `fofuto_lab_furatok.dxf` (furatkép) |
| Futómű-former | 3 mm rétegelt lemez | 1 | `fofuto_former.dxf` |
| Csuklók | M3 csavar, önzáró anya, alátét | 8 | – |
| Tengely | M3 csavar, kerékagy-rögzítő | 2 | – |

A két konzolfül a futómű-former első és hátsó lapjára ragad (20 mm-es nyelvvel, epoxival), és a hajótest oldalfalán vágott kb. 9 × 38 mm-es résen át 8,5 mm-re kiáll. A két fül között, a former vastagságának megfelelő 3 mm-es résben forognak a karok (2 mm vastagok, két oldalt egy-egy alátéttel). Így a leszállás terhelése a formerre jut, nem a habra.

Rétegek elölről hátrafelé (z irányban): első konzolfül – kar – hátsó konzolfül. A láb a karok elé, közvetlenül a kar első lapjára csavarozódik. A rés a vízvonal felett (y = 56–94 mm) van; a fülek körül epoxival, a karok körül szilikonnal zárd le, hogy fröccsenő víz ne jusson a törzsbe.

Behúzott helyzetben a láb alja 2 mm-rel a konzolfül teteje felett áll meg, ezért a fülek magassága (y = 56–94 mm) ne legyen nagyobb.

## 3. Orrfutó

| Méret | Érték |
|---|---|
| Kerekek | 2× 40 mm (ikerkerék, mint az igazi gépen) |
| Behúzás | hátrafelé, kb. 90°-kal |
| Csukló | kb. 20 mm-rel a gerinc felett |
| Láb hossza | 59 mm (csuklótól tengelyig) |
| Akna | kb. 80 × 50 × 45 mm, nedves akna (kifelé nyitott, befelé zárt) |
| Aknaajtó | 85 × 52 mm-es lap, a lábra ragasztva; behúzva lezárja az aknát |
| Tengelytáv (orr- és főfutó) | kb. 450 mm |
| Mozgatás | saját szervó a száraz térben, tolórúd tömített csövön át, holtponti reteszeléssel |
| Kormányzás | nincs; a kerekek szabadon elfordulnak, rugó tartja őket egyenesben |

DXF: `orrfuto_lab.dxf`, `orrfuto_aknaajto.dxf`.

## 4. Víztartály

![Tartály keresztmetszet](img/tartaly_metszet.svg)

| Méret | Érték |
|---|---|
| Külső szélesség | 130 mm (belső 126 mm) |
| Hossz | 72 mm külső (68 mm belső) |
| Alja | V-alakú, 24°-os hajlással; pontosan a hajótest fenekére fekszik |
| Teteje | 88 mm-rel a gerinc felett |
| Térfogat | kb. 557 ml teljesen; az 500 ml-es szint kb. 81 mm-nél van |
| Rekeszek | 2 (hosszanti válaszfal középen), hogy fordulóban a víz ne zúduljon egy oldalra |
| Hely | középen a súlypont alatt, így tele és üresen sem mozdul a súlypont |
| Anyag | 2 mm PETG (3D-nyomtatott) vagy PET-lemez ragasztva, belül epoxival lekenve |

DXF: `tartaly_eleje_hatulja.dxf`, `tartaly_oldal.dxf`, `tartaly_valaszfal.dxf`, `tartaly_teto.dxf`, `tartaly_fenek.dxf` (ajtónyílással, 2 db tükrözve).

### 4.1 Ürítőajtók

- Rekeszenként egy ajtó a V-fenék két felén, 50 × 34 mm-es nyílással, a gerinctől 8 mm-re.
- Az ajtó a chine felőli hosszú élén csuklós, befelé, a gerinc felé nyílik lefelé.
- **Egy szervó nyitja mindkettőt**, felülről, tömített csövön átmenő tolórúddal. Pozitív mozgatás: a szervó zárja is az ajtókat, nem rugó.
- Az ajtólap 52 × 36 mm-es (körben 1 mm átfedés), 1 mm PET, szilikon tömítőcsíkkal (`urito_ajto.dxf`).

### 4.2 Merítőlapok

Az eredetileg tervezett merítőcsövek helyett két csuklós lap az igazi géphez hasonlóan:

- a **lépcső mögött**, a gerinc két oldalán, 10 × 15 mm-es ráccsal ellátott nyílással (`merito_lap.dxf`);
- az első élükön csuklósak, 25–30°-ot nyílnak a vízbe, és a víz sebessége rövid csatornán át felnyomja a vizet a tartályba;
- **egy szervó** mozgatja mindkettőt;
- becsült töltési sebesség 4–6 m/s siklásnál kb. 0,3–0,45 l/s, tehát 500 ml kb. 1,5 másodperc alatt jön össze. Ha túl gyors vagy túl lassú, a nyílás betéttel szűkíthető.

## 5. Helyek oldalnézetben

![Oldalnézet](img/futomu_tartaly_oldal.svg)

![Alulnézet](img/futomu_tartaly_alul.svg)

| Elem | Hely a súlyponttól |
|---|---|
| Tartály | −36 … +36 mm |
| Ürítőajtók | −25 … +25 mm |
| Lépcső | +38 mm |
| Főfutó-tengely és futómű-former | +45 mm (a SP és a tengely közti szög kb. 24°) |
| Merítőlapok | kb. +50 mm |
| Orrfutó tengelye | kb. −405 mm |

A főfutó a súlypont mögött kb. 24°-kal van. Így a gép nem ül a farkára, és felszálláskor könnyen elemelhető az orr.

## 6. Szervók összesen

| Feladat | Darab | Vezérlés |
|---|---|---|
| Főfutó (mindkét oldal) | 1 | CH5, Y-kábellel az orrfutó szervójával közösen |
| Orrfutó | 1 | CH5 |
| Ürítőajtók | 1 | XIAO D5 (CH9 felső állás) |
| Merítőlapok | 1 | XIAO D9 (CH9 alsó állás) |

Mind a négy szervó a száraz térben ül, ezért nem kell vízálló típus.

## 7. 3D modellek (STEP)

![STEP előnézet](img/step_elonezet.png)

| Fájl | Tartalom |
|---|---|
| `cad/step/fofuto_kiengedve.step` | főfutó-összeállítás kiengedve: former, 4 konzolfül, 4 kar, 2 láb, 2 kerék csapágyakkal, távtartóval, tengellyel |
| `cad/step/fofuto_behuzva.step` | ugyanez behúzva |
| `cad/step/orrfuto.step` | orrfutó-láb 2 kerékkel (kiengedve, a csukló az origóban) |
| `cad/step/tartaly.step` | tartály válaszfallal és ajtónyílásokkal, fedél, 2 ürítőajtó |
| `cad/step/alkatreszek/` | minden alkatrész külön STEP-ben; a tartály, a fedél, a merítőlap és a kerekek STL-ben is, 3D-nyomtatáshoz |

Megnyitás SolidWorksben: **File → Open**, fájltípus **STEP**. Az összeállítások összeállításként nyílnak meg, minden alkatrész külön, saját színnel. A koordináták az 1. pont szerintiek (a Z tengely előre mutat).

A kerekek egyszerűsített modellek: 62 × 22 mm-es főkerék 8 mm-es, 4 mm mély csapágyfészekkel (693) mindkét oldalon, és 40 × 15 mm-es orrkerék 6 mm-es, 2,5 mm mély fészekkel (MR63). Ha kész kereket veszel, a modellt a megvett kerék méreteihez igazítsd.

A tartály 2 mm-es fallal kb. 73 cm³ PETG, ami kb. 95 g. Ha könnyíteni kell, 1,5 mm-es fallal is vízzáró, ha epoxival lekened.

## 8. SolidWorks-ben

1. **Paraméterek:** Eszközök → Egyenletek → Importálás, és válaszd a `cad/cl415_parameterek.txt` fájlt. A méreteket ezekre a globális változókra kötheted; ha egy változik, a modell követi.
2. **Sík alkatrészek:** Fájl → Megnyitás → DXF → „Importálás új alkatrészbe vázlatként”, mértékegység mm. Rétegek:
   - `KONTUR`: a körvonal és a kivágások;
   - `FURAT`: a furatok;
   - `SZOVEG`: megjegyzés (anyag, darabszám); ezt importáláskor kikapcsolhatod.

   A vázlatból kihúzással (Extrude) lesz alkatrész a megadott vastagsággal.
3. **Összeállítás:** a koordináta-rendszer az 1. pont szerint; a futómű-former síkja a súlyponttól 45 mm-re hátra.
4. **A mozgás ellenőrzése:** a karokat csuklós kényszerrel (Concentric) kösd a konzolhoz és a lábhoz, és egy szögkényszerrel (+85° … −25°) végig tudod forgatni a mechanizmust.

> A rajzok a Paper-Replika terv lemért formereihez készültek. Mielőtt alkatrészt vágsz, mérd le a saját megépített törzsedet (különösen a chine magasságát és az oldalfal helyét), és ha eltér, írd át a paraméterlistában vagy a generálóprogramban.
