# CL-415 főfutó v2 – Bernard Dumas CL-215 futóművének átméretezése (0,81×), szervós hajtással.
# Kimenet: SVG rajzok, DXF síkalkatrészek, STEP alkatrészek és összeállítások, mozgástáblázat a vezérlőnek.
# Koordináták: x oldalirány (jobbra +), y a gerinc felett, z előre + (a futómű-állomástól), mm.
import math, os, sys
import numpy as np
import cadquery as cq
from scipy.spatial import ConvexHull

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from futomu_kinematika import P, path, leg_pose, unit, OT, OB

OUT = sys.argv[1]
IMG = os.path.join(OUT, 'docs', 'img'); DXF = os.path.join(OUT, 'cad', 'dxf')
STP = os.path.join(OUT, 'cad', 'step'); PD = os.path.join(STP, 'alkatreszek')
FW = os.path.join(OUT, 'firmware', 'cl415_futomu')
for d in (IMG, DXF, PD, FW): os.makedirs(d, exist_ok=True)

LT, LP, L3, L4 = P['LT'], P['LP'], P['L3'], P['L4']
ALPHA, RC = P['ALPHA'], P['R_CRANK']
SB, ST = np.array(P['SERVO_B']), np.array(P['SERVO_T'])
AXU, AXN = P['AX_U'], P['AX_N']
XS, CH, TOP, BAY = P['XS'], P['CHINE'], P['TOP'], P['BAY_IN']
GROUND = P['GROUND']
BAYZ = 35.0                         # az akna első/hátsó falának távolsága a futómű-állomástól
WALL_T = 3.0


def hull_pts(circles, n=36):
    pts = []
    for (x, y, r) in circles:
        for k in range(n):
            a = 2 * math.pi * k / n
            pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    pts = np.array(pts); h = ConvexHull(pts)
    return [tuple(map(float, pts[i])) for i in h.vertices]


def plate(outline, t, holes=(), cuts=(), z0=None):
    w = cq.Workplane('XY').polyline(outline).close().extrude(t)
    for (x, y, d) in holes:
        w = w.cut(cq.Workplane('XY').center(x, y).circle(d / 2).extrude(t))
    for c in cuts:
        w = w.cut(cq.Workplane('XY').polyline(c).close().extrude(t))
    return w.translate((0, 0, -t / 2 if z0 is None else z0))


def export(w, name, dxf=True):
    cq.exporters.export(w, os.path.join(PD, name + '.step'))
    if dxf:
        cq.exporters.export(w.section(), os.path.join(DXF, name + '.dxf'))
    return w


# ================================================================ alkatrészek (helyi koordinátákban)
lob = (RC * math.cos(math.radians(ALPHA)), RC * math.sin(math.radians(ALPHA)))
# 1. lengőkar (a „triangle”): 2 mm Al, oldalanként 2 lap; csukló (0,0), lábcsukló (LT,0), szervófül
lengokar = plate(hull_pts([(0, 0, 5), (LT, 0, 5)]), 2, holes=[(0, 0, 3.2), (LT, 0, 3.2), (lob[0], lob[1], 2.0)])
lengokar = lengokar.union(plate(hull_pts([(0, 0, 5), (lob[0], lob[1], 4.5)]), 2, holes=[(0, 0, 3.2), (lob[0], lob[1], 2.0)]))
lengokar = lengokar.cut(cq.Workplane('XY').center((16 + LT - 12) / 2, 0).slot2D(LT - 28, 4).extrude(4).translate((0, 0, -2)))
export(lengokar, 'fo2_lengokar')
# 2. felső merevítő (OB – térd), kar a reteszelő szervónak
lev = (P['TOP_RO'] * math.cos(math.radians(P['TOP_GAM'])), P['TOP_RO'] * math.sin(math.radians(P['TOP_GAM'])))
merev_f = plate(hull_pts([(lev[0], lev[1], 4.5), (0, 0, 5), (L4, 0, 5)]), 2, holes=[(0, 0, 3.2), (L4, 0, 3.2), (lev[0], lev[1], 2.0)])
export(merev_f, 'fo2_merevito_felso')
# 3. alsó merevítő (térd – láb P2)
merev_a = plate(hull_pts([(0, 0, 5), (L3, 0, 5)]), 2, holes=[(0, 0, 3.2), (L3, 0, 3.2)])
export(merev_a, 'fo2_merevito_also')
# 4. láb: 4 mm Al lemez a láb síkjában; helyi x = n (kifelé), y = u (a láb mentén), P1 az origóban
LAB_SCREWS = [(1.0, -20.5), (8.0, -20.5)]
lab = plate(hull_pts([(0, LP, 5), (0, 0, 5), (-5, -25, 1), (12, -25, 1), (12, -17, 1)]), 4,
            holes=[(0, 0, 3.2), (0, LP, 3.2)] + [(x, y, 3.2) for x, y in LAB_SCREWS])
