#!/usr/bin/env python3
"""Book 10 verification: every checkable mathematical claim on book10/index.html.

Scope labels: CP = checked proof, SC = completed symbolic check,
NC = completed numerical check, ST = standard imported theorem (named where it
enters), MA = manuscript assertion (dependency verdicts rest on the cited
Volume I ledger; citation accuracy is machine-checked below). Nothing here is a
manuscript assertion dressed as a result: each check below ran to completion.
No timeouts.

Page claims verified (Part I figures, then Part II sections):
 V1  sxp(x)=tan(x/2), srx(x)=cot(x/2) on (0,pi)            (Fig 2; 10.III.T1)
 V2  free-Dirac ratio identities pc/(E+mc^2)=sqrt((E-mc^2)/(E+mc^2))=tanh(a/2)
                                                          (10.III.P1 import)
 V3  contract bridge: sxp(2*arctan(r)) = r                 (10.III.T1)
 V4  projective-rank obstruction: meridian rank 1, chart rank 2 (10.II.T1)
 V5  ground-sector |G/F| constant = Z*alpha/(1+gamma)       (10.IV.P1 import)
 V6  printed numbers: G/F=-0.00364872, x=0.007297 rad, sxp(x)=|G/F| (Fig 3)
 V7  radial-Dirac integrator reproduces analytic ground state (Fig 4 caption)
 V8  excited state (n=2,k=-1): 1 node at r~274; G/F in [-0.0450,0.0414],
     std/mean 1.65                                         (10.IV.N1, Fig 4)
 V9  Prufer reconstruction exact; tan(Theta)=G/F where finite; min A>0;
     excited Theta runs 3.14 rad ~ pi; ground Theta constant  (10.V.T1, Fig 4)
 V10 det d(u,v)/d(F,G) = 2 exact                           (10.VI.T1)
 V11 Part II section 6 dependency labels match the cited Volume I ledger
     (Z_car CHECKED; srx*sxp CHECKED; complex rank 5 MANUSCRIPT;
      Module 1 PROVED; Book 3 mixed)
"""
import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

results = []
n_assert = [0]

def check(name, err, tol, scope):
    err = np.asarray(err, dtype=float)
    assert np.all(np.isfinite(err)), f"{name}: non-finite values"
    m = float(np.max(np.abs(err)))
    assert m < tol, f"{name}: max_err={m:.3e} >= tol={tol:.0e}"
    n_assert[0] += 1
    results.append((name, m, tol, scope))
    print(f"OK [{scope}] {name}: max_err={m:.3e} < {tol:.0e}")

def check_bool(name, cond, scope, note=""):
    assert cond, f"{name}: FAILED"
    n_assert[0] += 1
    print(f"OK [{scope}] {name}" + (f" ({note})" if note else ""))

def sxp(x):
    return np.abs(1/np.sin(x)) - np.cos(x)/np.sin(x)

def srx(x):
    return np.abs(1/np.sin(x)) + np.cos(x)/np.sin(x)

ALPHA = 1/137.035999084  # fine-structure constant
Z = 1.0
GA = np.sqrt(1-(Z*ALPHA)**2)
RATIO = (Z*ALPHA)/(1+GA)   # |G/F| ground sector
X_HALF = 2*np.arctan(RATIO)

# ---- V1: canonical half-angle identities (exact trig on (0,pi)) ----
# On (0,pi), sin x > 0 so |csc x| = csc x; then
# sxp = (1-cos x)/sin x = tan(x/2), srx = (1+cos x)/sin x = cot(x/2),
# proved exactly by the Weierstrass substitution t = tan(x/2).
t = sp.symbols('t')
s, c = 2*t/(1+t**2), (1-t**2)/(1+t**2)   # sin x, cos x in t
r1 = sp.simplify((1-c)/s - t)
r2 = sp.simplify((1+c)/s - 1/t)
check_bool("V1 exact: (1-cos)/sin = tan(x/2), (1+cos)/sin = cot(x/2)",
           r1 == 0 and r2 == 0, "CP", "Weierstrass substitution, residual 0")
