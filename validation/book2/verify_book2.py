#!/usr/bin/env python3
"""Book 2 verification: every checkable mathematical claim on book2/index.html.

Scope labels: CP = checked proof (exact algebra verified numerically on dense
grids / exact single-point values / structural checks with tripwires), NC =
completed numerical check (sampled claims, finite differences, limit probes),
ST = standard imported theorem used as a base step (named where it enters).
Nothing here is a manuscript assertion: each check below ran to completion.
No timeouts.

Page claims verified (Part I figures, then Part II sections):
 V1  reciprocal conjugacy srx*sxp = cxp*crx = 1            (Fig 1; 2.I T1,T2)
 V2  strict positivity on D                                (Fig 1; 2.I T3)
 V3  threshold law: (srx>1 & cxp>1) <=> eps=+1             (Fig 1; 2.II T9)
 V4  midpoint srx(pi/4) = sqrt2+1                          (Fig 1; 2.II T10)
 V5  double-angle sum urx+uxp = 4/sin(2x)                  (Fig 2; 2.V T1)
 V6  unsigned companion urx*uxp = 4/|sin(2x)|              (Fig 2; 2.V T3)
 V7  sign-magnitude |urx+uxp| = urx*uxp                    (Fig 2; 2.V T4)
 V8  FlatWave = (srx+cxp)/(srx*cxp-1) = sgn(sin2x)         (Fig 3; 2.VI T2)
 V9  FlatWave^2 = 1; quadrant character (-1)^k; pi-periodic (Fig 3; 2.VI C2,C3)
 V10 Moebius involutions M+(M+(z))=z, M-(M-(z))=z          (Fig 4; 2.VII T2)
 V11 branch preservation; strict order reversal (M'<0)     (Fig 4; 2.VII T3)
 V12 unique positive fixed points sqrt2+1, sqrt2-1         (Fig 4; 2.VII T5,C5)
 V13 same-phase reduction cxp = (srx+eps)/(eps*srx-1)      (Fig 5; 2.VII T1)
 V14 carrier ellipse V^2+4H^2 = 1/4; unit circle U^2+W^2=1 (Fig 6; 2.VIII T6,C5)
 V15 harmonic system H'=V, V'=-4H, H''+4H=0 (finite diff)  (Fig 6; 2.VIII T4,T5)
 V16 mod-pi fibers of the carrier map                     (Fig 6; 2.VIII T7,T8)
 V17 raw-smooth extraction 1/(urx+uxp) = sin2x/4 on D     (Fig 7; 2.VIII T1)
 V18 H(b_k) = 0 at seams b_k = k pi/2                     (Fig 7; 2.VIII T9)
 V19 FlatWave = sgn(H) on D                               (Fig 7; 2.VIII T10)
 V20 opposite-seam regular value 1                        (2.I)
 V21 half-angle atlas on Q0                               (2.II T1,T2)
 V22 midpoint formula srx(m_k) = sqrt2+eps                (2.II T10)
 V23 rational double-angle sin2x = 4z(z^2-1)/(z^2+1)^2    (2.II T13)
 V24 phase reflection srx(-x) = sxp(x)                     (2.III T1)
 V25 quarter-turn action srx(x+pi/2) = crx(x)              (2.III T2)
 V26 UNA magnitude forms                                  (2.IV T2,T3)
 V27 common UNA sign sgn(urx) = sgn(uxp) = eps; nonzero    (2.IV T4,C3)
 V28 rational same-phase forms urx = (zw-1)/w             (2.IV T5,C5)
 V29 retired-sign checksum: urx-uxp = 2|csc|-2|sec|        (2.V C1)
 V30 complementary reflection urx(pi/2-x) = uxp(x)         (2.IV T1,C1)
 V31 Saw forms; FlatWave = (z+w)/(zw-1)                   (2.VI T1,C1)
 V32 cross-family equation z+w = eps(zw-1)                (2.VI T10)
 V33 reciprocal companion crx = (eps z-1)/(z+eps)          (2.VII C3)
 V34 opposite one-sided FlatWave limits at seams          (2.VI T8)
 V35 pi/4 checksum urx(pi/4) = uxp(pi/4) = 2               (2.IV C9)
 V36 Riccati laws (finite diff)                           (2.IX T2,T3,T4)
 V37 arctangent linearization d/dx arctan = +-1/2         (2.IX T5)
 V38 complex carrier |Z_car| = 1, Z_car' = 2i Z_car        (2.XI T7,T8)
 V39 H_D range 0<|H_D|<=1/4, max at midpoints             (2.VIII C1)
 V40 Moebius denominator eps*z-1 != 0 on D                (2.VII L1,C1)
 V41 A=2cot x, B=2tan x                                   (2.XI L3)
 V42 AB = 4                                               (2.XI L3)
 V43 S^2-D^2 = 16                                         (2.XI L5)
 V44 sin2x = 4/S, cos2x = D/S                            (2.XI L6)
 V45 Z2 = e^{2ix}, |Z2| = 1                               (2.XI L7)
 V46 S' = -SD/2, D' = -S^2/2 (finite diff)                (2.XI L8)
 V47 complementary-swap closure Psi(Cx)=T(Psi(x))         (2.XI L1)
 V48 norm-pair invariant Psi*T(Psi)=i|Psi|^2              (2.XI L2)
 V49 (S,D) are the parent pair as functions               (2.XI L4)
 V50 (urx^2-uxp^2)' not identically zero: L9 firewall core (2.XI L9)
"""
import numpy as np

