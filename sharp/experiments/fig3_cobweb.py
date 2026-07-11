"""fig3_cobweb.py — the Reflexive Operator as a dynamical system: rho_R < 1 vs rho_R >= 1."""
import sys, numpy as np, matplotlib.pyplot as plt
import os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT); sys.path.insert(0, os.path.join(_ROOT, "experiments"))
import style; style.apply()
from sharp import LinearGame

fig, axes = plt.subplots(1, 2, figsize=(11.4, 5.4), gridspec_kw=dict(wspace=0.28))

def cobweb(ax, kappa, title, converges):
    g = LinearGame(kappa=kappa)
    a_lo, a_hi = 0.0, 26
    aa = np.linspace(a_lo, a_hi, 50)
    # reaction functions in (a, c) plane
    ax.plot(aa, g.reaction_rival(aa), color=style.NAIVE, lw=2.2,
            label="competitor best response  c = c₀ + κa")
    # firm BR is a = a*(c): plot as c on x -> invert; draw in same plane as c vs a
    cc = np.linspace(0, 40, 50)
    ax.plot(g.best_response_firm(cc), cc, color=style.SHARP, lw=2.2,
            label="our best response  a = a*(c)")
    # cobweb trajectory
    a, c = g.iterate(1.0, steps=11)
    xs, ys = [], []
    for i in range(len(a)):
        xs += [a[i], a[i]]; ys += [c[i-1] if i>0 else 0, c[i]]
    ax.plot(xs, ys, color=style.OCHRE, lw=1.3, alpha=0.9)
    ax.scatter(a, c, color=style.OCHRE, s=16, zorder=5)
    fp = g.fixed_point()
    if converges and fp:
        ax.scatter([fp[0]], [fp[1]], marker="*", s=260, color=style.TEAL, zorder=6,
                   edgecolor="white", linewidth=0.8)
        ax.text(fp[0], fp[1]+2.0, "RCE\n" + r"$\theta^*=\mathcal{T}(\theta^*)$", color=style.TEAL,
                fontsize=10.5, fontweight="bold", ha="center")
    ax.set_xlim(0, a_hi); ax.set_ylim(0, 40)
    ax.set_xlabel("our log-price  a"); ax.set_ylabel("competitor log-price  c")
    tag = "stable" if converges else "unstable"
    style.titleblock(ax, f"ρ_R = {g.rho_R:.2f}  ·  {tag.upper()}", title)
    ax.legend(loc="lower right", fontsize=9.2)

cobweb(axes[0], 1.2, "Re-estimation contracts to the equilibrium", True)
cobweb(axes[1], 2.4, "Re-estimation spirals out — the markdown", False)
fig.savefig(os.path.join(_ROOT, "figures", "fig3_cobweb.png"), bbox_inches="tight")
print("saved fig3_cobweb.png")
