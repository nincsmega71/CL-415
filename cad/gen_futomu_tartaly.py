# CL-415 futómű és víztartály: geometria, SVG rajzok, DXF alkatrészek, paraméterlista
import math, os, sys
import ezdxf

OUT = sys.argv[1]
IMG = os.path.join(OUT, 'docs', 'img')
CAD = os.path.join(OUT, 'cad')
DXF = os.path.join(CAD, 'dxf')
for d in (IMG, CAD, DXF):
    os.makedirs(d, exist_ok=True)

# ------------------------------------------------------------------ paraméterek (mm)
P = dict(
    torzs_belso_szel=155.0, fal=5.0, chine_mag=34.0, oldal_mag=171.0,
    talaj_y=-30.0,                       # gerinc a talaj felett 30 mm (a fő tengelynél)
    fo_kerek_d=62.0, fo_kerek_sz=22.0,
    fo_csuklo_x=86.0, fo_felso_csuklo_y=90.0, fo_also_csuklo_y=66.0,
    fo_kar_hossz=70.0, fo_szog_behuzva=85.0, fo_szog_kiengedve=-25.0,
    fo_lab_felso_tav=60.0, fo_lab_also_tav=36.0, fo_lab_tengely_kiallas=16.0,
    fo_lab_cso=8.0,
    vizvonal_y=46.0,
    sp_x=0.0, fo_tengely_x=45.0, lepcso_x=38.0, merito_x=50.0, tartaly_hossz=72.0,
    orr_tengelytav=450.0, orr_kerek_d=40.0, orr_lab_hossz=59.0, orr_csuklo_keel_felett=20.0,
    tartaly_kulso_szel=130.0, tartaly_fal=2.0, tartaly_teteje_y=88.0, v_szog=24.0,
    ajto_hossz=50.0, ajto_szel=34.0, merito_nyilas_sz=15.0, merito_nyilas_h=10.0,
)
xs = P['torzs_belso_szel'] / 2 + P['fal']          # külső oldalfal x = 82.5


def fo_allapot(a_deg):
    a = math.radians(a_deg)
    R = P['fo_kar_hossz']
    Bu = (P['fo_csuklo_x'] + R * math.cos(a), P['fo_felso_csuklo_y'] + R * math.sin(a))
    Bl = (P['fo_csuklo_x'] + R * math.cos(a), P['fo_also_csuklo_y'] + R * math.sin(a))
    ax = (Bu[0] + P['fo_lab_tengely_kiallas'], Bu[1] - P['fo_lab_felso_tav'])
    return Bu, Bl, ax


ret = fo_allapot(P['fo_szog_behuzva'])
ext = fo_allapot(P['fo_szog_kiengedve'])
print('behúzva: tengely', [round(v, 1) for v in ret[2]], ' kiengedve: tengely', [round(v, 1) for v in ext[2]])
print('nyomtáv', round(2 * ext[2][0]), 'mm; forgás', P['fo_szog_behuzva'] - P['fo_szog_kiengedve'], '°')

# ------------------------------------------------------------------ SVG segédek
COL = dict(ink='#1d2830', mut='#5b6a72', hull='#888780', arm='#24485e', wheel='#2c2c2a',
           water='#378ADD', ret='#D85A30', dim='#993C1D', tank='#0F6E56', tankf='#E1F5EE', grid='#eef2f2')
FONT = "DejaVu Sans, Arial, Helvetica, sans-serif"


def svg(w, h, title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
            f'<title>{title}</title><defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0 1L9 5L0 9z" fill="{COL["dim"]}"/></marker></defs>'
            f'<style>text{{font-family:{FONT};fill:{COL["ink"]}}}.t{{font-size:13px}}.th{{font-size:15px;font-weight:bold}}.ts{{font-size:11px;fill:{COL["mut"]}}}.d{{font-size:11px;fill:{COL["dim"]}}}</style>'
            f'<rect width="{w}" height="{h}" fill="#fff"/>{body}</svg>')


def dim_h(x1, x2, y, label, T):
    a, b = T(x1, 0)[0], T(x2, 0)[0]
    return (f'<line x1="{a}" y1="{y}" x2="{b}" y2="{y}" stroke="{COL["dim"]}" stroke-width="0.8" marker-start="url(#a)" marker-end="url(#a)"/>'
            f'<text class="d" x="{(a+b)/2}" y="{y-4}" text-anchor="middle">{label}</text>')


def dim_v(x, y1, y2, label, T, side=1):
    a, b = T(0, y1)[1], T(0, y2)[1]
    return (f'<line x1="{x}" y1="{a}" x2="{x}" y2="{b}" stroke="{COL["dim"]}" stroke-width="0.8" marker-start="url(#a)" marker-end="url(#a)"/>'
            f'<text class="d" x="{x+6*side}" y="{(a+b)/2+4}" text-anchor="{"start" if side>0 else "end"}">{label}</text>')