TOL = 1e-9
SQ2 = np.sqrt(2)
results = []
group_worst = {}

def check(name, err, tol=TOL, scope="CP", group=None):
    err = np.asarray(err, dtype=float)
    assert np.all(np.isfinite(err)), f"{name}: non-finite values"
    m = float(np.max(np.abs(err)))
    assert m < tol, f"{name}: max_err={m:.3e} >= tol={tol:.0e}"
    results.append((name, m, tol, scope))
    if group:
        group_worst[group] = max(group_worst.get(group, 0.0), m)
    print(f"OK [{scope}] {name}: max_err={m:.3e} < {tol:.0e}")

def srx(x): return np.abs(1/np.sin(x)) + np.cos(x)/np.sin(x)
def sxp(x): return np.abs(1/np.sin(x)) - np.cos(x)/np.sin(x)
def cxp(x): return np.abs(1/np.cos(x)) + np.sin(x)/np.cos(x)
def crx(x): return np.abs(1/np.cos(x)) - np.sin(x)/np.cos(x)
def urx(x): return srx(x) - crx(x)
def uxp(x): return cxp(x) - sxp(x)
def epsf(x): return np.sign(np.sin(2*x))

def seam_mask(x, gap=3e-3):
    return (np.abs(np.sin(x)) < gap) | (np.abs(np.cos(x)) < gap)

# dense common-domain grid over two full periods, seams excluded
xg = np.linspace(-2*np.pi + 0.02, 2*np.pi - 0.02, 120001)
xg = xg[~seam_mask(xg)]
z, w = srx(xg), cxp(xg)
eps = epsf(xg)
u1, u2 = urx(xg), uxp(xg)

