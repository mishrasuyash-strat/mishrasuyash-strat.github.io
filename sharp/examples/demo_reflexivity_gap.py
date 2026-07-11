"""
demo_reflexivity_gap.py — the two diagnostics, as a function of competitor aggression.

For a grid of competitor best-response gains kappa, report:
  * effective (equilibrium) elasticity      eps_eff = eps_own + eps_cross * kappa
  * the naive vs RCE-optimal price
  * the Reflexivity Gap  G  (profit lost per period by pricing on the static estimate)
  * the reflexivity spectral radius rho_R of the linear best-response instance

    python examples/demo_reflexivity_gap.py
"""
import numpy as np
from sharp import Economics

alpha, mc = 3.0, 0.35
eps_own, eps_cross = -2.2, 1.0

def ce_price(eps):                      # constant-elasticity monopoly optimum (eps < -1)
    return mc * eps / (1 + eps) if eps < -1 else np.nan

def profit(price, eps):
    return (price - mc) * np.exp(alpha) * price**eps

print(f"{'kappa':>6} {'eps_eff':>8} {'p_naive':>8} {'p_RCE':>7} {'gap/wk':>7} {'gap%':>6} {'rho_R':>6}")
for kappa in [0.0, 0.3, 0.6, 0.9, 1.2, 1.5]:
    eps_eff = eps_own + eps_cross * kappa
    p_naive = ce_price(eps_own)                       # you price on the static estimate
    p_rce = ce_price(eps_eff)                         # you should price on the induced world
    # near/above unit-elastic -> interior optimum leaves the feasible band; clip to the corner
    if not np.isfinite(p_rce) or p_rce < 0.5 or p_rce > 2.2:
        p_rce = 2.2
    gap = profit(p_rce, eps_eff) - profit(p_naive, eps_eff)
    gpct = 100 * gap / profit(p_naive, eps_eff)
    # linear-instance spectral radius, b_own=-1, b_cross=eps_cross
    rho = kappa * eps_cross / (2 * 1.0)
    print(f"{kappa:6.1f} {eps_eff:8.2f} {p_naive:8.2f} {p_rce:7.2f} {gap:7.2f} {gpct:5.0f}% {rho:6.2f}")

print("\nRead: as the competitor's response gain rises, the estimate you shipped becomes")
print("a worse and worse description of the market it created — and once rho_R crosses 1,")
print("iterating a point estimate no longer converges. That is when SHARP hedges (DRO).")