# ------------------------------------------------------------------ 1. főfutó elölnézet
S = 2.0; CX = 520; CY = 470


def T(x, y):
    return (round(CX + x * S, 1), round(CY - y * S, 1))


def pl(pts, **kw):
    s = ' '.join(f'{T(*p)[0]},{T(*p)[1]}' for p in pts)
    st = ' '.join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items())
    return f'<polyline points="{s}" fill="none" {st}/>'


def circ(c, r, **kw):
    st = ' '.join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items())
    x, y = T(*c)
    return f'<circle cx="{x}" cy="{y}" r="{r*S}" {st}/>'


b = ''
# talaj, vízvonal
b += pl([(-210, P['talaj_y']), (210, P['talaj_y'])], stroke=COL['mut'], stroke_width=1)
b += f'<text class="ts" x="{T(-205,0)[0]}" y="{T(0,P["talaj_y"])[1]+14}">talaj (kiengedett futóval)</text>'
b += pl([(-180, P['vizvonal_y']), (178, P['vizvonal_y'])], stroke=COL['water'], stroke_width=1, stroke_dasharray='6 4')
b += f'<text class="ts" x="{T(-175,0)[0]}" y="{T(0,P["vizvonal_y"])[1]-5}" style="fill:{COL["water"]}">vízvonal 500 ml-rel (kb. 46 mm)</text>'
# hajótest keresztmetszet (külső)
hull = [(0, 0), (xs, P['chine_mag']), (xs, P['oldal_mag']), (-xs, P['oldal_mag']), (-xs, P['chine_mag']), (0, 0)]
b += pl(hull, stroke=COL['hull'], stroke_width=2)
b += pl([(-xs + 5, P['chine_mag'] + 2), (-xs + 5, P['oldal_mag'] - 5), (xs - 5, P['oldal_mag'] - 5), (xs - 5, P['chine_mag'] + 2)], stroke=COL['hull'], stroke_width=0.8, stroke_dasharray='3 3')
b += f'<text class="ts" x="{T(0,150)[0]}" y="{T(0,150)[1]}" text-anchor="middle">futómű-former (belül)</text>'
# szervó középen + tolórudak
sv = (0, 95)
b += f'<rect x="{T(-11,101)[0]}" y="{T(-11,101)[1]}" width="{22*S}" height="{12*S}" fill="#F1EFE8" stroke="#5F5E5A"/>'
b += f'<text class="ts" x="{T(0,108)[0]}" y="{T(0,108)[1]}" text-anchor="middle">szervó</text>'


def gear(side, a_deg, colr, label):
    Bu, Bl, ax = fo_allapot(a_deg)
    m = lambda p: (side * p[0], p[1])
    Au = m((P['fo_csuklo_x'], P['fo_felso_csuklo_y'])); Al = m((P['fo_csuklo_x'], P['fo_also_csuklo_y']))
    s = ''
    # konzol a falon
    s += f'<rect x="{min(T(*m((xs,62)))[0],T(*m((xs+8,94)))[0])}" y="{T(0,96)[1]}" width="{8*S}" height="{36*S}" fill="#F1EFE8" stroke="#5F5E5A" stroke-width="0.8"/>'
    s += pl([Au, m(Bu)], stroke=COL['arm'], stroke_width=4)
    s += pl([Al, m(Bl)], stroke=COL['arm'], stroke_width=4)
    top = m(Bu); top = (top[0], top[1] + 6)
    leg_bot = m((ax[0] - P['fo_lab_tengely_kiallas'], ax[1] - 3))
    s += pl([top, leg_bot], stroke=COL['wheel'], stroke_width=P['fo_lab_cso'] * S * 0.9)
    s += pl([m((ax[0] - P['fo_lab_tengely_kiallas'], ax[1])), m(ax)], stroke=COL['wheel'], stroke_width=2)
    cx, cy = T(*m(ax)); hw = P['fo_kerek_sz'] / 2 * S; hr = P['fo_kerek_d'] / 2 * S
    s += f'<rect x="{cx-hw}" y="{cy-hr}" width="{2*hw}" height="{2*hr}" rx="{hw*0.7}" fill="{COL["wheel"]}"/>'
    for p in (Au, Al, m(Bu), m(Bl)):
        s += circ(p, 1.6, fill=colr)
    lx = T(*m((150, 0)))[0]
    s += f'<text class="th" x="{lx}" y="{T(0,190)[1]}" text-anchor="middle" style="fill:{colr}">{label}</text>'
    return s


b += gear(-1, P['fo_szog_behuzva'], COL['ret'], 'BEHÚZVA')
b += gear(1, P['fo_szog_kiengedve'], COL['arm'], 'KIENGEDVE')
# a lábtető pályája (ív) a jobb oldalon
arc = []
for k in range(0, 41):
    a = P['fo_szog_behuzva'] - (P['fo_szog_behuzva'] - P['fo_szog_kiengedve']) * k / 40
    arc.append(fo_allapot(a)[2])