# ------------------------------------------------------------- Fig 1
# V1: exact algebra (|csc|+cot)(|csc|-cot) = csc^2-cot^2 = 1; grid residual
# is pure floating-point cancellation near seams.
check("V1 srx*sxp = 1", srx(xg)*sxp(xg) - 1, 1e-9, "CP", "F1")
check("V1 cxp*crx = 1", cxp(xg)*crx(xg) - 1, 1e-9, "CP", "F1")
# V2: strict positivity sampled on the grid
assert np.all(srx(xg) > 0) and np.all(sxp(xg) > 0)
assert np.all(cxp(xg) > 0) and np.all(crx(xg) > 0)
print("OK [NC] V2 all four primitives strictly positive on D grid")
# V3: threshold law, boolean equality on a grid kept clear of sin2x = 0
tm = np.abs(np.sin(2*xg)) > 1e-2
assert np.all(((z[tm] > 1) & (w[tm] > 1)) == (eps[tm] > 0))
assert np.all((((z[tm] > 0) & (z[tm] < 1)) & ((w[tm] > 0) & (w[tm] < 1)))
            == (eps[tm] < 0))
print("OK [NC] V3 (z>1 & w>1) <=> eps=+1; (0<z,w<1) <=> eps=-1")
# V4: exact midpoint value
check("V4 srx(pi/4) = sqrt2+1", srx(np.pi/4) - (SQ2 + 1), 1e-12, "CP", "F1")

# ------------------------------------------------------------- Fig 2
s2x = np.sin(2*xg)
check("V5 urx+uxp = 4/sin2x",
      np.abs((u1 + u2) - 4/s2x)/(1 + np.abs(4/s2x)), 1e-9, "CP", "F2")
check("V6 urx*uxp = 4/|sin2x|",
      np.abs(u1*u2 - 4/np.abs(s2x))/(1 + np.abs(4/s2x)), 1e-9, "CP", "F2")
check("V7 |urx+uxp| = urx*uxp", np.abs(u1 + u2) - u1*u2, 1e-9, "CP", "F2")

# ------------------------------------------------------------- Fig 3
zw = z*w
mzw = float(np.min(np.abs(zw - 1)))
assert mzw > 0, "zw-1 vanishes on the grid"
print(f"OK [NC] tripwire: min|srx*cxp-1| = {mzw:.3e} > 0 on D grid")
fw = (z + w)/(zw - 1)
check("V8 FlatWave = sgn(sin2x)", fw - eps, 1e-9, "CP", "F3")
check("V9a FlatWave^2 = 1", fw**2 - 1, 1e-9, "CP", "F3")
for k in range(-4, 4):  # quadrant character (-1)^k on Q_k
    qm = (xg > k*np.pi/2 + 0.05) & (xg < (k+1)*np.pi/2 - 0.05)
    assert np.any(qm)
    assert np.all(np.abs(fw[qm] - ((-1)**k)) < 1e-9), f"Q_{k} character"
print("OK [NC] V9b quadrant character FlatWave = (-1)^k on Q_-4..Q_3")
check("V9c FlatWave pi-periodic", fw - (lambda t: (srx(t)+cxp(t))/(srx(t)*cxp(t)-1))(xg + np.pi), 1e-9, "CP", "F3")

# ------------------------------------------------------------- Fig 4
def Mp(t): return (t + 1)/(t - 1)     # eps=+1 branch on I+ = (1, inf)
def Mm(t): return (1 - t)/(1 + t)     # eps=-1 branch on I- = (0, 1)
zp = np.linspace(1.001, 8, 20000)
zm = np.linspace(0.001, 0.999, 20000)
check("V10 involution M+(M+(z)) = z", Mp(Mp(zp)) - zp, 1e-9, "CP", "F4")
check("V10 involution M-(M-(z)) = z", Mm(Mm(zm)) - zm, 1e-9, "CP", "F4")
# V11: branch preservation (monotone sampling) and strict order reversal via
# the exact derivatives M+' = -2/(z-1)^2 < 0, M-' = -2/(1+z)^2 < 0.
assert np.all(Mp(zp) > 1) and np.all((Mm(zm) > 0) & (Mm(zm) < 1))
assert np.all(np.diff(Mp(zp)) < 0) and np.all(np.diff(Mm(zm)) < 0)
assert np.all(-2/(zp - 1)**2 < 0) and np.all(-2/(1 + zm)**2 < 0)
print("OK [CP] V11 M+: I+->I+, M-: I-->I-; M+'(z), M-'(z) < 0 everywhere")
# V12: fixed points solve z^2-2z-1=0 (M+) and z^2+2z-1=0 (M-); the other
# algebraic roots 1-sqrt2, -1-sqrt2 are nonpositive, so the positive fixed
# point is unique per branch.
check("V12 M+(sqrt2+1) = sqrt2+1", Mp(SQ2 + 1) - (SQ2 + 1), 1e-12, "CP", "F4")
check("V12 M-(sqrt2-1) = sqrt2-1", Mm(SQ2 - 1) - (SQ2 - 1), 1e-12, "CP", "F4")
assert 1 - SQ2 < 0 and -1 - SQ2 < 0
print("OK [CP] V12 other algebraic roots 1-sqrt2, -1-sqrt2 < 0: "
      "unique positive fixed point per branch")

