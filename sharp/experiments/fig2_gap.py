"""fig2_gap.py — the Reflexivity Gap: profit in the world your own policy induces."""
import sys, numpy as np, matplotlib.pyplot as plt
import os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT); sys.path.insert(0, os.path.join(_ROOT, "experiments"))
import style; style.apply()
from config import PARAMS, effective_elasticity, ce_optimal_price

alpha, mc = PARAMS["alpha"], PARAMS["mc"]
eps_static = PARAMS["eps_own"]          # -2.2  (what you cleanly identify in the static regime)
eps_eff = effective_elasticity()        # -1.3  (the elasticity of the world you create)

a = np.linspace(0.5, 2.2, 400)
def profit(price, eps):                 # true induced world uses eps_eff
    return (price - mc) * np.exp(alpha) * price**eps
pi_true = profit(a, eps_eff)            # profit you actually earn (competitor responds)

a_naive = ce_optimal_price(eps_static)  # you optimize believing eps_static
a_star = ce_optimal_price(eps_eff)      # RCE-optimal
pi_naive = profit(a_naive, eps_eff)
pi_star = profit(a_star, eps_eff)

fig, ax = plt.subplots(figsize=(9.2, 5.6))
ax.plot(a, pi_true, color=style.INK, lw=2.6)
ax.fill_between(a, pi_true, pi_naive, where=(a>=a_naive)&(a<=a_star),
                color=style.OCHRE, alpha=0.22)
# markers
for x, y, col, lab, dx, ha in [(a_naive, pi_naive, style.NAIVE, "naive price\n(optimises ε=−2.2)", 0.05, "left"),
                               (a_star, pi_star, style.SHARP, "RCE price\n(optimises ε_eff=−1.3)", 0.03, "left")]:
    ax.scatter([x], [y], color=col, s=70, zorder=5)
    ax.plot([x, x], [pi_true.min()*0.8, y], color=col, ls=":", lw=1.3)
    ax.text(x+dx, y-0.05, lab, color=col, fontsize=10.5, fontweight="bold",
            ha=ha, va="top")
gap = pi_star - pi_naive
ax.annotate(f"Reflexivity Gap $\\mathcal{{G}}$ = {gap:.1f}/wk  ({100*gap/pi_naive:.0f}%)",
            xy=((a_naive+a_star)/2, (pi_naive+pi_star)/2),
            xytext=(1.35, pi_true.min()*0.92), color=style.OCHRE, fontsize=11.5, fontweight="bold",
            arrowprops=dict(arrowstyle="-|>", color=style.OCHRE, lw=1.4))
ax.set_xlabel("your price")
ax.set_ylabel("profit per week  (in the market your policy induces)")
ax.set_xlim(0.5, 2.2)
style.titleblock(ax, "THE REFLEXIVITY GAP",
                 "You optimise on the curve you measured; you earn on the curve you caused")
fig.savefig(os.path.join(_ROOT, "figures", "fig2_gap.png"), bbox_inches="tight")
print("saved fig2_gap.png  gap/wk=", round(gap,2), " a_naive=", round(a_naive,2), " a*=", round(a_star,2))