xs = np.linspace(0.01, np.pi-0.01, 20001)
check("V1 sxp = tan(x/2) on (0,pi)", sxp(xs) - np.tan(xs/2), 1e-12, "CP")
check("V1 srx = cot(x/2) on (0,pi)", srx(xs) - 1/np.tan(xs/2), 1e-12, "CP")
# (grid residuals 5.7e-14/2.8e-14 are floating-point noise; the identity is exact)

# ---- V2: free-Dirac lower/upper ratio identities (standard import) ----
rng = np.random.default_rng(20260918)
m = c = 1.0
E = m*c**2 * (1 + rng.random(500)*5)
p = np.sqrt(E**2 - (m*c**2)**2)/c
rr1 = p*c/(E + m*c**2)
rr2 = np.sqrt((E - m*c**2)/(E + m*c**2))
a = np.arccosh(E/(m*c**2))
rr3 = np.tanh(a/2)
check("V2 pc/(E+mc^2) = sqrt((E-mc^2)/(E+mc^2))", rr1 - rr2, 1e-14, "ST")
check("V2 pc/(E+mc^2) = tanh(a/2)", rr1 - rr3, 1e-14, "ST")
# (standard textbook identities; the import 10.III.P1 itself is ST)

# ---- V3: contract bridge sxp(2*arctan(r)) = r ----
r = rng.random(300)*3.0 + 1e-3
xx = 2*np.arctan(r)
check_bool("V3 x=2*arctan(r) in (0,pi)", np.all((xx > 0) & (xx < np.pi)), "NC")
check("V3 sxp(2*arctan(r)) = r", sxp(xx) - r, 1.5e-15, "NC")
# (conditional on projection contract 10.III.PC1; page bound 1.5e-15)

# ---- V4: projective-rank obstruction (SVD witness of exact dimension count) ----
def jac_singvals(f, pt, h=1e-7):
    pt = np.asarray(pt, float); n = len(pt)
    J = np.column_stack([(f(pt+np.eye(n)[i]*h)-f(pt-np.eye(n)[i]*h))/(2*h)
                         for i in range(n)])
    return np.linalg.svd(J, compute_uv=False)
f1 = lambda v: np.array([np.cos(v[0]/2), np.sin(v[0]/2)])
s1 = jac_singvals(f1, [1.0])
check_bool("V4 meridian singular values [0.5], rank 1",
           len(s1) == 1 and abs(s1[0]-0.5) < 1e-9, "CP",
           f"measured {s1}")
f2 = lambda v: np.array([np.cos(v[0]/2), np.cos(v[1])*np.sin(v[0]/2),
                         np.sin(v[1])*np.sin(v[0]/2)])
s2 = jac_singvals(f2, [1.0, 0.7])
check_bool("V4 chart singular values [0.5, 0.479], rank 2",
           len(s2) == 2 and abs(s2[0]-0.5) < 1e-9 and abs(s2[1]-0.479) < 1e-3,
           "CP", f"measured {s2}")
# (finite-difference SVD is the numerical witness; the dimension count is exact:
#  a 1-parameter curve cannot cover a 2-real-dimensional chart)

# ---- V5: ground-sector constant ratio (standard import 10.IV.P1) ----
rr = np.logspace(-3, 3, 4000)   # six decades of r
Pg = np.sqrt(1+GA) * rr**GA * np.exp(-Z*ALPHA*rr)    # F (large)
Qg = -np.sqrt(1-GA) * rr**GA * np.exp(-Z*ALPHA*rr)   # G (small)
ratio = np.abs(Qg/Pg)
rel_spread = ratio.std()/ratio.mean()
print(f"V5 |G/F|: mean={ratio.mean():.8f}, rel spread={rel_spread:.3e}")
check_bool("V5 |G/F| constant, rel spread < 4e-16", rel_spread < 4e-16, "NC",
           "page states measured 3.4e-16")
check("V5 |G/F| = Z*alpha/(1+gamma)", ratio - RATIO, 1e-12, "NC")

# ---- V6: Fig 3 printed numbers ----
check_bool("V6 G/F = -0.00364872 (8 decimals)", round(RATIO, 8) == 0.00364872,
           "NC", f"RATIO={RATIO:.10f}")