b += pl(arc, stroke=COL['ret'], stroke_width=1, stroke_dasharray='4 3')
b += f'<text class="ts" x="{T(150,70)[0]}" y="{T(150,70)[1]}">a tengely útja</text>'
# méretek
b += dim_h(0, ext[2][0], T(0, P['talaj_y'])[1] + 34, f'félnyomtáv {ext[2][0]:.0f} (nyomtáv {2*ext[2][0]:.0f})', T)
b += dim_h(0, xs, T(0, 0)[1] + 22, f'{xs:.1f}', T)
b += dim_v(T(205, 0)[0], 0, P['fo_felso_csuklo_y'], f'felső csukló {P["fo_felso_csuklo_y"]:.0f}', T)
b += dim_v(T(186, 0)[0], 0, P['fo_also_csuklo_y'], f'alsó csukló {P["fo_also_csuklo_y"]:.0f}', T)
b += dim_v(T(-196, 0)[0], 0, ret[2][1], f'{ret[2][1]:.0f}', T, side=-1)
b += f'<text class="ts" x="{T(-196,0)[0]-6}" y="{T(0,ret[2][1])[1]+18}" text-anchor="end">tengely behúzva</text>'
b += f'<text class="t" x="{T(0,0)[0]}" y="{T(0,0)[1]+14}" text-anchor="middle">gerinc (y = 0)</text>'
# jelmagyarázat
ly = 640
leg = [(COL['arm'], 'kar: 70 mm csuklótávolság, 2 mm alumínium (oldalanként 2 db)'),
       (COL['wheel'], 'láb: 8×8 mm alumínium zártszelvény, 3 mm-es tengelycsavar'),
       ('#5F5E5A', 'konzol: 8 mm-re kiálló fül a hajótest oldalán, a vízvonal felett'),
       (COL['ret'], 'csuklók: M3 csavar + önzáró anya; forgás 110°')]
for k, (c, t) in enumerate(leg):
    b += f'<rect x="40" y="{ly+k*20-10}" width="16" height="10" fill="{c}"/><text class="t" x="64" y="{ly+k*20}">{t}</text>'
b += f'<text class="th" x="40" y="30">Főfutó elölnézetben (a futómű-former síkjában), 1 mm = {S} képpont</text>'
b += f'<text class="ts" x="40" y="48">Bal fél: behúzva, a kerék a hajótest oldalán, a vízvonal felett. Jobb fél: kiengedve. A két oldalt egy közös szervó mozgatja.</text>'
open(os.path.join(IMG, 'futomu_elol.svg'), 'w').write(svg(1080, 730, 'Főfutó elölnézet', b))

# ------------------------------------------------------------------ 2. oldalnézet: állomások
S2 = 0.95; X0 = 560; Y0 = 300


def T2(x, y):
    return (round(X0 + x * S2, 1), round(Y0 - y * S2, 1))


def pl2(pts, **kw):
    s = ' '.join(f'{T2(*p)[0]},{T2(*p)[1]}' for p in pts)
    st = ' '.join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items())
    return f'<polyline points="{s}" fill="none" {st}/>'


nose_x = -P['orr_tengelytav'] + P['fo_tengely_x']           # orrfutó tengelye a SP-hez képest
keel = [(-515, 62), (-480, 40), (-420, 26), (-300, 0), (P['lepcso_x'], 0), (P['lepcso_x'], 10), (700, 70)]


def keel_y(x):
    for (x1, y1), (x2, y2) in zip(keel, keel[1:]):
        if x1 <= x <= x2 and x2 != x1:
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    return 0


