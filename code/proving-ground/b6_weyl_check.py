"""B-6 support: independent exact check of the D8 Weyl dimensions and
Casimir eigenvalues used in PROOFS_Casimir.md K-7/K-9.

Fresh implementation (Fractions, exact rational arithmetic) of the Weyl
dimension formula for D8: positive roots e_i +/- e_j (1<=i<j<=8),
rho = (7,6,5,4,3,2,1,0).  dim V(lam) = prod_{a>0} <lam+rho,a>/<rho,a>.
Also evaluates <lam, lam+2rho> (the Casimir eigenvalue up to the kappa
normalization pinned in K-9).

Expected: dim V(w8)=128, dim V(w4)=1820, dim V(2w8)=6435;
eigenvalues 30 (pinning), 48, 64.
"""
from fractions import Fraction

rho = [7, 6, 5, 4, 3, 2, 1, 0]


def weyl_dim(lam):
    a = [lam[i] + rho[i] for i in range(8)]
    num = den = Fraction(1)
    for i in range(8):
        for j in range(i + 1, 8):
            num *= a[i] - a[j]
            den *= rho[i] - rho[j]          # e_i - e_j : j - i
            num *= a[i] + a[j]
            den *= rho[i] + rho[j]          # e_i + e_j : 16 - i - j
    assert den != 0 and num % den == 0
    return num // den


def casimir_eig(lam):
    return sum(lam[i] * (lam[i] + 2 * rho[i]) for i in range(8))


half = Fraction(1, 2)
checks = {
    "omega_8 (spinor S_+)": [half] * 8,
    "omega_4 (Lambda^4)": [1, 1, 1, 1, 0, 0, 0, 0],
    "2*omega_8": [1] * 8,
}
expected = {"omega_8 (spinor S_+)": (128, 30),
            "omega_4 (Lambda^4)": (1820, 48),
            "2*omega_8": (6435, 64)}
ok = True
for name, lam in checks.items():
    d, e = weyl_dim(lam), casimir_eig(lam)
    exp_d, exp_e = expected[name]
    status = "OK" if (d == exp_d and e == exp_e) else "MISMATCH"
    ok &= status == "OK"
    print(f"{name}: dim={d} (expect {exp_d}), <l,l+2r>={e} (expect {exp_e}) -> {status}")
print("ALL EXACT MATCH" if ok else "FAILURE")
