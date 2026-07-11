"""fig5_stability.py — the stability frontier: where a causal estimate stops being safe to ship."""
import sys, numpy as np, matplotlib.pyplot as plt
import os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT); sys.path.insert(0, os.path.join(_ROOT, "experiments"))
import style; style.apply()

# rho_R = kappa * b_cross / (2 |b_own|). Sweep competitor gain kappa and cross-sensitivity.
kappa = np.linspace(0, 3, 240)
fig, ax = plt.subplots(figsize=(9.2, 5.6))
for bc, col, lab in [(0.6, style.INDIGO_2, "weak coupling  b_cross=0.6"),
                     (1.0, style.SHARP, "b_cross=1.0"),
                     (1.4, style.NAIVE, "strong coupling  b_cross=1.4")]:
    rho = kappa * bc / (2 * 1.0)
    ax.plot(kappa, rho, color=col, lw=2.4, label=lab)

ax.axhspan(1, 3, color=style.NAIVE, alpha=0.06)
ax.axhline(1.0, color=style.INK, lw=1.4, ls=(0, (4, 3)))
ax.text(0.05, 1.03, "ρ_R = 1  ·  reflexivity frontier", fontsize=10.5, fontweight="bold", color=style.INK)
ax.text(2.95, 2.5, "SHIP-AND-HEDGE\nρ_R ≥ 1: point estimate\ndiverges — go DRO",
        fontsize=10.5, color=style.NAIVE, ha="right", va="center", fontweight="bold")
ax.text(2.95, 0.35, "SHIP-AND-RE-ESTIMATE\nρ_R < 1: contracts to RCE",
        fontsize=10.5, color=style.SHARP, ha="right", va="center", fontweight="bold")
ax.set_xlabel("competitor best-response gain  κ")
ax.set_ylabel("reflexivity spectral radius  ρ_R")
ax.set_xlim(0, 3); ax.set_ylim(0, 3)
ax.legend(loc="upper left", fontsize=10)
style.titleblock(ax, "THE DECISION RULE",
                 "One number decides whether your estimate is an asset or a liability")
fig.savefig(os.path.join(_ROOT, "figures", "fig5_stability.png"), bbox_inches="tight")
print("saved fig5_stability.png")