b = ''
b += pl2([(-540, P['talaj_y']), (720, P['talaj_y'])], stroke=COL['mut'], stroke_width=1)
b += pl2([(-540, P['vizvonal_y']), (720, P['vizvonal_y'])], stroke=COL['water'], stroke_width=1, stroke_dasharray='6 4')
top = [(-515, 62), (-500, 120), (-440, 160), (-380, 171), (700, 171), (700, 70)]
b += pl2(keel + [(700, 70)], stroke=COL['hull'], stroke_width=2)
b += pl2(top, stroke=COL['hull'], stroke_width=2)
b += pl2([(-60, 171), (-60, 200), (160, 200), (160, 171)], stroke=COL['hull'], stroke_width=1.2)
b += f'<text class="ts" x="{T2(50,190)[0]}" y="{T2(50,190)[1]}" text-anchor="middle">szárny (220 mm húr)</text>'
# SP
cx, cy = T2(0, 128)
b += f'<circle cx="{cx}" cy="{cy}" r="8" fill="#fff" stroke="{COL["ink"]}" stroke-width="1.5"/><path d="M{cx} {cy-8} A8 8 0 0 1 {cx+8} {cy} L{cx} {cy}Z" fill="{COL["ink"]}"/><path d="M{cx} {cy+8} A8 8 0 0 1 {cx-8} {cy} L{cx} {cy}Z" fill="{COL["ink"]}"/>'
b += f'<text class="t" x="{cx}" y="{cy-14}" text-anchor="middle">SP</text>'
# tartály
L = P['tartaly_hossz']
b += f'<rect x="{T2(-L/2,P["tartaly_teteje_y"])[0]}" y="{T2(0,P["tartaly_teteje_y"])[1]}" width="{L*S2}" height="{(P["tartaly_teteje_y"]-5)*S2}" fill="{COL["tankf"]}" stroke="{COL["tank"]}"/>'
b += f'<text class="ts" x="{T2(0,60)[0]}" y="{T2(0,60)[1]}" text-anchor="middle">tartály</text>'
# ürítőajtók (nyitva, szaggatva)
b += pl2([(-25, 3), (-25, -22)], stroke=COL['ret'], stroke_width=2, stroke_dasharray='3 2')
b += pl2([(25, 3), (25, -22)], stroke=COL['ret'], stroke_width=2, stroke_dasharray='3 2')
# lépcső, merítőlap
b += f'<text class="ts" x="{T2(P["lepcso_x"],0)[0]+40}" y="{T2(0,-14)[1]}">lépcső</text><line x1="{T2(P["lepcso_x"],0)[0]+38}" y1="{T2(0,-11)[1]}" x2="{T2(P["lepcso_x"],0)[0]}" y2="{T2(0,4)[1]}" stroke="#5b6a72" stroke-dasharray="3 3"/>'
mx = P['merito_x']
b += pl2([(mx - 8, keel_y(mx) + 0), (mx + 6, keel_y(mx) - 9)], stroke=COL['ret'], stroke_width=3)
b += pl2([(mx + 4, keel_y(mx) + 2), (mx - 4, 40), (-30, 40), (-30, 30)], stroke=COL['tank'], stroke_width=1.5)
# főfutó (kiengedve) a SP mögött
fx = P['fo_tengely_x']
b += pl2([(fx, 90), (fx, 1)], stroke=COL['wheel'], stroke_width=4)
cx, cy = T2(fx, 1)
b += f'<circle cx="{cx}" cy="{cy}" r="{31*S2}" fill="none" stroke="{COL["wheel"]}" stroke-width="5"/>'
# orrfutó
ky = keel_y(nose_x); piv = (nose_x, ky + P['orr_csuklo_keel_felett'])
axe = (nose_x, P['talaj_y'] + P['orr_kerek_d'] / 2)
b += pl2([piv, axe], stroke=COL['wheel'], stroke_width=4)
cx, cy = T2(*axe); b += f'<circle cx="{cx}" cy="{cy}" r="{20*S2}" fill="none" stroke="{COL["wheel"]}" stroke-width="4"/>'
axr = (nose_x + P['orr_lab_hossz'], piv[1])
b += pl2([piv, axr], stroke=COL['ret'], stroke_width=3, stroke_dasharray='4 3')
cx, cy = T2(*axr); b += f'<circle cx="{cx}" cy="{cy}" r="{20*S2}" fill="none" stroke="{COL["ret"]}" stroke-width="2" stroke-dasharray="4 3"/>'
b += pl2([(nose_x - 12, ky + 2), (nose_x - 12, piv[1] + 25), (axr[0] + 24, piv[1] + 25), (axr[0] + 24, keel_y(axr[0] + 24) + 2)], stroke=COL['ret'], stroke_width=1)
b += f'<text class="ts" x="{T2(nose_x,0)[0]}" y="{T2(0,piv[1]+32)[1]}" text-anchor="middle">orrfutó-akna (nedves)</text>'
# méretek
yb = T2(0, P['talaj_y'])[1] + 28
b += dim_h(nose_x, fx, yb, f'tengelytáv {P["orr_tengelytav"]:.0f}', T2)
b += dim_h(0, fx, yb + 30, f'SP → főtengely {fx:.0f} (kb. 24°)', T2)
b += dim_h(-L / 2, L / 2, T2(0, 104)[1], f'tartály {L:.0f}', T2)
b += f'<text class="th" x="30" y="28">Oldalnézet: a futóművek és a tartály helye (a körvonal vázlatos)</text>'
b += f'<text class="ts" x="30" y="46">Minden hossz a súlyponttól (SP) mérve, hátra pozitív. A szaggatott narancs vonalak a behúzott/nyitott állapotot mutatják.</text>'
open(os.path.join(IMG, 'futomu_tartaly_oldal.svg'), 'w').write(svg(1240, 420, 'Futóművek és tartály oldalnézetben', b))

# ------------------------------------------------------------------ 3. alulnézet
S3 = 1.6; X3 = 470; Y3 = 250


def T3(x, z):
    return (round(X3 + x * S3, 1), round(Y3 + z * S3, 1))


