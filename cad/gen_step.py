# CL-415: 3D alkatrészek és összeállítások STEP-ben (CadQuery)
# Koordináták: X oldalirány (jobbra +), Y fel (gerinc = 0), Z hossztengely (előre +), mm.
import math, os, sys
import cadquery as cq

OUT = sys.argv[1]
PD = os.path.join(OUT, 'cad', 'step', 'alkatreszek')
AD = os.path.join(OUT, 'cad', 'step')
os.makedirs(PD, exist_ok=True)

# ---------------------------------------------------------------- paraméterek (egyezzenek a gen_futomu_tartaly.py-val)
XS = 82.5                       # külső oldalfal
R = 70.0
FO_D, FO_W = 62.0, 22.0
ORR_D, ORR_W, ORR_L = 40.0, 15.0, 69.0
T_W, T_L, T_TOP, V = 81.0, 72.0, 124.0, 24.0
AJ_L, AJ_W = 50.0, 32.0

C = {
    'al': cq.Color(0.75, 0.77, 0.80), 'fa': cq.Color(0.80, 0.65, 0.42), 'gumi': cq.Color(0.15, 0.15, 0.15),
    'agy': cq.Color(0.85, 0.85, 0.82), 'acel': cq.Color(0.55, 0.57, 0.60), 'petg': cq.Color(0.55, 0.80, 0.85, 0.6),
    'pet': cq.Color(0.95, 0.55, 0.30),
}


def save_part(shape, name):
    cq.exporters.export(shape, os.path.join(PD, name + '.step'))
    return shape


def plate(pts, t, holes=(), cuts=()):
    """Sík lemez az XY síkban, Z irányban t vastag (z = 0..t)."""
    w = cq.Workplane('XY').polyline(pts).close().extrude(t)
    for (x, y, d) in holes:
        w = w.cut(cq.Workplane('XY').center(x, y).circle(d / 2).extrude(t))
    for c in cuts:
        w = w.cut(cq.Workplane('XY').polyline(c).close().extrude(t))
    return w


def slot_plate(L, W, t, holes):
    w = cq.Workplane('XY').center(L / 2, 0).slot2D(L + W, W).extrude(t)
    for (x, y, d) in holes:
        w = w.cut(cq.Workplane('XY').center(x, y).circle(d / 2).extrude(t))
    return w


def wheel(D, W, bore_seat, seat_depth, center_bore, fillet):
    """Kerék a Z tengely körül, z = -W/2..W/2."""
    w = cq.Workplane('XY').circle(D / 2).extrude(W).translate((0, 0, -W / 2))
    w = w.edges().fillet(fillet)
    # agy-mélyedések (könnyítés, a kerék oldalán)
    rec = W * 0.18
    for s in (1, -1):
        ring = (cq.Workplane('XY').circle(D / 2 - fillet - 3).circle(bore_seat / 2 + 3).extrude(rec)
                .translate((0, 0, s * W / 2 - (rec if s > 0 else 0))))
        w = w.cut(ring)
    w = w.cut(cq.Workplane('XY').circle(center_bore / 2).extrude(W).translate((0, 0, -W / 2)))
    for s in (1, -1):
        w = w.cut(cq.Workplane('XY').circle(bore_seat / 2).extrude(seat_depth).translate((0, 0, s * W / 2 - (seat_depth if s > 0 else 0))))
    return w


def ring(od, idd, L):
    return cq.Workplane('XY').circle(od / 2).circle(idd / 2).extrude(L).translate((0, 0, -L / 2))


fokerek = save_part(wheel(FO_D, FO_W, 8.0, 4.0, 5.5, 7.0), 'fokerek_62x22_693')
orrkerek = save_part(wheel(ORR_D, ORR_W, 6.0, 2.5, 4.5, 4.5), 'orrkerek_40x15_MR63')
cs693 = save_part(ring(8, 3, 4), 'csapagy_693_3x8x4')
csMR63 = save_part(ring(6, 3, 2.5), 'csapagy_MR63_3x6x2_5')
tav_fo = save_part(ring(5, 3.2, FO_W - 8), 'tavtarto_fokerek_5x3_2x14')
tav_orr = save_part(ring(4, 3.2, ORR_W - 5), 'tavtarto_orrkerek_4x3_2x10')
tengely_fo = save_part(cq.Workplane('XY').circle(1.5).extrude(40).translate((0, 0, -20)), 'tengely_3x40')
tengely_orr = save_part(cq.Workplane('XY').circle(1.5).extrude(44).translate((0, 0, -22)), 'tengely_3x44')


def to_x(shape):
    """Z tengelyű forgástestet X tengelyűvé fordít."""
    return shape.rotate((0, 0, 0), (0, 1, 0), 90)


