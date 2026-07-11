"""fig4_regime.py — what SHARP senses: rho proxy crosses threshold, agent switches modes."""
import sys, numpy as np, matplotlib.pyplot as plt
from matplotlib.patches import Patch
import os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT); sys.path.insert(0, os.path.join(_ROOT, "experiments"))
import style; style.apply()
from config import run_headtohead, COMPARE_FROM, BREAK_WEEK, HORIZON, WARMUP

SEED = 3
hn, hs, naive, sth = run_headtohead(SEED)
t = np.arange(HORIZON)
rho = np.array([np.nan if r is None else r for r in sth.log["rho"]], dtype=float)
modes = sth.log["mode"]
alarm = np.array(sth.log["alarm"], dtype=object)

MODE_COL = {"warmup": style.MUTED, "snapshot": style.INDIGO_2,
            "reflexive": style.SHARP, "DRO": style.OCHRE}

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.4, 6.6), height_ratios=[1.5, 0.5],
                               gridspec_kw=dict(hspace=0.5), sharex=True)

# ---- panel 1: rho proxy + threshold + alarms ----
ax1.axvspan(BREAK_WEEK, HORIZON, color=style.OCHRE, alpha=0.06)
ax1.plot(t, rho, color=style.SHARP, lw=2.2)
ax1.axhline(sth.rho_thr, color=style.NAIVE, lw=1.6, ls=(0, (4, 3)))
ax1.text(WARMUP+1, sth.rho_thr+0.03, f"reflexivity threshold  ρ*={sth.rho_thr}",
         color=style.NAIVE, fontsize=10, fontweight="bold")
ax1.axvline(BREAK_WEEK, color=style.OCHRE, lw=1.4, ls=(0, (4, 3)))
ax1.text(BREAK_WEEK+1, np.nanmax(rho)*0.96, "competitor turns strategic",
         color=style.OCHRE, fontsize=10.5, fontweight="bold", va="top")
# alarm ticks
al_t = [i for i in range(HORIZON) if alarm[i] is True]
ax1.scatter(al_t, [0.02]*len(al_t), marker="|", s=120, color=style.NAIVE, alpha=0.8)
ax1.text(al_t[0] if al_t else WARMUP, 0.06, "CUSUM alarms", color=style.NAIVE, fontsize=8.6)
ax1.set_ylabel("reflexivity proxy  ρ̂(t)")
ax1.set_xlim(WARMUP, HORIZON-1); ax1.set_ylim(0, max(1.0, np.nanmax(rho)*1.1))
style.titleblock(ax1, "REGIME DETECTION AS A FIRST-CLASS CITIZEN",
                 "The agent measures its own reflexivity — and re-plans when it spikes")

# ---- panel 2: mode timeline ----
for i in range(WARMUP, HORIZON):
    ax2.axvspan(i-0.5, i+0.5, color=MODE_COL.get(modes[i], style.MUTED), alpha=0.9)
ax2.set_yticks([]); ax2.set_xlabel("week")
ax2.set_xlim(WARMUP, HORIZON-1)
ax2.set_ylabel("mode", rotation=0, ha="right", va="center")
legend = [Patch(facecolor=MODE_COL[m], label=m) for m in ["snapshot", "reflexive", "DRO"]]
ax2.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.5, -0.55),
           ncol=3, fontsize=10)

fig.savefig(os.path.join(_ROOT, "figures", "fig4_regime.png"), bbox_inches="tight")
from collections import Counter
print("saved fig4_regime.png  modes:", dict(Counter(modes[BREAK_WEEK:])))