b = ''
b += f'<rect x="{T3(-170,-xs)[0]}" y="{T3(0,-xs)[1]}" width="{(170+260)*S3}" height="{2*xs*S3}" fill="none" stroke="{COL["hull"]}" stroke-width="2"/>'
b += f'<line x1="{T3(-170,0)[0]}" y1="{T3(0,0)[1]}" x2="{T3(260,0)[0]}" y2="{T3(0,0)[1]}" stroke="{COL["mut"]}" stroke-dasharray="8 4"/>'
b += f'<text class="ts" x="{T3(-165,0)[0]}" y="{T3(0,0)[1]-4}">gerinc</text>'
b += f'<line x1="{T3(P["lepcso_x"],-xs)[0]}" y1="{T3(0,-xs)[1]}" x2="{T3(P["lepcso_x"],xs)[0]}" y2="{T3(0,xs)[1]}" stroke="{COL["ink"]}" stroke-width="2"/>'
b += f'<text class="t" x="{T3(P["lepcso_x"],0)[0]+4}" y="{T3(0,-xs)[1]+34}">lépcső</text>'
for zs in (-1, 1):
    z0 = 8 * zs
    zz = (z0, z0 + P['ajto_szel'] * zs)
    b += f'<rect x="{T3(-P["ajto_hossz"]/2,0)[0]}" y="{T3(0,min(zz))[1]}" width="{P["ajto_hossz"]*S3}" height="{P["ajto_szel"]*S3}" fill="#FAECE7" stroke="{COL["ret"]}" stroke-width="1.5"/>'
    mz = 12 * zs
    b += f'<rect x="{T3(mx-5,0)[0]}" y="{T3(0,mz-7.5)[1]}" width="{10*S3}" height="{15*S3}" fill="#FAEEDA" stroke="#854F0B" stroke-width="1.5"/>'
    b += f'<rect x="{T3(fx-6,0)[0]}" y="{T3(0,zs*xs-(8 if zs>0 else 0))[1]}" width="{12*S3}" height="{8*S3}" fill="#F1EFE8" stroke="#5F5E5A"/>'
b += f'<text class="t" x="{T3(0,0)[0]}" y="{T3(0,xs)[1]+22}" text-anchor="middle">2 ürítőajtó (bal és jobb rekesz), 50 × 34 mm</text>'
b += f'<text class="t" x="{T3(mx,0)[0]+30}" y="{T3(0,-xs)[1]-24}">2 merítőlap 10 × 15 mm-es ráccsal</text>'
b += f'<line x1="{T3(mx,0)[0]+28}" y1="{T3(0,-xs)[1]-28}" x2="{T3(mx,0)[0]}" y2="{T3(0,-20)[1]}" stroke="{COL["mut"]}" stroke-dasharray="3 3"/>'
b += f'<text class="t" x="{T3(fx,0)[0]+70}" y="{T3(0,xs)[1]+48}">főfutó-konzolok az oldalfalon</text>'
b += f'<line x1="{T3(fx,0)[0]+68}" y1="{T3(0,xs)[1]+44}" x2="{T3(fx,0)[0]}" y2="{T3(0,xs)[1]+4}" stroke="{COL["mut"]}" stroke-dasharray="3 3"/>'
b += dim_h(-P['ajto_hossz'] / 2, P['ajto_hossz'] / 2, T3(0, -42)[1] - 8, '50', T3)
b += f'<text class="th" x="30" y="28">Alulnézet a súlypont környékén</text>'
b += f'<text class="ts" x="30" y="46">Elöl balra. Az ajtók a V-fenék két oldalán, a gerinctől 8 mm-re; a merítőlapok közvetlenül a lépcső mögött, a gerinc két oldalán.</text>'
open(os.path.join(IMG, 'futomu_tartaly_alul.svg'), 'w').write(svg(940, 460, 'Alulnézet: ajtók és merítőlapok', b))

# ------------------------------------------------------------------ 4. tartály keresztmetszet
S4 = 2.4; X4 = 330; Y4 = 385


def T4(x, y):
    return (round(X4 + x * S4, 1), round(Y4 - y * S4, 1))


def pl4(pts, **kw):
    s = ' '.join(f'{T4(*p)[0]},{T4(*p)[1]}' for p in pts)
    st = ' '.join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items())
    return f'<polyline points="{s}" fill="none" {st}/>'