export(lab, 'fo2_lab')
# 5. kerékbak: a láb aljára csavarozva, benne a kerék tengelye (n irányban); nyomtatott PA/PETG vagy Al
kb = cq.Workplane('XY').box(21, 16, 14).translate((7.5, AXU + 2.5 - 8 + 8, 0))
kb = cq.Workplane('XY').box(21, 16, 14).translate((7.5, -25.0, 0))
kb = kb.cut(cq.Workplane('XY').box(30, 9.2, 4.2).translate((7.5, -25.0 + 8 - 4.6 + 0.01, 0)))  # rés a lábnak (u > -24.6)
for x, y in LAB_SCREWS:
    kb = kb.cut(cq.Workplane('XY').center(x, y).circle(1.6).extrude(20, both=True))
kb = kb.cut(cq.Workplane('YZ').center(AXU, 0).circle(1.25).extrude(30).translate((-5, 0, 0)))  # M3 menetfurat
export(kb, 'fo2_kerekbak', dxf=False)


# 6. szervó (MG90S, egyszerűsített): a tengely az origóban, a test -x irányban? -> helyi: tengely (0,0), test x: -6 .. 16.8
def servo_model():
    body = cq.Workplane('XY').box(22.8, 12.2, 22.7).translate((5.4, 0, -22.7 / 2))
    ears = cq.Workplane('XY').box(32.2, 12.2, 2.5).translate((5.4, 0, -6.0))
    tower = cq.Workplane('XY').circle(5.9).extrude(4.0)
    shaft = cq.Workplane('XY').circle(2.4).extrude(7.0)
    return body.union(ears).union(tower).union(shaft)


szervo = servo_model()
cq.exporters.export(szervo, os.path.join(PD, 'szervo_MG90S_egyszerusitett.step'))


def horn(r):
    return cq.Workplane('XY').center(r / 2, 0).slot2D(r + 8, 6).extrude(1.5).cut(
        cq.Workplane('XY').center(r, 0).circle(0.8).extrude(1.5))


# 7. akna és dobozfalak (3 mm rétegelt lemez)
def hull_bottom(x):           # a hajótest belső fenékvonala (5 mm-es fallal), egyszerűsítve
    return CH * abs(x) / XS + 5.0


# a rudak átmenete a dobozfalon (x = BAY + 1.5): magasságtartomány
def rod_cross(p0s, p1s, x):
    ys = []
    for a, b in zip(p0s, p1s):
        if (a[0] - x) * (b[0] - x) <= 0:
            ys.append(a[1] + (x - a[0]) * (b[1] - a[1]) / (b[0] - a[0]))
    return min(ys), max(ys)