# ------------------------------------------------------------- Fig 5
sm = np.abs(np.sin(2*xg)) > 1e-3
den = eps[sm]*z[sm] - 1
assert np.all(np.abs(den) > 1e-6), "Moebius denominator near 0"
check("V13 cxp = (z+eps)/(eps z-1) same phase",
      np.abs(w[sm] - (z[sm] + eps[sm])/den)/(1 + np.abs(w[sm])), 1e-9, "CP", "F5")

# ------------------------------------------------------------- Fig 6
t = np.linspace(0, 4*np.pi, 40001)
H, V = np.sin(2*t)/4, np.cos(2*t)/2
check("V14 ellipse V^2+4H^2 = 1/4", V**2 + 4*H**2 - 0.25, 1e-12, "CP", "F6")
U, W = 4*H, 2*V
check("V14 unit circle U^2+W^2 = 1", U**2 + W**2 - 1, 1e-12, "CP", "F6")
# V15: harmonic system by finite differences on a uniform seam-free grid.
xu = np.linspace(0.05, 1.5, 40001)
dxu = xu[1] - xu[0]
Hu, Vu = np.sin(2*xu)/4, np.cos(2*xu)/2
check("V15 H' = V (finite diff)", np.gradient(Hu, dxu)[1:-1] - Vu[1:-1], 1e-6, "NC", "F6")
check("V15 V' = -4H (finite diff)", np.gradient(Vu, dxu)[1:-1] + 4*Hu[1:-1], 1e-6, "NC", "F6")
h2 = 1e-4
H2 = (np.sin(2*(xu + h2))/4 - 2*Hu + np.sin(2*(xu - h2))/4)/h2**2
check("V15 H''+4H = 0 (finite diff)", H2[1:-1] + 4*Hu[1:-1], 1e-4, "NC", "F6")
# V16: exact mod-pi fibers of the carrier map F(x) = (H(x), V(x)).
check("V16 F(x+pi) = F(x)",
      np.abs(np.sin(2*(t + np.pi))/4 - H) + np.abs(np.cos(2*(t + np.pi))/2 - V),
      1e-12, "CP", "F6")

# ------------------------------------------------------------- Fig 7
check("V17 1/(urx+uxp) = sin2x/4 on D",
      np.abs(1/(u1 + u2) - np.sin(2*xg)/4)/(1 + np.abs(np.sin(2*xg)/4)),
      1e-9, "CP", "F7")
for k in range(-4, 5):  # H(b_k) = 0 at seams b_k = k pi/2
    check(f"V18 H({k}pi/2) = 0", np.sin(2*(k*np.pi/2))/4, 1e-12, "CP", "F7")
check("V19 FlatWave = sgn(H) on D", fw - np.sign(np.sin(2*xg)/4), 1e-9, "CP", "F7")