hw = P['tartaly_kulso_szel'] / 2; vd = hw * math.tan(math.radians(P['v_szog']))
b = ''
b += pl4([(0, 0), (xs, P['chine_mag']), (xs, 130)], stroke=COL['hull'], stroke_width=1.5)
b += pl4([(0, 0), (-xs, P['chine_mag']), (-xs, 130)], stroke=COL['hull'], stroke_width=1.5)
tank = [(0, 5), (hw, 5 + vd), (hw, P['tartaly_teteje_y']), (-hw, P['tartaly_teteje_y']), (-hw, 5 + vd), (0, 5)]
pts = ' '.join(f'{T4(*p)[0]},{T4(*p)[1]}' for p in tank)
b += f'<polygon points="{pts}" fill="{COL["tankf"]}" stroke="{COL["tank"]}" stroke-width="2"/>'
b += pl4([(0, 5), (0, P['tartaly_teteje_y'])], stroke=COL['tank'], stroke_width=2)
wl = 81
b += pl4([(-hw + 2, wl), (hw - 2, wl)], stroke=COL['water'], stroke_width=1, stroke_dasharray='4 3')
b += f'<text class="ts" x="{T4(hw,wl)[0]+8}" y="{T4(0,wl)[1]+4}">500 ml-es szint (kb. 81 mm)</text>'
for sgn in (-1, 1):
    p1 = (sgn * 8, 5 + 8 * math.tan(math.radians(P['v_szog'])))
    p2 = (sgn * (8 + P['ajto_szel'] * math.cos(math.radians(P['v_szog']))), p1[1] + P['ajto_szel'] * math.sin(math.radians(P['v_szog'])))
    b += pl4([p1, p2], stroke=COL['ret'], stroke_width=4)
    b += pl4([p2, (p2[0] - sgn * 6, p2[1] - 32)], stroke=COL['ret'], stroke_width=2, stroke_dasharray='3 2')
    b += f'<circle cx="{T4(*p2)[0]}" cy="{T4(*p2)[1]}" r="3.5" fill="{COL["ret"]}"/>'
b += pl4([(-hw + 15, P['tartaly_teteje_y']), (-hw + 15, P['tartaly_teteje_y'] + 25)], stroke=COL['tank'], stroke_width=2)
b += f'<text class="ts" x="{T4(-hw+15,0)[0]-6}" y="{T4(0,P["tartaly_teteje_y"]+28)[1]}" text-anchor="end">szellőző / túlfolyó</text>'
b += pl4([(hw - 20, P['tartaly_teteje_y']), (hw - 20, P['tartaly_teteje_y'] + 25)], stroke=COL['arm'], stroke_width=2)
b += f'<text class="ts" x="{T4(hw-20,0)[0]+6}" y="{T4(0,P["tartaly_teteje_y"]+28)[1]}">ajtó-tolórúd (tömített cső)</text>'
b += dim_h(-hw, hw, T4(0, P['tartaly_teteje_y'])[1] - 30, f'{P["tartaly_kulso_szel"]:.0f} (külső)', T4)
b += dim_v(T4(-xs - 12, 0)[0], 5, P['tartaly_teteje_y'], f'{P["tartaly_teteje_y"]-5:.0f}', T4, side=-1)
b += f'<text class="t" x="{T4(-hw/2,40)[0]}" y="{T4(0,40)[1]}" text-anchor="middle">bal rekesz</text>'
b += f'<text class="t" x="{T4(hw/2,40)[0]}" y="{T4(0,40)[1]}" text-anchor="middle">jobb rekesz</text>'
b += f'<text class="ts" x="{T4(0,-14)[0]}" y="{T4(0,-14)[1]}" text-anchor="middle">V-fenék 24°-os hajlással, a hajótesttel együtt; az ajtók a chine felőli élükön csuklósak</text>'
b += f'<text class="th" x="30" y="28">Tartály keresztmetszet (elölről), belső térfogat kb. 557 ml</text>'
b += f'<text class="ts" x="30" y="46">Két rekesz, 2 mm-es PETG falakkal; mindkét rekesz alján egy-egy ürítőajtó (narancs, szaggatva: nyitva).</text>'
open(os.path.join(IMG, 'tartaly_metszet.svg'), 'w').write(svg(720, 450, 'Tartály keresztmetszet', b))

# ------------------------------------------------------------------ DXF alkatrészek
def new_doc():
    d = ezdxf.new('R2010', setup=True)
    d.units = ezdxf.units.MM
    d.layers.add('KONTUR', color=7); d.layers.add('FURAT', color=1); d.layers.add('SZOVEG', color=3)
    return d, d.modelspace()


def slot_part(msp, length, width, holes):
    r = width / 2
    msp.add_line((0, -r), (length, -r), dxfattribs={'layer': 'KONTUR'})
    msp.add_line((0, r), (length, r), dxfattribs={'layer': 'KONTUR'})
    msp.add_arc((0, 0), r, 90, 270, dxfattribs={'layer': 'KONTUR'})
    msp.add_arc((length, 0), r, 270, 90, dxfattribs={'layer': 'KONTUR'})
    for (x, y, d) in holes:
        msp.add_circle((x, y), d / 2, dxfattribs={'layer': 'FURAT'})


def save(doc, msp, name, note):
    msp.add_text(note, dxfattribs={'layer': 'SZOVEG', 'height': 3}).set_placement((0, -20))
    doc.saveas(os.path.join(DXF, name))


