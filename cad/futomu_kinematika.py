# CL-415 főfutó v2: a Dumas-féle CL-215 futómű átméretezve (k = 0.81), szervós hajtással.
# Elölnézet, a jobb oldal; x oldalirány (kifelé +), y a gerinc felett. mm, fok.
import math
_MAIN = __name__ == '__main__'
def _p(*a):
    if _MAIN: print(*a)
import numpy as np
from scipy.optimize import least_squares, brentq

K = 0.81
def S(p): return (p[0] * K, p[1] * K)

# --- az eredeti rajzból kiolvasott pontok (gerinc = 0, tengely = 0), 1:12,9
O_OT, O_OB = (80.0, 66.26), (60.0, 224.26)
O_LT = 101.96                              # alsó lengőkar (triangle) furattávolság
O_THR, O_THE = 90.70, -36.80               # lengőkar szöge behúzva / kiengedve (a rajz blokkjaiból)
O_PHR, O_PHE = 96.87, 97.60                # a láb iránya behúzva / kiengedve (a rajz blokkjaiból)
O_AX_U, O_AX_N = -33.46, 37.0              # a kerék tengelye a láb P1 pontjához képest
O_CYL = (-38.0, 96.76)                     # a henger talppontja (a túloldalon, keresztben)

# --- átméretezett és a mi törzsünkhöz igazított paraméterek
P = dict(
    k=K,
    OT=S(O_OT),                 # lengőkar csuklója
    LT=O_LT * K,                # lengőkar hossza
    TH_RET=O_THR, TH_EXT=O_THE,
    PH_RET=O_PHR, PH_EXT=O_PHE,
    LP=26.0,                    # P1-P2 távolság a lábon (eredetileg 35.9 lenne, a törzs magassága miatt rövidítve)
    AX_U=O_AX_U * K, AX_N=O_AX_N * K,
    OB=(50.5, 156.0),           # a merevítő felső csuklója (eredetileg 48.6;181.6 lenne, a törzs 171 mm magas)
    SERVO_B=S(O_CYL),           # alsó (behúzó) szervó tengelye: a henger talppontjának helyén
    R_CRANK=10.0,               # behúzó kar és lengőkar-fül sugara (párhuzamos forgattyú)
    SERVO_T=(-10.0, 150.0),     # felső (reteszelő) szervó a jobb oldalhoz; a bal tükörképe (+10)
    WHEEL_D=62.0, WHEEL_W=22.0,
    XS=82.5, CHINE=34.0, TOP=171.0, BAY_IN=44.5, WL=46.0,
)
OT, OB = np.array(P['OT']), np.array(P['OB'])
r = math.radians


def unit(a): return np.array([math.cos(r(a)), math.sin(r(a))])


def leg_pose(th, ph):
    P1 = OT + P['LT'] * unit(th)
    u = unit(ph); n = np.array([u[1], -u[0]])
    P2 = P1 + P['LP'] * u
    AX = P1 + P['AX_U'] * u + P['AX_N'] * n
    return P1, P2, AX, u, n


# merevítő hossza: kiengedve egyenes; behúzva a térd lefelé mutat (mint az eredetin, kb. -85°)
P1e, P2e, AXe, _, _ = leg_pose(P['TH_EXT'], P['PH_EXT'])
P1r, P2r, AXr, _, _ = leg_pose(P['TH_RET'], P['PH_RET'])
d_ext = np.linalg.norm(P2e - OB)
KDIR = -85.0
def _f(L4):
    Kr = OB + L4 * unit(KDIR)
    return np.linalg.norm(P2r - Kr) - (d_ext - L4)
L4 = brentq(_f, 20, d_ext - 20)
L3 = d_ext - L4
P['L4'], P['L3'] = round(L4, 2), round(L3, 2)

def knee(P2, prefer):
    d = np.linalg.norm(P2 - OB)
    a = (L4**2 - L3**2 + d**2) / (2 * d)
    h2 = L4**2 - a**2
    h = math.sqrt(max(h2, 0.0))
    e = (P2 - OB) / d; nrm = np.array([-e[1], e[0]])
    c1 = OB + a * e + h * nrm; c2 = OB + a * e - h * nrm
    return (c1 if np.linalg.norm(c1 - prefer) < np.linalg.norm(c2 - prefer) else c2), h2 >= -1e-6


def ang(v): return math.degrees(math.atan2(v[1], v[0]))


# pálya: a lengőkar és a láb szöge egyenletesen változik
N = 41
path = []
Kprev = OB + L4 * unit(KDIR)      # az eredeti térd behúzott helye, az ág kiválasztásához
for i in range(N):
    t = i / (N - 1)                       # 0 = behúzva, 1 = kiengedve
    th = P['TH_RET'] + (P['TH_EXT'] - P['TH_RET']) * t
    ph = P['PH_RET'] + (P['PH_EXT'] - P['PH_RET']) * t
    P1, P2, AX, u, n = leg_pose(th, ph)
    Kn, ok = knee(P2, Kprev); Kprev = Kn
    path.append(dict(t=t, th=th, ph=ph, P1=P1, P2=P2, AX=AX, K=Kn, ok=ok, psi=ang(Kn - OB)))