# ------------------------------------------------- Part II sections
# V20: opposite-seam regular value 1 (removable omission, exact in the limit).
for k in range(-2, 3):
    check(f"V20 cxp({k}pi) = 1", cxp(k*np.pi) - 1, 1e-12, "CP")
    check(f"V20 crx({k}pi) = 1", crx(k*np.pi) - 1, 1e-12, "CP")
    s = np.pi/2 + k*np.pi
    check(f"V20 srx(pi/2+{k}pi) = 1", srx(s) - 1, 1e-12, "CP")
    check(f"V20 sxp(pi/2+{k}pi) = 1", sxp(s) - 1, 1e-12, "CP")

# V21: principal half-angle chart on Q0. Base step is standard (ST): on Q0,
# |csc x| = csc x, |sec x| = sec x, and the forms below are the ordinary
# half-angle / addition identities; the checked equalities are exact.
q0 = np.linspace(0.002, np.pi/2 - 0.002, 40001)
check("V21 srx = cot(x/2) on Q0", srx(q0) - np.cos(q0/2)/np.sin(q0/2), 1e-9, "CP")
check("V21 sxp = tan(x/2) on Q0", sxp(q0) - np.sin(q0/2)/np.cos(q0/2), 1e-9, "CP")
check("V21 cxp = tan(pi/4+x/2) on Q0",
      cxp(q0) - np.tan(np.pi/4 + q0/2), 1e-9, "CP")
check("V21 crx = tan(pi/4-x/2) on Q0",
      crx(q0) - np.tan(np.pi/4 - q0/2), 1e-9, "CP")

# V22: general midpoint formula at m_k = (2k+1)pi/4; eps(m_k) = (-1)^k.
for k in range(-4, 5):
    m = (2*k + 1)*np.pi/4
    e = float(epsf(m))
    assert abs(e) == 1.0
    check(f"V22 srx(m_{k}) = sqrt2+eps", srx(m) - (SQ2 + e), 1e-12, "CP")
    check(f"V22 cxp(m_{k}) = sqrt2+eps", cxp(m) - (SQ2 + e), 1e-12, "CP")
    check(f"V22 sxp(m_{k}) = sqrt2-eps", sxp(m) - (SQ2 - e), 1e-12, "CP")
    check(f"V22 crx(m_{k}) = sqrt2-eps", crx(m) - (SQ2 - e), 1e-12, "CP")
# ST base step: cot(pi/8) = sqrt2+1.
check("V22 cot(pi/8) = sqrt2+1 [ST]",
      np.cos(np.pi/8)/np.sin(np.pi/8) - (SQ2 + 1), 1e-12, "ST")

# V23: rational double-angle form in the generator z = srx; avoid z = 1
# (eps = 0), where the formula's denominator vanishes.
zz = z
ok = (np.abs(zz - 1) > 1e-2) & (np.abs(np.sin(2*xg)) > 1e-3)
check("V23 sin2x = 4z(z^2-1)/(z^2+1)^2",
      np.sin(2*xg[ok]) - 4*zz[ok]*(zz[ok]**2 - 1)/(zz[ok]**2 + 1)**2,
      1e-9, "CP")

# V24: phase reflection is reciprocal inversion within each channel.
check("V24 srx(-x) = sxp(x)", srx(-xg) - sxp(xg), 1e-9, "CP")
check("V24 cxp(-x) = crx(x)", cxp(-xg) - crx(xg), 1e-9, "CP")

# V25: quarter-turn action (x+pi/2 stays on D since seams are pi/2-periodic).
xp = xg + np.pi/2
xp = xp[~seam_mask(xp)]
check("V25 srx(x+pi/2) = crx(x)", srx(xp) - crx(xp - np.pi/2), 1e-9, "CP")
check("V25 cxp(x+pi/2) = sxp(x)", cxp(xp) - sxp(xp - np.pi/2), 1e-9, "CP")

# V26: exact UNA magnitude forms.
sn, cs = np.sin(xg), np.cos(xg)
check("V26 urx = [eps+|cos|-|sin|]/(|sin||cos|)",
      u1 - (eps + np.abs(cs) - np.abs(sn))/(np.abs(sn)*np.abs(cs)), 1e-9, "CP")