# kar (alsó): 70 mm csuklótáv, 10 mm széles, 2 mm Al
d, m = new_doc(); slot_part(m, 70, 10, [(0, 0, 3.2), (70, 0, 3.2)])
save(d, m, 'fofuto_kar_also.dxf', 'Fofuto also kar - 2 mm aluminium - 2 db')
# felső kar fül a szervó tolórúdnak: 10 mm-re a csuklótól, 90°-ban
d, m = new_doc(); slot_part(m, 70, 10, [(0, 0, 3.2), (70, 0, 3.2)])
m.add_lwpolyline([(-5, 0), (-5, -14), (5, -14), (5, 0)], dxfattribs={'layer': 'KONTUR'})
m.add_circle((0, -10), 1.0, dxfattribs={'layer': 'FURAT'})
save(d, m, 'fofuto_kar_felso.dxf', 'Fofuto felso kar fullel (tolorud 2 mm-es Z-hajlitas, 10 mm) - 2 mm Al - 2 db')
# konzol fül: 14 × 40, csuklók 24 mm-re egymástól, 3,5 mm-re a fal síkjától; 6 mm-es beragasztó nyelv
d, m = new_doc()
m.add_lwpolyline([(-6, -8), (0, -8), (0, -14), (14, -14), (14, 38), (0, 38), (0, 32), (-6, 32), (-6, -8)], close=True, dxfattribs={'layer': 'KONTUR'})
m.add_circle((3.5, 0), 1.6, dxfattribs={'layer': 'FURAT'}); m.add_circle((3.5, 24), 1.6, dxfattribs={'layer': 'FURAT'})
save(d, m, 'fofuto_konzol_ful.dxf', 'Konzol ful - 3 mm retegelt lemez vagy 2 mm Al - oldalankent 2 db (kar ele es moge) - x=0 a kulso falsik')
# láb fúrási sablon (8×8 Al cső)
d, m = new_doc()
m.add_lwpolyline([(0, -6), (8, -6), (8, 66), (0, 66)], close=True, dxfattribs={'layer': 'KONTUR'})
for y, dd in ((0, 3.2), (36, 3.2), (60, 3.2)):
    m.add_circle((4, y), dd / 2, dxfattribs={'layer': 'FURAT'})
save(d, m, 'fofuto_lab_furatok.dxf', 'Lab: 8x8 Al zartszelveny 72 mm. y=0 tengely (oldalirany), y=36 es y=60 csuklo (elore-hatra)')
# futómű-former (a Paper-Replika F8-hoz illesztve): gerinc y=0, chine 34, oldal 171
d, m = new_doc()
hwf = P['torzs_belso_szel'] / 2
m.add_lwpolyline([(0, 0), (hwf, 33.3), (hwf, 171), (-hwf, 171), (-hwf, 33.3)], close=True, dxfattribs={'layer': 'KONTUR'})
m.add_lwpolyline([(-11.4, 89), (11.4, 89), (11.4, 101.2), (-11.4, 101.2)], close=True, dxfattribs={'layer': 'KONTUR'})
for sx in (-1, 1):
    m.add_lwpolyline([(sx * 30, 70), (sx * 66, 70), (sx * 66, 150), (sx * 30, 150)], close=True, dxfattribs={'layer': 'KONTUR'})
    m.add_lwpolyline([(sx * 77.5, 60), (sx * 72.5, 60), (sx * 72.5, 96), (sx * 77.5, 96)], dxfattribs={'layer': 'KONTUR'})