bot_a = [SB + RC * unit(p['a_bot']) for p in path]; bot_b = [OT + RC * unit(p['a_bot']) for p in path]
top_a = [ST + P['TOP_RI'] * unit(p['a_top'] + P['TOP_PH']) for p in path]
top_b = [OB + P['TOP_RO'] * unit(p['psi'] + P['TOP_GAM']) for p in path]
yb0, yb1 = rod_cross(bot_a, bot_b, BAY - 1.5)
yt0, yt1 = rod_cross(top_a, top_b, BAY - 1.5)
print('alsó rúd a falon: y', round(yb0, 1), '…', round(yb1, 1), '; felső rúd: y', round(yt0, 1), '…', round(yt1, 1))
Z_ROD = 12.0
# belső fal (yz sík): helyi x = z, y = y
yb_w = hull_bottom(BAY)
fal = plate([(-BAYZ, yb_w), (BAYZ, yb_w), (BAYZ, TOP), (-BAYZ, TOP)], WALL_T,
            cuts=[[(Z_ROD - 4, yb0 - 4), (Z_ROD + 4, yb0 - 4), (Z_ROD + 4, yb1 + 4), (Z_ROD - 4, yb1 + 4)],
                  [(Z_ROD - 4, yt0 - 4), (Z_ROD + 4, yt0 - 4), (Z_ROD + 4, min(yt1 + 4, TOP - 3)), (Z_ROD - 4, min(yt1 + 4, TOP - 3))]])
export(fal, 'fo2_akna_belso_fal')
# az akna első/hátsó fala (xy sík) a belső fal és a hajótest oldala között, a két tengely furatával
akna_fal = plate([(BAY, hull_bottom(BAY)), (XS - 5, hull_bottom(XS - 5)), (XS - 5, TOP), (BAY, TOP)], WALL_T,
                 holes=[(OT[0], OT[1], 3.2), (OB[0], OB[1], 3.2)])
export(akna_fal, 'fo2_akna_elso_hatso_fal')
# középső former (xy sík, a két belső fal között) a négy szervó kivágásával
srv_cut = []
for sx, (cx, cy), out in ((1, SB, 1), (-1, SB * [-1, 1], 1), (1, ST, -1), (-1, ST * [-1, 1], -1)):
    # alsó szervók: a test a közép felé; felső szervók: a test kifelé
    dirx = (1 if cx < 0 else -1) * out
    x0, x1 = (cx - 6.0, cx + 16.8) if dirx > 0 else (cx - 16.8, cx + 6.0)
    srv_cut.append([(x0 - 0.2, cy - 6.3), (x1 + 0.2, cy - 6.3), (x1 + 0.2, cy + 6.3), (x0 - 0.2, cy + 6.3)])
kf_out = [(-(BAY - 3), hull_bottom(BAY - 3)), (0, 5.0), (BAY - 3, hull_bottom(BAY - 3)), (BAY - 3, TOP), (-(BAY - 3), TOP)]
kozepso = plate(kf_out, WALL_T, cuts=srv_cut)
export(kozepso, 'fo2_kozepso_former')

# rudak
D_BOT = float(np.linalg.norm(OT - SB)); C_TOP = P['TOP_C']
print('alsó rúd', round(D_BOT, 1), 'felső rúd', round(C_TOP, 1))


# ================================================================ összeállítás
C = {'al': cq.Color(0.75, 0.77, 0.80), 'fa': cq.Color(0.80, 0.65, 0.42, 0.85), 'gumi': cq.Color(0.15, 0.15, 0.15),
     'acel': cq.Color(0.55, 0.57, 0.60), 'szervo': cq.Color(0.20, 0.35, 0.65), 'pa': cq.Color(0.95, 0.55, 0.20),
     'rud': cq.Color(0.85, 0.25, 0.20)}
fokerek = cq.importers.importStep(os.path.join(PD, 'fokerek_62x22_693.step'))
cs693 = cq.importers.importStep(os.path.join(PD, 'csapagy_693_3x8x4.step'))


def place2d(shape, ang_deg, pos, z, mirror):
    s = shape.rotate((0, 0, 0), (0, 0, 1), ang_deg).translate((pos[0], pos[1], z))
    return s.mirror('YZ') if mirror else s