# --- alsó szervó: párhuzamos forgattyú (a szervókar szöge = lengőkar szöge + alfa)
SB = np.array(P['SERVO_B'])
beta = ang(OT - SB)                       # a keret iránya
lo, hi = min(P['TH_EXT'], P['TH_RET']), max(P['TH_EXT'], P['TH_RET'])
span = hi - lo
# a holtpontok (beta és beta+180) között középre tesszük a tartományt
center = (beta + 180 + beta) / 2 + 0
cands = []
for alpha in np.arange(-180, 180, 0.5):
    a1, a2 = lo + alpha, hi + alpha
    def dist_to_dead(x):
        return min(abs(((x - beta + 180) % 360) - 180), abs(((x - beta) % 360) - 180))
    m = min(dist_to_dead(x) for x in np.linspace(a1, a2, 50))
    cands.append((m, alpha))
mB, ALPHA = max(cands)
P['ALPHA'] = float(ALPHA); P['B_DEAD_MARGIN'] = round(mB, 1)


# --- felső (reteszelő) szervók: oldalanként egy, középen a törzs tetején, tükrözve (Y-kábel)
ST = np.array(P['SERVO_T'])
psis = np.array([p['psi'] for p in path])
psi_ret, psi_ext = psis[0], psis[-1]

def fb(a, r_i, ph, r_o, gam, C, prev):
    A = ST + r_i * unit(a + ph)
    def f(ps): return np.linalg.norm(OB + r_o * unit(ps + gam) - A) - C
    best = None
    for d in np.linspace(-30, 30, 241):
        x0 = prev + d
        if f(x0) * f(x0 + 0.25) <= 0:
            s_ = brentq(f, x0, x0 + 0.25)
            if best is None or abs(s_ - prev) < abs(best - prev): best = s_
    return best


R_I, R_O = 6.0, 12.0
res = []
pmin, pmax = psis.min(), psis.max()
import os as _os
_SYN = _os.environ.get('SYNTH') == '1'
FIX = (60.0, 132.0, 174.0)      # a keresés eredménye (SYNTH=1: teljes keresés 40..60 fok, 3 fokos rács)
for A_SPAN in ((40.0, 46.0, 52.0, 60.0) if _SYN else (FIX[0],)):
    a1, a2 = -A_SPAN / 2, A_SPAN / 2
    for ph in (np.arange(-180, 180, 3.0) if _SYN else (FIX[1],)):
        for gam in (np.arange(-180, 180, 3.0) if _SYN else (FIX[2],)):
            A1 = ST + R_I * unit(a1 + ph); A2 = ST + R_I * unit(a2 + ph)
            B1 = OB + R_O * unit(pmin + gam); B2 = OB + R_O * unit(pmax + gam)
            C1, C2 = np.linalg.norm(B1 - A1), np.linalg.norm(B2 - A2)
            if abs(C1 - C2) > 0.4 or C1 < 15: continue
            C = (C1 + C2) / 2
            prev = pmin; outs = []; trm = 180; ok = True
            for a in np.linspace(a1, a2, 31):
                ps = fb(a, R_I, ph, R_O, gam, C, prev)
                if ps is None: ok = False; break
                A = ST + R_I * unit(a + ph); B = OB + R_O * unit(ps + gam)
                tr = abs(ang(A - B) - ang(OB - B)) % 360; tr = min(tr, 360 - tr); trm = min(trm, tr, 180 - tr)
                outs.append(ps); prev = ps
            if not ok or abs(outs[-1] - pmax) > 0.8: continue
            if np.any(np.diff(outs) <= 0): continue
            # a rúd a doboz falán (x=44.5) a vízvonal felett és a térd felett menjen át
            res.append((trm, A_SPAN, ph, gam, C))
res.sort(reverse=True)
trm, A_SPAN, ph, gam, C = res[0]
P.update(TOP_RI=R_I, TOP_RO=R_O, TOP_SPAN=A_SPAN, TOP_PH=float(ph), TOP_GAM=float(gam), TOP_C=round(float(C), 2))
_p('felső mechanizmus: tr.szög min', round(trm, 1), 'szervó', A_SPAN, 'fok, fázis', ph, 'gamma', gam, 'rúd', round(C, 1))
a_grid = np.linspace(-A_SPAN / 2, A_SPAN / 2, 301); out = []; prev = pmin
for a in a_grid:
    prev = fb(a, R_I, ph, R_O, gam, C, prev); out.append(prev)