save(d, m, 'fofuto_former.dxf', 'Fofuto-former 3 mm retegelt lemez. Kozepen 9 g-os szervo kivagas (22,8x12,2). Oldalt ablak a tolorudnak; a szelen 5x36 mm-es horony a konzolfulek nyelvenek.')
# orrfutó láb (oldalnézeti lemez)
d, m = new_doc()
L0 = P['orr_lab_hossz']
m.add_lwpolyline([(-6, 6), (6, 6), (6, -L0 - 6), (-6, -L0 - 6)], close=True, dxfattribs={'layer': 'KONTUR'})
m.add_lwpolyline([(-6, 6), (-16, 6), (-16, -4), (-6, -4)], dxfattribs={'layer': 'KONTUR'})
m.add_circle((0, 0), 1.6, dxfattribs={'layer': 'FURAT'}); m.add_circle((0, -L0), 1.6, dxfattribs={'layer': 'FURAT'}); m.add_circle((-12, 1), 1.0, dxfattribs={'layer': 'FURAT'})
save(d, m, 'orrfuto_lab.dxf', 'Orrfuto lab: 3 mm Al vagy szenszalas lemez. Csuklo felul, tengely 59 mm-rel lejjebb, 2x40 mm kerek; ful a tolorudnak.')
d, m = new_doc()
m.add_lwpolyline([(0, 0), (85, 0), (85, 52), (0, 52)], close=True, dxfattribs={'layer': 'KONTUR'})
save(d, m, 'orrfuto_aknaajto.dxf', 'Orrfuto aknaajto 85x52 - 1 mm PET vagy 0,8 mm retegelt lemez - a labra ragasztva, behuzva lezarja az aknat')
# tartály lapok
d, m = new_doc()
th = P['tartaly_teteje_y']
m.add_lwpolyline([(0, 5), (hw, 5 + vd), (hw, th), (-hw, th), (-hw, 5 + vd)], close=True, dxfattribs={'layer': 'KONTUR'})
save(d, m, 'tartaly_eleje_hatulja.dxf', 'Tartaly eleje es hatulja - 2 mm PETG/PET - 2 db (y=0 a gerinc)')
d, m = new_doc()
m.add_lwpolyline([(0, 0), (L, 0), (L, th - 5 - vd), (0, th - 5 - vd)], close=True, dxfattribs={'layer': 'KONTUR'})
save(d, m, 'tartaly_oldal.dxf', 'Tartaly oldallap - 2 db')
d, m = new_doc()
m.add_lwpolyline([(0, 0), (L, 0), (L, th - 5), (0, th - 5)], close=True, dxfattribs={'layer': 'KONTUR'})
save(d, m, 'tartaly_valaszfal.dxf', 'Tartaly valaszfal (kozepen, a V csucsatol a tetoig) - 1 db')
d, m = new_doc()
m.add_lwpolyline([(0, 0), (L, 0), (L, 2 * hw), (0, 2 * hw)], close=True, dxfattribs={'layer': 'KONTUR'})
m.add_circle((L / 2, 15), 4, dxfattribs={'layer': 'FURAT'}); m.add_circle((L / 2, 2 * hw - 20), 2.5, dxfattribs={'layer': 'FURAT'})
save(d, m, 'tartaly_teto.dxf', 'Tartaly teto - szellozo (8 mm) es ajto-tolorud cso (5 mm) furat')
slope = hw / math.cos(math.radians(P['v_szog']))
d, m = new_doc()
m.add_lwpolyline([(0, 0), (L, 0), (L, slope), (0, slope)], close=True, dxfattribs={'layer': 'KONTUR'})
x0 = (L - P['ajto_hossz']) / 2
m.add_lwpolyline([(x0, 8), (x0 + P['ajto_hossz'], 8), (x0 + P['ajto_hossz'], 8 + P['ajto_szel']), (x0, 8 + P['ajto_szel'])], close=True, dxfattribs={'layer': 'KONTUR'})
save(d, m, 'tartaly_fenek.dxf', 'Tartaly fenek (V-fel) ajtonyilassal - 2 db (tukrozve). y=0 a gerinc oldal')
d, m = new_doc()
m.add_lwpolyline([(0, 0), (P['ajto_hossz'] + 2, 0), (P['ajto_hossz'] + 2, P['ajto_szel'] + 2), (0, P['ajto_szel'] + 2)], close=True, dxfattribs={'layer': 'KONTUR'})
m.add_circle(((P['ajto_hossz'] + 2) / 2, 6), 1.0, dxfattribs={'layer': 'FURAT'})
save(d, m, 'urito_ajto.dxf', 'Uritoajto 52x36 - 1 mm PET + szilikon tomites - 2 db; csuklo a chine feloli hosszu elen')
d, m = new_doc()
m.add_lwpolyline([(0, 0), (20, 0), (20, 17), (0, 17)], close=True, dxfattribs={'layer': 'KONTUR'})
for k in range(3):
    m.add_lwpolyline([(4, 3 + k * 4.5), (16, 3 + k * 4.5), (16, 5.5 + k * 4.5), (4, 5.5 + k * 4.5)], close=True, dxfattribs={'layer': 'KONTUR'})
save(d, m, 'merito_lap.dxf', 'Meritolap racsos nyilassal 20x17 - 2 db; elso elen csuklos, 25-30 fokot nyilik a vizbe')

# ------------------------------------------------------------------ paraméterlista SolidWorkshöz
lines = ['" SolidWorks globalis valtozok (Eszkozok > Egyenletek > Import). Minden ertek mm vagy fok."']
for k, v in P.items():
    lines.append(f'"{k}" = {v}')
lines += ['', '" Szamitott ertekek"', f'"fo_tengely_behuzva_x" = {ret[2][0]:.1f}', f'"fo_tengely_behuzva_y" = {ret[2][1]:.1f}',
          f'"fo_tengely_kiengedve_x" = {ext[2][0]:.1f}', f'"fo_tengely_kiengedve_y" = {ext[2][1]:.1f}',
          f'"nyomtav" = {2*ext[2][0]:.1f}', f'"kulso_oldalfal_x" = {xs}']
open(os.path.join(CAD, 'cl415_parameterek.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('kész', sorted(os.listdir(DXF)))