def bolt(x, y, z0, z1, d=3.0):
    return cq.Workplane('XY').circle(d / 2).extrude(z1 - z0).translate((x, y, z0))


def rod(a, b, z, d=1.6):
    v = np.array(b) - np.array(a); L = float(np.linalg.norm(v)); ang = math.degrees(math.atan2(v[1], v[0]))
    return cq.Workplane('YZ').circle(d / 2).extrude(L).rotate((0, 0, 0), (0, 0, 1), ang).translate((a[0], a[1], z))


def gear_assy(i, name):
    p = path[i]
    asm = cq.Assembly(name=name)
    asm.add(kozepso, name='kozepso_former', color=C['fa'])
    for side, sn in ((1, 'J'), (-1, 'B')):
        mir = side < 0
        zs = 1 if side > 0 else -1          # a jobb oldali rudak elöl, a bal oldaliak hátul
        P1, P2, AX, u, n = p['P1'], p['P2'], p['AX'], unit(p['ph']), None
        th, ph, psi = p['th'], p['ph'], p['psi']
        Kn = p['K']
        # falak
        asm.add(place2d(fal.rotate((0, 0, 0), (0, 1, 0), -90), 0, (BAY - 1.5 + 0.0, 0), 0, mir), name=f'belso_fal_{sn}', color=C['fa'])
        for zz, zn in ((BAYZ, 'e'), (-BAYZ, 'h')):
            asm.add(place2d(akna_fal, 0, (0, 0), zz, mir), name=f'akna_fal_{sn}{zn}', color=C['fa'])
        # lengőkar (2 lap)
        for zz in (5.5, -5.5):
            asm.add(place2d(lengokar, th, OT, zz, mir), name=f'lengokar_{sn}{"e" if zz > 0 else "h"}', color=C['al'])
        for zz in (8.0, -8.0):
            asm.add(place2d(merev_a, math.degrees(math.atan2(*(P2 - Kn)[::-1])), Kn, zz, mir), name=f'merev_also_{sn}{"e" if zz > 0 else "h"}', color=C['al'])
        for zz in (10.5, -10.5):
            asm.add(place2d(merev_f, psi, OB, zz, mir), name=f'merev_felso_{sn}{"e" if zz > 0 else "h"}', color=C['al'])
        # láb: helyi x = n, y = u  ->  forgatás: a helyi +y tengely u irányába
        asm.add(place2d(lab, ph - 90, P1, 0, mir), name=f'lab_{sn}', color=C['al'])
        asm.add(place2d(kb, ph - 90, P1, 0, mir), name=f'kerekbak_{sn}', color=C['pa'])
        whl = fokerek.rotate((0, 0, 0), (0, 1, 0), 90).translate((AXN, AXU, 0))
        asm.add(place2d(whl, ph - 90, P1, 0, mir), name=f'fokerek_{sn}', color=C['gumi'])
        for k, dn in enumerate((AXN - 9, AXN + 9)):
            bb = cs693.rotate((0, 0, 0), (0, 1, 0), 90).translate((dn, AXU, 0))
            asm.add(place2d(bb, ph - 90, P1, 0, mir), name=f'csapagy_{sn}{k+1}', color=C['acel'])
        tg = cq.Workplane('YZ').circle(1.5).extrude(48).translate((-3, AXU, 0))
        asm.add(place2d(tg, ph - 90, P1, 0, mir), name=f'tengely_{sn}', color=C['acel'])
        # csapszegek
        for (pt, z0, z1, nm) in ((OT, -BAYZ, BAYZ, 'OT'), (OB, -BAYZ, BAYZ, 'OB'), (P1, -7, 7, 'P1'), (P2, -9.5, 9.5, 'P2'), (Kn, -12, 12, 'K')):
            asm.add(place2d(bolt(pt[0], pt[1], z0, z1), 0, (0, 0), 0, mir), name=f'csap_{nm}_{sn}', color=C['acel'])
        # szervók: jobb oldal teste hátul (z<0), a kar elöl z = +12; bal oldal fordítva (tükrözve z-ben is)
        for (sp, ang, rr, nm) in ((SB, p['a_bot'], RC, 'also'), (ST, p['a_top'] + P['TOP_PH'], P['TOP_RI'], 'felso')):
            body_dir = 1 if nm == 'also' else -1          # alsó: a test a közép felé (+x), felső: kifelé (-x)
            s = szervo.rotate((0, 0, 0), (0, 0, 1), 0 if body_dir > 0 else 180)
            s = s.translate((sp[0], sp[1], Z_ROD - 7.0 - 1.5))
            hh = horn(rr).rotate((0, 0, 0), (0, 0, 1), ang).translate((sp[0], sp[1], Z_ROD - 1.0))
            if side < 0:
                s = s.mirror('XY').mirror('YZ'); hh = hh.mirror('XY').mirror('YZ')
            asm.add(s, name=f'szervo_{nm}_{sn}', color=C['szervo'])
            asm.add(hh, name=f'szervokar_{nm}_{sn}', color=C['szervo'])
        ra, rb = SB + RC * unit(p['a_bot']), OT + RC * unit(p['a_bot'])
        ta, tb = ST + P['TOP_RI'] * unit(p['a_top'] + P['TOP_PH']), OB + P['TOP_RO'] * unit(psi + P['TOP_GAM'])
        for (a_, b_, nm) in ((ra, rb, 'also'), (ta, tb, 'felso')):
            rr_ = rod(a_, b_, Z_ROD + 0.8)
            if side < 0: rr_ = rr_.mirror('XY').mirror('YZ')
            asm.add(rr_, name=f'rud_{nm}_{sn}', color=C['rud'])
    asm.save(os.path.join(STP, name + '.step'))
    return asm