out = np.array(out)
for p in path:
    p['a_top'] = float(np.interp(p['psi'], out, a_grid))
    p['a_bot'] = p['th'] + ALPHA

# ütközés: kerék a hajótesttel
def hull_inside(x, y):
    if y < 0: return False
    if x < P['XS'] and y >= P['CHINE']: return y <= P['TOP']
    return y >= P['CHINE'] * x / P['XS'] and x < P['XS']

clash = []
for p in path:
    ax = p['AX']; hw = P['WHEEL_W'] / 2; R = P['WHEEL_D'] / 2
    for xx in np.linspace(ax[0] - hw, ax[0] + hw, 7):
        for yy in np.linspace(ax[1] - R, ax[1] + R, 13):
            if hull_inside(xx, yy): clash.append(round(p['t'], 2)); break
_p('kerék a törzsben (t értékek):', sorted(set(clash)))
_p('L4', P['L4'], 'L3', P['L3'], 'alfa', P['ALPHA'], 'holtpont-tartalék', P['B_DEAD_MARGIN'])
_p('behúzva: tengely', AXr.round(1), 'P1', P1r.round(1), 'P2', P2r.round(1))
_p('kiengedve: tengely', AXe.round(1), 'P1', P1e.round(1), 'P2', P2e.round(1), 'nyomtáv', round(2 * AXe[0]))
_p('talaj a gerinc alatt', round(-(AXe[1] - P['WHEEL_D'] / 2), 1))
_p('felső szervó:', [round(p['a_top'], 1) for p in path[::5]])
_p('psi', [round(p['psi'], 1) for p in path[::5]], 'térd ok', all(p['ok'] for p in path))

# ---------------------------------------------------------------- ütközésvizsgálat elölnézetben, z-rétegenként
def seg_dist(a, b, c, d):
    def pd(p, a, b):
        ab = b - a; L2 = np.dot(ab, ab)
        if L2 < 1e-9: return np.linalg.norm(p - a)
        t = np.clip(np.dot(p - a, ab) / L2, 0, 1); return np.linalg.norm(a + t * ab - p)
    return min(pd(a, c, d), pd(b, c, d), pd(c, a, b), pd(d, a, b))

worst = {}
for p in path:
    u = unit(p['ph']); n = np.array([u[1], -u[0]])
    leg = (p['P2'] + 4 * u, p['P1'] - 20 * u)
    tri = (OT, p['P1']); b3 = (p['K'], p['P2']); b4 = (OB, p['K'])
    sup = (p['P1'] + P['AX_U'] * u, p['AX'])           # kerékbak
    chk = {
        'láb – reteszelő tengely (OB)': seg_dist(*leg, OB, OB) - 4 - 3,
        'lengőkar – alsó merevítő (térdtengely)': seg_dist(*tri, p['K'], p['K']) - 4 - 2.5,
        'láb – térdtengely': seg_dist(*leg, p['K'], p['K']) - 4 - 2.5,
        'alsó merevítő – lengőkar tengely (OT)': seg_dist(*b3, OT, OT) - 4 - 3,
        'felső merevítő – lengőkar tengely (OT)': seg_dist(*b4, OT, OT) - 4 - 3,
        'láb – doboz fala': min(leg[0][0], leg[1][0]) - 4 - P['BAY_IN'],
        'merevítők – doboz fala': min(p['K'][0], OB[0]) - 5 - P['BAY_IN'],
        'lengőkar – doboz fala': min(OT[0], p['P1'][0]) - 5 - P['BAY_IN'],
    }
    for k, v in chk.items():
        worst[k] = min(worst.get(k, 99), v)
for k, v in worst.items(): _p(f'  {k}: {v:.1f} mm')
# az oldalfal kivágása: mely magasságokban metszi az x = 82.5 síkot valami
ys = []
for p in path:
    u = unit(p['ph'])
    for a, b in ((OT, p['P1']), (p['P2'] + 4 * u, p['P1'] - 20 * u), (p['P1'] + P['AX_U'] * u, p['AX'])):
        if (a[0] - P['XS']) * (b[0] - P['XS']) <= 0 and abs(b[0] - a[0]) > 1e-6:
            ys.append(a[1] + (P['XS'] - a[0]) * (b[1] - a[1]) / (b[0] - a[0]))
_p('oldalfal-kivágás magassága:', round(min(ys), 1), '…', round(max(ys), 1))
P['OPEN_Y'] = (round(min(ys) - 5, 1), round(max(ys) + 6, 1))

P['GROUND'] = float(path[-1]['AX'][1] - P['WHEEL_D'] / 2)
P['AXE'] = tuple(float(v) for v in path[-1]['AX']); P['AXR'] = tuple(float(v) for v in path[0]['AX'])
P['KR'] = tuple(float(v) for v in path[0]['K']); P['KE'] = tuple(float(v) for v in path[-1]['K'])