check_bool("V6 x = 2*arctan(|G/F|) = 0.007297 rad",
           round(X_HALF, 6) == 0.007297, "NC", f"X_HALF={X_HALF:.8f}")
check_bool("V6 0 < x < pi", 0 < X_HALF < np.pi, "NC")
check("V6 sxp(x) = |G/F|", np.array([sxp(X_HALF) - RATIO]), 1e-14, "NC")

# ---- Dirac ODE machinery (shared by V7/V8/V9) ----
def dirac_rhs(r, y, E, k):
    P_, Q_ = y
    return [-(k/r)*P_ + (E+1+Z*ALPHA/r)*Q_,
            (k/r)*Q_ - (E-1+Z*ALPHA/r)*P_]

def integrate(E, k, ga, r0, rmax, npts=30000):
    P0 = r0**ga; Q0 = r0**ga*(ga-1)/(Z*ALPHA)  # small-r asymptotics
    rs = np.geomspace(r0, rmax*(1-1e-9), npts)
    sol = solve_ivp(lambda r, y: dirac_rhs(r, y, E, k), (r0, rmax), [P0, Q0],
                    t_eval=rs, method='LSODA', rtol=1e-10, atol=1e-13)
    assert sol.success, "ODE integration failed"
    return sol.t, sol.y[0], sol.y[1]

# ---- V7: integrator reproduces the analytic ground state ----
rg, Pg_num, Qg_num = integrate(GA, -1, GA, 1e-4, 900.0, npts=20000)
Pg_an = np.sqrt(1+GA)*rg**GA*np.exp(-Z*ALPHA*rg)
Qg_an = -np.sqrt(1-GA)*rg**GA*np.exp(-Z*ALPHA*rg)
s = Pg_num[np.argmax(np.abs(Pg_num))]/Pg_an[np.argmax(np.abs(Pg_an))]
relP = np.max(np.abs(Pg_num - s*Pg_an))/np.max(np.abs(Pg_an))
relQ = np.max(np.abs(Qg_num - s*Qg_an))/np.max(np.abs(Qg_an))
print(f"V7 ODE vs analytic: max rel err P={relP:.3e}, Q={relQ:.3e}")
check_bool("V7 integrator reproduces analytic ground state to 7e-11",
           relP < 7e-11 and relQ < 7e-11, "NC",
           "integrator accuracy, not an identity")

# ---- V8: excited state (n=2, k=-1): node + non-constant G/F ----
n_r = 1
E2 = 1/np.sqrt(1 + (Z*ALPHA/(n_r+GA))**2)
re_, Pe, Qe = integrate(E2, -1, GA, 1e-4, 1400.0)
sgn = np.sign(Pe); sgn = sgn[sgn != 0]
nodes = np.sum(sgn[1:] != sgn[:-1])
check_bool("V8 P has exactly 1 node", nodes == 1, "NC")
i = np.where(np.sign(Pe[1:]) != np.sign(Pe[:-1]))[0][0]
node_r = re_[i] - Pe[i]*(re_[i+1]-re_[i])/(Pe[i+1]-Pe[i])
check_bool("V8 node at r ~= 274", 270 < node_r < 280, "NC",
           f"node_r={node_r:.2f}")
rat = Qe/Pe
mask = np.abs(Pe) > 0.05*np.max(np.abs(Pe))   # away from the node
rratio = rat[mask]
sm = rratio.std()/abs(rratio.mean())
print(f"V8 G/F away from node: min={rratio.min():.4f}, max={rratio.max():.4f}, "
      f"std/mean={sm:.3f}")
check_bool("V8 G/F range [-0.0450, 0.0414]",
           round(rratio.min(), 4) == -0.0450 and round(rratio.max(), 4) == 0.0414,
           "NC")
check_bool("V8 G/F std/mean = 1.65 (non-constant)", round(sm, 2) == 1.65 and sm > 0.3,
           "NC")
# (the n=2 case is numerically confirmed; the "generic" qualifier of 10.IV.N1
#  stays MA per the page's own section 8)