# ---------------------------------------------------------------- orrfutó (kiengedve, a csukló az origóban)
orr_lab = plate([(-6, 6), (6, 6), (6, -ORR_L - 6), (-6, -ORR_L - 6)], 3,
                holes=[(0, 0, 3.2), (0, -ORR_L, 3.2)])
orr_lab = orr_lab.union(plate([(-6, 6), (-16, 6), (-16, -4), (-6, -4)], 3, holes=[(-12, 1, 2.0)]))
save_part(orr_lab, 'orrfuto_lab')
asm = cq.Assembly(name='orrfuto')
# a lemez az YZ síkban (oldalnézet), X irányban 3 mm vastag
lab_yz = orr_lab.rotate((0, 0, 0), (0, 1, 0), 90).translate((-1.5, 0, 0))
asm.add(lab_yz, name='orrfuto_lab', color=C['al'])
asm.add(to_x(tengely_orr).translate((0, -ORR_L, 0)), name='tengely', color=C['acel'])
for s, sn in ((1, 'J'), (-1, 'B')):
    cx = s * (1.5 + 1.0 + ORR_W / 2)
    asm.add(to_x(orrkerek).translate((cx, -ORR_L, 0)), name=f'orrkerek_{sn}', color=C['gumi'])
    asm.add(to_x(tav_orr).translate((cx, -ORR_L, 0)), name=f'tavtarto_{sn}', color=C['agy'])
    for k, dx in enumerate((-ORR_W / 2 + 1.25, ORR_W / 2 - 1.25)):
        asm.add(to_x(csMR63).translate((cx + dx, -ORR_L, 0)), name=f'csapagy_{sn}{k+1}', color=C['acel'])
asm.save(os.path.join(AD, 'orrfuto.step'))

# ---------------------------------------------------------------- tartály
hwt = T_W / 2
vd = hwt * math.tan(math.radians(V))
sec = [(0, 5), (hwt, 5 + vd), (hwt, T_TOP), (-hwt, T_TOP), (-hwt, 5 + vd)]
body = cq.Workplane('XY').polyline(sec).close().extrude(T_L).translate((0, 0, -T_L / 2))
body = body.faces('>Y').shell(-2)
body = body.union(cq.Workplane('XY').box(2, T_TOP - 6, T_L - 2).translate((0, (T_TOP + 6) / 2 - 1, 0)))
ca, sa = math.cos(math.radians(V)), math.sin(math.radians(V))
for s in (1, -1):
    d = 8 + AJ_W / 2  # a nyílás közepe a V csúcsától, a lejtő mentén
    cutter = (cq.Workplane('XY').box(AJ_W, 12, AJ_L)
              .rotate((0, 0, 0), (0, 0, 1), s * V)
              .translate((s * d * ca, 5 + d * sa, 0)))
    body = body.cut(cutter)
save_part(body, 'tartaly_test')
teto = (cq.Workplane('XY').box(T_W, 2, T_L).translate((0, T_TOP + 1, 0))
        .cut(cq.Workplane('XZ').center(-hwt + 15, 0).circle(4).extrude(10, both=True).translate((0, T_TOP, 0)))
        .cut(cq.Workplane('XZ').center(hwt - 20, 0).circle(2.5).extrude(10, both=True).translate((0, T_TOP, 0))))
save_part(teto, 'tartaly_teto')
ajto = save_part(cq.Workplane('XY').box(AJ_W + 2, 1, AJ_L + 2), 'urito_ajto')
merito = plate([(0, 0), (20, 0), (20, 17), (0, 17)], 1,
               cuts=[[(4, 3 + k * 4.5), (16, 3 + k * 4.5), (16, 5.5 + k * 4.5), (4, 5.5 + k * 4.5)] for k in range(3)])
save_part(merito, 'merito_lap')
asm = cq.Assembly(name='tartaly')
asm.add(body, name='tartaly_test', color=C['petg'])
asm.add(teto, name='tartaly_teto', color=C['petg'])
for s, sn in ((1, 'J'), (-1, 'B')):
    d = 8 + AJ_W / 2
    a = (ajto.rotate((0, 0, 0), (0, 0, 1), s * V)
         .translate((s * (d * ca + 0.5 * sa), 5 + d * sa - 0.5 * ca, 0)))
    asm.add(a, name=f'urito_ajto_{sn}', color=C['pet'])
asm.save(os.path.join(AD, 'tartaly.step'))

# térfogat-ellenőrzés
inner = cq.Workplane('XY').polyline(sec).close().extrude(T_L).translate((0, 0, -T_L / 2)).val().Volume() - body.val().Volume()
print('tartály belső térfogat kb.', round(inner / 1000), 'ml (fedél nélkül, a tetőig)')
print('kész:', sorted(os.listdir(AD)), len(os.listdir(PD)), 'alkatrész')