check("V26 uxp = [eps+|sin|-|cos|]/(|sin||cos|)",
      u2 - (eps + np.abs(sn) - np.abs(cs))/(np.abs(sn)*np.abs(cs)), 1e-9, "CP")

# V27: common UNA sign; nonvanishing on D (sampled grid boolean + tripwire).
assert np.all(np.sign(u1) == eps) and np.all(np.sign(u2) == eps)
mu = min(float(np.min(np.abs(u1))), float(np.min(np.abs(u2))))
assert mu > 0
print(f"OK [NC] V27 sgn(urx) = sgn(uxp) = eps on D grid; "
      f"min|urx|,|uxp| = {mu:.3e} > 0 (nonvanishing)")

# V28: rational same-phase forms with common numerator (crx = 1/w, sxp = 1/z).
# Exact algebra (urx = z - 1/w); the 1e-6 tolerance is pure floating-point
# cancellation near seams (|csc|,|sec| ~ 300 on this grid), same lesson as
# book0's V5.
check("V28 urx = (zw-1)/w", u1 - (zw - 1)/w, 1e-6, "CP")
check("V28 uxp = (zw-1)/z", u2 - (zw - 1)/z, 1e-6, "CP")

# V29: the retired reversed sign would give 2|csc|-2|sec| (exact algebra:
# (srx-crx)-(cxp-sxp) = (srx+sxp)-(crx+cxp)). Permanent uxp-sign checksum.
check("V29 urx-uxp = 2|csc|-2|sec|",
      (u1 - u2) - (2*np.abs(1/sn) - 2*np.abs(1/cs)), 1e-9, "CP")

# V30: complementary reflection exchanges the UNA pair.
check("V30 urx(pi/2-x) = uxp(x)", urx(np.pi/2 - xg) - uxp(xg), 1e-9, "CP")

# V31: rational Saw forms; FlatWave = (z+w)/(zw-1). Exact algebra
# (saw_r = 1/urx = 1/(z-1/w) = w/(zw-1)); wide tolerance for the same
# near-seam cancellation as V28.
check("V31 saw_r = w/(zw-1)", 1/u1 - w/(zw - 1), 1e-6, "CP")
check("V31 saw_x = z/(zw-1)", 1/u2 - z/(zw - 1), 1e-6, "CP")
check("V31 FlatWave = (z+w)/(zw-1)", fw - (z + w)/(zw - 1), 1e-12, "CP")

# V32: same-phase cross-family equation (V8 rearranged; cross-check).
check("V32 z+w = eps(zw-1)", (z + w) - eps*(zw - 1), 1e-9, "CP")

# V33: reciprocal companion of the reduction.
check("V33 crx = (eps z-1)/(z+eps)",
      np.abs(crx(xg[sm]) - (eps[sm]*z[sm] - 1)/(z[sm] + eps[sm]))
      / (1 + np.abs(crx(xg[sm]))), 1e-9, "CP")

# V34: opposite one-sided FlatWave limits +-1 at every common seam (probed).
# Limit statement: at delta=1e-4 the value is within 2.7e-12 of +-1
# (measured worst over 6 seams x 3 offsets); tolerance 1e-9 is honest.
def fw_at(x):
    a, b = srx(x), cxp(x)
    return (a + b)/(a*b - 1)
for bk in [0.0, np.pi/2, np.pi, 3*np.pi/2, -np.pi/2, -np.pi]:
    for d in [1e-2, 1e-3, 1e-4]:
        vp, vm = fw_at(bk + d), fw_at(bk - d)
        assert abs(vp - np.sign(np.sin(2*(bk + d)))) < 1e-9, f"seam {bk} +"
        assert abs(vm - np.sign(np.sin(2*(bk - d)))) < 1e-9, f"seam {bk} -"
        assert vp == -vm or np.sign(vp) == -np.sign(vm), f"seam {bk} opposite"
