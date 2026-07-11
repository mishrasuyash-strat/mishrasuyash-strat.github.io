"""fig1_trap.py — the headline: naive tracks, then bleeds; SHARP re-estimates and pulls away."""
import sys, numpy as np, matplotlib.pyplot as plt
import os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT); sys.path.insert(0, os.path.join(_ROOT, "experiments"))
import style; style.apply()
from config import run_headtohead, COMPARE_FROM, BREAK_WEEK, HORIZON, effective_elasticity, ce_optimal_price, PARAMS

SEED = 3
hn, hs, naive, sth = run_headtohead(SEED)
t = np.arange(HORIZON)
c = COMPARE_FROM
cum_n = np.cumsum(hn["profit"]); cum_s = np.cumsum(hs["profit"])
# rebase cumulative at compare-start
cum_n -= cum_n[c]; cum_s -= cum_s[c]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.2, 8.2), height_ratios=[1.35, 1],
                               gridspec_kw=dict(hspace=0.42))

# ---- panel 1: cumulative profit ----
ax1.axvspan(BREAK_WEEK, HORIZON, color=style.OCHRE, alpha=0.06)
ax1.plot(t[c:], cum_n[c:], color=style.NAIVE, lw=2.6, label="Naive snapshot  (ship once, freeze)")
ax1.plot(t[c:], cum_s[c:], color=style.SHARP, lw=2.6, label="SHARP  (re-estimate, re-play)")
ax1.axvline(BREAK_WEEK, color=style.OCHRE, lw=1.4, ls=(0, (4, 3)))
ax1.text(BREAK_WEEK + 1.2, ax1.get_ylim()[1]*0.12, "competitor turns\nstrategic",
         color=style.OCHRE, fontsize=10.5, fontweight="bold", va="bottom")
gap = cum_s[-1] - cum_n[-1]
ax1.annotate(f"+{100*(cum_s[-1]/cum_n[-1]-1):.0f}% cumulative profit",
             xy=(HORIZON-1, cum_s[-1]), xytext=(HORIZON-34, cum_s[-1]*0.86),
             color=style.SHARP, fontsize=11, fontweight="bold",
             arrowprops=dict(arrowstyle="-|>", color=style.SHARP, lw=1.4))
ax1.set_ylabel("cumulative profit  (rebased at week 40)")
ax1.set_xlabel("week")
ax1.legend(loc="upper left", fontsize=10.5)
ax1.set_xlim(c, HORIZON-1)
style.titleblock(ax1, "THE REFLEXIVITY TRAP",
                 "A correct estimate, shipped into a market that answers back")

# ---- panel 2: realized price vs the two optima ----
def roll(v, w=5):
    v = np.asarray(v, float); out = np.copy(v)
    for i in range(len(v)):
        out[i] = v[max(0, i-w+1):i+1].mean()
    return out
p_static = ce_optimal_price(PARAMS["eps_own"])
p_eff = ce_optimal_price(effective_elasticity())
ax2.axvspan(BREAK_WEEK, HORIZON, color=style.OCHRE, alpha=0.06)
ax2.plot(t[c:], np.exp(hn["loga"][c:]), color=style.NAIVE, lw=0.8, alpha=0.25)
ax2.plot(t[c:], np.exp(hs["loga"][c:]), color=style.SHARP, lw=0.8, alpha=0.22)
ax2.plot(t[c:], roll(np.exp(hn["loga"]))[c:], color=style.NAIVE, lw=2.4, label="naive price (5-wk mean)")
ax2.plot(t[c:], roll(np.exp(hs["loga"]))[c:], color=style.SHARP, lw=2.4, label="SHARP price (5-wk mean)")
ax2.axhline(p_static, color=style.NAIVE, ls=":", lw=1.6)
ax2.axhline(p_eff, color=style.SHARP, ls=":", lw=1.6)
ax2.text(HORIZON-1, p_static-0.14, "static-optimal  (ε=−2.2)", color=style.NAIVE,
         fontsize=9.5, ha="right", va="top")
ax2.text(HORIZON-1, p_eff+0.06, "equilibrium-optimal  (ε_eff=−1.3)", color=style.SHARP,
         fontsize=9.5, ha="right")
ax2.axvline(BREAK_WEEK, color=style.OCHRE, lw=1.4, ls=(0, (4, 3)))
ax2.set_ylabel("price")
ax2.set_xlabel("week")
ax2.set_xlim(c, HORIZON-1)
ax2.set_ylim(0.45, 2.35)
ax2.legend(loc="upper left", fontsize=10, ncol=2)
style.titleblock(ax2, "WHY", "The naive firm keeps pricing for a demand curve that no longer exists")

fig.savefig(os.path.join(_ROOT, "figures", "fig1_trap.png"), bbox_inches="tight")
print("saved fig1_trap.png  gap=", round(gap,1), "seed", SEED)