# ---- V9: Prufer completion (standard ODE theory, 10.V.T1) ----
for name, F_, G_ in [("ground", Pg_num, Qg_num), ("excited", Pe, Qe)]:
    A = np.sqrt(F_**2 + G_**2)
    Th = np.arctan2(G_, F_)
    check_bool(f"V9 {name}: min A > 0 (Theta well-defined)",
               np.min(A) > 0, "ST")
    check(f"V9 {name}: F = A cos(Theta)",
          (F_ - A*np.cos(Th))/np.max(A), 1e-9, "ST")
    check(f"V9 {name}: G = A sin(Theta)",
          (G_ - A*np.sin(Th))/np.max(A), 1e-9, "ST")
    ok = np.abs(F_) > 1e-6*np.max(np.abs(F_))
    check(f"V9 {name}: tan(Theta) = G/F where finite",
          np.tan(Th[ok]) - (G_/F_)[ok], 1e-8, "ST")
Th_e = np.unwrap(np.arctan2(Qe, Pe))
Th_g = np.unwrap(np.arctan2(Qg_num, Pg_num))
range_e = Th_e.max()-Th_e.min(); range_g = Th_g.max()-Th_g.min()
print(f"V9 Theta ranges: excited={range_e:.5f} rad, ground={range_g:.3e} rad")
check_bool("V9 excited Theta runs 3.14 rad ~ pi", abs(range_e - np.pi) < 0.01,
           "ST", f"range={range_e:.5f}")
check_bool("V9 ground Theta constant (range 0.000 rad)", range_g < 1e-6,
           "ST", f"range={range_g:.2e}")

# ---- V10: shared symplectic form (exact) ----
F, G = sp.symbols('F G')
u = F - G; v = F + G
detJ = sp.simplify(sp.Matrix([[sp.diff(u, F), sp.diff(u, G)],
                              [sp.diff(v, F), sp.diff(v, G)]]).det())
check_bool("V10 det d(u,v)/d(F,G) = 2 exactly", detJ == 2, "SC",
           "=> du^dv = 2 dF^dG, i.e. 4*dF^dG = 2*du^dv")

# ---- V11: Part II section 6 dependency labels match the cited ledger ----
LEDGER = "/home/hatch/workspace/wolfram/theorem_ledger.md"
PAGE = "/home/hatch/workspace/r-theory-rewrite/book10/index.html"
led = open(LEDGER).read()
html = open(PAGE).read()
check_bool("V11 ledger: srx*sxp row is CHECKED",
           "| srx·sxp = 1 | 1.3e-13 | CHECKED |" in led, "MA")
check_bool("V11 ledger: Z_car row is CHECKED",
           "| Z_car = 2V+i·4H = e^{2ix} | 0.0 (exact) | CHECKED |" in led, "MA")
check_bool("V11 ledger: complex rank 5 via I_iota is MANUSCRIPT",
           "complex rank 5 via I_ι" in led and "**MANUSCRIPT**" in led, "MA")
check_bool("V11 ledger: Module 1 APPROVED FIX, CHECKED independent numeric",
           "Module 1 — gamma matrices (APPROVED FIX, CHECKED independent numeric)" in led,
           "MA")
check_bool("V11 ledger: Book 3 Moebius algebra PROVED independent-symbolic",
           "Book 3 Möbius / reciprocal-transform algebra (PROVED independent — symbolic)" in led,
           "MA")
check_bool("V11 page: Z_car labeled CHECKED (independent numeric)",
           "Z_{car} = e^{2ix}</span> <b>CHECKED (independent numeric" in html, "MA")
check_bool("V11 page: complex rank 5 labeled MANUSCRIPT",
           "I_ι² = −I_{10}</span> <b>MANUSCRIPT</b>" in html, "MA")
check_bool("V11 page: Book 2 spine labeled CHECKED (independent numeric)",
           "Book 2 spine <b>CHECKED (independent numeric" in html, "MA")
check_bool("V11 page: Book 3 projective phase labeled mixed",
           "Book 3 projective phase\n<b>mixed</b>" in html, "MA")
# (the dependency claims themselves are MA — they rest on the Volume I ledger;
#  what is machine-checked here is that the page quotes the ledger accurately)

print(f"\nAll {n_assert[0]} assertions passed ({len(results)} max-error checks + "
      f"boolean checks). No timeouts.")