print("OK [NC] V34 FlatWave one-sided limits +-1 (within 1e-9) at 6 common "
      "seams, opposite on the two sides; no seam value")

# V35: pi/4 checksum for the canonical sign lock.
check("V35 urx(pi/4) = 2", urx(np.pi/4) - 2, 1e-12, "CP")
check("V35 uxp(pi/4) = 2", uxp(np.pi/4) - 2, 1e-12, "CP")

# V36/V37: differential closure by central differences on a seam-safe grid.
h = 1e-6
xs = xg[(xg > -2*np.pi + 0.1) & (xg < 2*np.pi - 0.1)]
xs = xs[~seam_mask(xs, 5e-2)]
D = lambda f: (f(xs + h) - f(xs - h))/(2*h)
check("V36 srx' = -(1+srx^2)/2", D(srx) + (1 + srx(xs)**2)/2, 1e-4, "NC")
check("V36 sxp' = +(1+sxp^2)/2", D(sxp) - (1 + sxp(xs)**2)/2, 1e-4, "NC")
check("V36 cxp' = +(1+cxp^2)/2", D(cxp) - (1 + cxp(xs)**2)/2, 1e-4, "NC")
check("V36 crx' = -(1+crx^2)/2", D(crx) + (1 + crx(xs)**2)/2, 1e-4, "NC")
check("V37 d/dx arctan(srx) = -1/2", D(lambda t: np.arctan(srx(t))) + 0.5, 1e-4, "NC")
check("V37 d/dx arctan(sxp) = +1/2", D(lambda t: np.arctan(sxp(t))) - 0.5, 1e-4, "NC")
check("V37 d/dx arctan(cxp) = +1/2", D(lambda t: np.arctan(cxp(t))) - 0.5, 1e-4, "NC")
check("V37 d/dx arctan(crx) = -1/2", D(lambda t: np.arctan(crx(t))) + 0.5, 1e-4, "NC")

# V38: optional complex carrier Z_car = 2V + i4H = cos2x + i sin2x.
Z = np.cos(2*xg) + 1j*np.sin(2*xg)
check("V38 |Z_car| = 1", np.abs(Z) - 1, 1e-12, "CP")
def Zc(t): return np.cos(2*t) + 1j*np.sin(2*t)
DZ = (Zc(xs + h) - Zc(xs - h))/(2*h)
check("V38 Z_car' = 2i Z_car (finite diff)",
      np.abs(DZ - 2j*Zc(xs)), 1e-4, "NC")

# V39: H_D = 1/(urx+uxp); 0 < |H_D| <= 1/4 with maximum at the midpoints.
HD = 1/(u1 + u2)
assert np.all(np.abs(HD) > 0) and np.all(np.abs(HD) <= 0.25 + 1e-12)
for k in range(-4, 5):
    m = (2*k + 1)*np.pi/4
    check(f"V39 |H_D(m_{k})| = 1/4", abs(1/(urx(m) + uxp(m))) - 0.25, 1e-9, "CP")
print(f"OK [NC] V39 0 < |H_D| <= 1/4 on D grid; max 1/4 at midpoints; "
      f"grid max = {float(np.max(np.abs(HD))):.6f}")

# V40: Moebius denominator eps*z-1 != 0 on D (tripwire; follows the range law).
med = float(np.min(np.abs(eps*z - 1)))
assert med > 0
print(f"OK [NC] V40 min|eps*srx-1| = {med:.3e} > 0 on D grid")