gear_assy(len(path) - 1, 'fofuto_kiengedve')
gear_assy(0, 'fofuto_behuzva')
gear_assy(len(path) // 2, 'fofuto_felut')

# ================================================================ SVG rajzok
COL = dict(ink='#1d2830', mut='#5b6a72', hull='#888780', arm='#24485e', brace='#185FA5', wheel='#2c2c2a',
           water='#378ADD', ret='#D85A30', dim='#993C1D', servo='#3C3489', rod='#A32D2D', wall='#BA7517')
FONT = "DejaVu Sans, Arial, Helvetica, sans-serif"


def svg(w, h, title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
            f'<title>{title}</title><defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0 1L9 5L0 9z" fill="{COL["dim"]}"/></marker></defs>'
            f'<style>text{{font-family:{FONT};fill:{COL["ink"]}}}.t{{font-size:13px}}.th{{font-size:15px;font-weight:bold}}.ts{{font-size:11px;fill:{COL["mut"]}}}.d{{font-size:11px;fill:{COL["dim"]}}}</style>'
            f'<rect width="{w}" height="{h}" fill="#fff"/>{body}</svg>')


class View:
    def __init__(s, cx, cy, sc): s.cx, s.cy, s.sc = cx, cy, sc
    def T(s, x, y): return (round(s.cx + x * s.sc, 1), round(s.cy - y * s.sc, 1))
    def pl(s, pts, **kw):
        st = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
        return f'<polyline points="{" ".join(f"{s.T(*p)[0]},{s.T(*p)[1]}" for p in pts)}" fill="none" {st}/>'
    def poly(s, pts, **kw):
        st = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
        return f'<polygon points="{" ".join(f"{s.T(*p)[0]},{s.T(*p)[1]}" for p in pts)}" {st}/>'
    def dot(s, p, r=2.2, c='#1d2830'):
        x, y = s.T(*p); return f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke="{c}" stroke-width="1.4"/>'
    def text(s, p, t, cls='ts', anchor='start', dx=0, dy=0, color=None):
        x, y = s.T(*p); st = f' style="fill:{color}"' if color else ''
        return f'<text class="{cls}" x="{x+dx}" y="{y+dy}" text-anchor="{anchor}"{st}>{t}</text>'


def hull_outline():
    return [(0, 0), (XS, CH), (XS, TOP), (-XS, TOP), (-XS, CH), (0, 0)]


def draw_side(V, p, side, ghost=False, servos=True):
    m = lambda q: (side * q[0], q[1])
    b = ''
    op = ' opacity="0.25"' if ghost else ''
    P1, P2, AX, Kn = p['P1'], p['P2'], p['AX'], p['K']
    u = unit(p['ph']); n = np.array([u[1], -u[0]])
    # rudak és szervók
    if servos and not ghost:
        ra, rb = SB + RC * unit(p['a_bot']), OT + RC * unit(p['a_bot'])
        ta, tb = ST + P['TOP_RI'] * unit(p['a_top'] + P['TOP_PH']), OB + P['TOP_RO'] * unit(p['psi'] + P['TOP_GAM'])
        for sp, bd in ((SB, 1), (ST, -1)):
            x0, x1 = (sp[0] - 6, sp[0] + 16.8) if (bd > 0) == (sp[0] < 0) else (sp[0] - 16.8, sp[0] + 6)
            b += V.poly([m((x0, sp[1] - 6.1)), m((x1, sp[1] - 6.1)), m((x1, sp[1] + 6.1)), m((x0, sp[1] + 6.1))], fill='#EEEDFE', stroke=COL['servo'], stroke_width=1.2)
        b += V.pl([m(SB), m(ra), m(rb), m(OT)], stroke=COL['rod'], stroke_width=1.6)
        b += V.pl([m(ST), m(ta), m(tb), m(OB)], stroke=COL['rod'], stroke_width=1.6)
        b += V.dot(m(SB), 2.4, COL['servo']) + V.dot(m(ST), 2.4, COL['servo'])
    sw = 1 if ghost else 1
    # lengőkar, merevítők, láb, kerék
    b += f'<g{op}>'
    b += V.pl([m(OT), m(P1)], stroke=COL['arm'], stroke_width=7 * V.sc / 2.2, stroke_linecap='round')
    b += V.pl([m(OB), m(Kn), m(P2)], stroke=COL['brace'], stroke_width=5 * V.sc / 2.2, stroke_linecap='round')
    lab_pts = [P2 + 5 * u, P1 + AXU * u + 2 * u, P1 + AXU * u + 12 * n]
    b += V.pl([m(q) for q in lab_pts[:2]], stroke=COL['wheel'], stroke_width=8 * V.sc / 2.2, stroke_linecap='round')
    b += V.pl([m(P1 + AXU * u), m(AX)], stroke=COL['wheel'], stroke_width=3 * V.sc / 2.2)
    hw, R = P['WHEEL_W'] / 2, P['WHEEL_D'] / 2
    corners = [AX + hw * n + R * u, AX - hw * n + R * u, AX - hw * n - R * u, AX + hw * n - R * u]
    b += V.poly([m(c) for c in corners], fill=COL['wheel'], stroke='none')
    b += '</g>'
    if not ghost:
        for q in (OT, OB, P1, P2, Kn): b += V.dot(m(q))
    return b


# --- 1. elölnézet: bal oldal kiengedve, jobb oldal behúzva
V = View(560, 520, 2.1)
b = ''
b += V.pl([(-230, GROUND), (230, GROUND)], stroke=COL['mut'], stroke_width=1)
b += V.text((120, GROUND), f'talaj (a gerinc {-GROUND:.0f} mm-rel felette)', dy=14)
b += V.pl([(-200, P['WL']), (200, P['WL'])], stroke=COL['water'], stroke_width=1, stroke_dasharray='6 4')
b += V.text((-196, P['WL']), 'vízvonal 500 ml-rel', dy=-5, color=COL['water'])
b += V.pl(hull_outline(), stroke=COL['hull'], stroke_width=2)
for s in (-1, 1):
    b += V.poly([(s * (BAY - 3), hull_bottom(BAY - 3)), (s * BAY, hull_bottom(BAY)), (s * BAY, TOP), (s * (BAY - 3), TOP)], fill='#FAEEDA', stroke=COL['wall'], stroke_width=1)
    oy0, oy1 = P['OPEN_Y']
    b += V.pl([(s * XS, oy0), (s * XS, oy1)], stroke='#fff', stroke_width=4)
    b += V.pl([(s * XS, oy0), (s * XS, oy1)], stroke=COL['hull'], stroke_width=1, stroke_dasharray='2 3')
b += draw_side(V, path[-1], -1)
b += draw_side(V, path[0], 1)
for k in (10, 20, 30):
    b += draw_side(V, path[k], 1, ghost=True)
b += V.pl([(p['AX'][0], p['AX'][1]) for p in path], stroke=COL['ret'], stroke_width=1, stroke_dasharray='4 3')
b += V.text((0, 0), 'gerinc', 'ts', 'middle', dy=14)
b += V.text((-150, 188), 'KIENGEDVE', 'th', 'middle', color=COL['arm'])
b += V.text((150, 188), 'BEHÚZVA', 'th', 'middle', color=COL['ret'])
b += V.text((0, 120), 'száraz tér', 'ts', 'middle')
b += V.text((BAY + 3, 172), 'akna', 'ts', dy=-4)
# feliratok
lab = [
    (OT, 'lengőkar csuklója', (20, -12)), (OB, 'merevítő csuklója', (60, -26)),
    (SB, 'behúzó szervó (a bal futóé)', (-60, 40)), (ST, 'reteszelő szervó', (-120, -18)),
]
for q, t, (dx, dy) in lab:
    x, y = V.T(*q)
    b += f'<line x1="{x}" y1="{y}" x2="{x+dx}" y2="{y+dy}" stroke="{COL["mut"]}" stroke-dasharray="2 2"/><text class="ts" x="{x+dx+(3 if dx>=0 else -3)}" y="{y+dy+4}" text-anchor="{"start" if dx>=0 else "end"}">{t}</text>'
# méretek
def dimh(x1, x2, y, label):
    a, c = V.T(x1, y), V.T(x2, y)
    return (f'<line x1="{a[0]}" y1="{a[1]}" x2="{c[0]}" y2="{c[1]}" stroke="{COL["dim"]}" stroke-width="0.8" marker-start="url(#a)" marker-end="url(#a)"/>'
            f'<text class="d" x="{(a[0]+c[0])/2}" y="{a[1]-4}" text-anchor="middle">{label}</text>')
b += dimh(-path[-1]['AX'][0], 0, GROUND - 14, f'félnyomtáv {path[-1]["AX"][0]:.0f} (nyomtáv {2*path[-1]["AX"][0]:.0f})')
b += f'<text class="th" x="30" y="30">Főfutó v2 elölnézetben – a Dumas-féle CL-215 futómű 0,81-szeresen, szervókkal</text>'
b += f'<text class="ts" x="30" y="48">Bal: kiengedve, a merevítő egyenesre feszítve (reteszelve). Jobb: behúzva, halványan a köztes helyzetek, szaggatva a kerék tengelyének útja.</text>'
b += f'<text class="ts" x="30" y="64">A behúzó szervók keresztben ülnek, mint az eredeti hengerek; a reteszelő szervók fent, az eredeti reteszelő henger helyén.</text>'
leg = [(COL['arm'], f'lengőkar: {LT:.1f} mm csuklótáv, 2 × 2 mm Al lap'),
       (COL['brace'], f'merevítő: felső {L4:.1f} + alsó {L3:.1f} mm, 2 × 2 mm Al lap'),
       (COL['wheel'], f'láb: 4 mm Al lemez, kerékbak, 62 mm kerék'),
       (COL['servo'], 'szervók: 2 behúzó + 2 reteszelő (MG90S)'),
       (COL['rod'], f'tolórudak: alsó {D_BOT:.1f}, felső {C_TOP:.1f} mm'),
       (COL['wall'], 'akna belső fala (3 mm rétegelt lemez)')]
for k, (c, t) in enumerate(leg):
    yy = 700 + k * 19
    b += f'<rect x="40" y="{yy-10}" width="16" height="10" fill="{c}"/><text class="t" x="64" y="{yy}">{t}</text>'
open(os.path.join(IMG, 'futomu_elol.svg'), 'w').write(svg(1120, 820, 'Főfutó v2 elölnézet', b))

# --- 2. mozgás lépésenként (jobb oldal)
W = 1320; b = ''
steps = [0, 10, 20, 30, 36, 40]
for k, i in enumerate(steps):
    V = View(50 + k * 212, 290, 0.92)
    p = path[i]
    b += V.pl([(-10, GROUND), (190, GROUND)], stroke=COL['mut'], stroke_width=0.8)
    b += V.pl([(0, 0), (XS, CH), (XS, P['OPEN_Y'][0])], stroke=COL['hull'], stroke_width=1.5)
    b += V.pl([(XS, P['OPEN_Y'][1]), (XS, TOP), (-10, TOP)], stroke=COL['hull'], stroke_width=1.5)
    b += V.poly([(BAY - 3, hull_bottom(BAY - 3)), (BAY, hull_bottom(BAY)), (BAY, TOP), (BAY - 3, TOP)], fill='#FAEEDA', stroke=COL['wall'], stroke_width=0.8)
    b += draw_side(V, p, 1)
    lab_t = ['behúzva', '25%', '50%', '75%', '90%', 'kiengedve, reteszelve'][k]
    b += V.text((90, 200), lab_t, 't', 'middle')
    b += V.text((90, GROUND), f'behúzó {p["a_bot"] - (P["TH_RET"] + P["TH_EXT"]) / 2 - ALPHA:+.0f}°, reteszelő {p["a_top"]:+.0f}°', 'ts', 'middle', dy=16)
b += f'<text class="th" x="30" y="30">A behúzás lépései (jobb oldal, elölnézet)</text>'
b += f'<text class="ts" x="30" y="48">A két szervót a futómű-vezérlő együtt mozgatja egy táblázat szerint; a merevítő a végén feszül ki egyenesre, ez reteszeli a lábat.</text>'
open(os.path.join(IMG, 'futomu_mozgas.svg'), 'w').write(svg(W, 380, 'Főfutó v2 mozgása', b))

# ================================================================ mozgástáblázat a vezérlőnek
mid_b = (P['TH_RET'] + P['TH_EXT']) / 2 + ALPHA
rows = []
for p in path:
    rows.append((p['a_bot'] - mid_b, p['a_top']))
h = ['// Automatikusan generált: cad/gen_futomu_v2.py – ne kézzel módosítsd.',
     '// A főfutó szervóinak szöge (fok, a szervó középállásához képest) a behúzott (0) és',
     '// a kiengedett (utolsó) állapot között, egyenlő lépésekben.', '#pragma once',
     f'const int MOZGAS_PONTOK = {len(rows)};',
     'const float BEHUZO_SZOG[MOZGAS_PONTOK] = {' + ', '.join(f'{a:.2f}f' for a, _ in rows) + '};',
     'const float RETESZ_SZOG[MOZGAS_PONTOK] = {' + ', '.join(f'{c:.2f}f' for _, c in rows) + '};']
open(os.path.join(FW, 'mozgas_tabla.h'), 'w').write('\n'.join(h) + '\n')
print('behúzó szervó tartomány', round(rows[0][0], 1), '…', round(rows[-1][0], 1), '; reteszelő', rows[0][1], '…', rows[-1][1])
print('kész')