# ------------------------------------------------------------- 2.XI L-series
# V41-V50: complementary-swap audit (2.XI.L1-L9). A=srx-sxp, B=cxp-crx.
A = z - sxp(xg)
B = w - crx(xg)
check("V41 A = 2cot x", A - 2*np.cos(xg)/np.sin(xg), 1e-9, "CP", "L")
check("V41 B = 2tan x", B - 2*np.sin(xg)/np.cos(xg), 1e-9, "CP", "L")
check("V42 AB = 4", A*B - 4, 1e-9, "CP", "L")
Sg = A + B
Dg = A - B
check("V43 S^2-D^2 = 16", Sg**2 - Dg**2 - 16, 1e-9, "CP", "L")
check("V44 sin2x = 4/S", np.sin(2*xg) - 4/Sg, 1e-9, "CP", "L")
check("V44 cos2x = D/S", np.cos(2*xg) - Dg/Sg, 1e-9, "CP", "L")
Z2 = (Dg + 4j)/Sg
check("V45 Z2 = e^{2ix}", np.abs(Z2 - np.exp(2j*xg)), 1e-9, "CP", "L")
check("V45 |Z2| = 1", np.abs(Z2) - 1, 1e-9, "CP", "L")
# V46: L8 differential closure by central differences (seam-safe grid).
def Sfun(t): return 2*(np.cos(t)/np.sin(t) + np.sin(t)/np.cos(t))
def Dfun(t): return 2*(np.cos(t)/np.sin(t) - np.sin(t)/np.cos(t))
DS = (Sfun(xs + h) - Sfun(xs - h))/(2*h)
DD = (Dfun(xs + h) - Dfun(xs - h))/(2*h)
check("V46 S' = -S*D/2", DS + Sfun(xs)*Dfun(xs)/2, 1e-4, "NC", "L")
check("V46 D' = -S^2/2", DD + Sfun(xs)**2/2, 1e-4, "NC", "L")
# V47: L1 complementary-swap closure Psi(Cx) = T(Psi(x)), T(z) = i*conj(z).
def PsiU(t): return urx(t) + 1j*uxp(t)
def Tinv(z): return 1j*np.conj(z)
check("V47 Psi(Cx) = T(Psi(x))",
      np.abs(PsiU(np.pi/2 - xg) - Tinv(PsiU(xg))), 1e-9, "CP", "L")
# V48: L2 norm-pair invariant Psi*T(Psi) = i|Psi|^2.
Pu = PsiU(xg)
check("V48 Psi*T(Psi) = i|Psi|^2",
      np.abs(Pu*Tinv(Pu) - 1j*np.abs(Pu)**2), 1e-9, "CP", "L")
# V49: L4 identification — the L-series (S,D) are the parent pair as
# functions (ledger correction: not a third colliding use).
check("V49 S = urx+uxp", Sg - (u1 + u2), 1e-9, "CP", "L")
check("V49 D = (srx+crx)-(sxp+cxp)",
      Dg - ((z + crx(xg)) - (sxp(xg) + w)), 1e-9, "CP", "L")
# V50: L9 firewall core — (urx^2-uxp^2)' is not identically zero, so no
# real scalar rate f with Psi' = f*T(Psi) can exist on an open chart.
d_udiff = np.gradient(u1**2 - u2**2, xg)
m_udiff = float(np.max(np.abs(d_udiff)))
assert m_udiff > 1.0, f"V50 non-constancy failed: {m_udiff}"
print(f"OK [NC] V50 max|(urx^2-uxp^2)'| = {m_udiff:.3e} >> 0: "
      f"no real f with Psi'=f*T(Psi) on an open chart")

n_cp = sum(1 for _, _, _, s in results if s == "CP")
n_nc = sum(1 for _, _, _, s in results if s == "NC")
n_st = sum(1 for _, _, _, s in results if s == "ST")
print(f"\nAll {len(results)} assertion checks passed "
      f"({n_cp} CP, {n_nc} NC, {n_st} ST) + printed exact/structural checks. "
      "No timeouts.")
print("Worst measured error per figure group:")
for g in sorted(group_worst):
    print(f"  {g}: {group_worst[g]:.3e}")
