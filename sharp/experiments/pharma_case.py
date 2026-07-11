"""
pharma_case.py — the reflexive trap in a branded therapeutic duopoly.

This is the SHARP benchmark re-instantiated for pharma. It is a *calibrated
illustration*, not a claim of measured elasticities: the parameters are set to
the qualitative dynamics documented in two real price wars —

  * GLP-1 (2025-26): Novo cuts Wegovy/Ozempic cash price 499->349 (+199 intro),
    then list -35/50% to $675; Lilly best-responds on LillyDirect within weeks
    (Zepbound 349->299 / 499->399->449).
  * PCSK9 (2018-19): Amgen cuts Repatha list 60% to $5,850; Regeneron/Sanofi
    match Praluent to the identical $5,850 months later.

Both fit the reflexive pattern: a price set as if the rival will hold still, then
matched once deployed. The decision surface in pharma is *net* price / formulary
access (rebate-mediated), so elasticities are of net revenue to net price, and a
policy shock (IRA / government deals) is modelled as the regime break.
"""
from __future__ import annotations
import sys, os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT); sys.path.insert(0, os.path.join(_ROOT, "experiments"))

import numpy as np
import matplotlib.pyplot as plt
import style; style.apply()
from sharp import (MarketParams, SimConfig, MarketSimulator,
                   NaiveSnapshotController, SharpController)

# --- calibration: a branded duopoly with rebate-mediated net demand ----------
# net-revenue moderately elastic (formulary position is a cliff); strong cross-
# substitution between two therapeutic rivals; competitor matches fast (low L).
PHARMA = dict(alpha=3.0, eps_own=-1.7, eps_cross=0.9, gamma=0.3,
              kappa=1.0, c0=0.0, mc=0.15,          # biologic COGS ~ low
              exp_jitter=0.30, expl_sd=0.10)
WARMUP, WINDOW, BREAK, HORIZON, SW, LAT = 40, 40, 52, 140, 40, 2

def run(seed):
    p = MarketParams(**PHARMA)
    cfg = SimConfig(horizon=HORIZON, break_week=BREAK, latency=LAT, expiry=12,
                    seed=seed, loyalty_eta=0.0)
    hn = MarketSimulator(p, cfg).run(NaiveSnapshotController(p, warmup=WARMUP, static_window=SW))
    hs = MarketSimulator(p, cfg).run(SharpController(p, warmup=WARMUP, window=WINDOW))
    return hn, hs

if __name__ == "__main__":
    # quick multi-seed summary
    U = []
    for s in range(8):
        hn, hs = run(s)
        n = hn["profit"][WARMUP:].sum(); m = hs["profit"][WARMUP:].sum()
        U.append((n, m))
    U = np.array(U)
    wins = int((U[:,1] > U[:,0]).sum())
    print(f"pharma calibration: SHARP wins {wins}/8  "
          f"mean uplift {100*(U[:,1]/U[:,0]-1).mean():+.1f}%")

    # ---- figure: representative seed, net-revenue framing ----
    SEED = 1
    hn, hs = run(SEED)
    t = np.arange(HORIZON); c = WARMUP
    cn = np.cumsum(hn["profit"]); cs = np.cumsum(hs["profit"])
    cn -= cn[c]; cs -= cs[c]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.2, 8.0), height_ratios=[1.35, 1],
                                   gridspec_kw=dict(hspace=0.44))
    ax1.axvspan(BREAK, HORIZON, color=style.OCHRE, alpha=0.06)
    ax1.plot(t[c:], cn[c:], color=style.NAIVE, lw=2.6, label="Price on the snapshot (isolated value case)")
    ax1.plot(t[c:], cs[c:], color=style.SHARP, lw=2.6,
             label="SHARP (net-price + access, re-estimated)")
    ax1.axvline(BREAK, color=style.OCHRE, lw=1.4, ls=(0, (4, 3)))
    ax1.text(BREAK+1.2, ax1.get_ylim()[1]*0.10, "rival matches +\npolicy shock (IRA / gov deals)",
             color=style.OCHRE, fontsize=10.5, fontweight="bold", va="bottom")
    ax1.annotate(f"+{100*(cs[-1]/cn[-1]-1):.0f}% cumulative net revenue",
                 xy=(HORIZON-1, cs[-1]), xytext=(HORIZON-40, cs[-1]*0.84),
                 color=style.SHARP, fontsize=11, fontweight="bold",
                 arrowprops=dict(arrowstyle="-|>", color=style.SHARP, lw=1.4))
    ax1.set_ylabel("cumulative net revenue (rebased, wk 40)"); ax1.set_xlabel("week")
    ax1.set_xlim(c, HORIZON-1); ax1.legend(loc="upper left", fontsize=10.5)
    style.titleblock(ax1, "PHARMA CASE · BRANDED DUOPOLY",
                     "A price set for isolated value, matched once it ships")

    def roll(v, w=5):
        v = np.asarray(v, float); o = np.copy(v)
        for i in range(len(v)): o[i] = v[max(0, i-w+1):i+1].mean()
        return o
    ax2.axvspan(BREAK, HORIZON, color=style.OCHRE, alpha=0.06)
    ax2.plot(t[c:], np.exp(hn["loga"][c:]), color=style.NAIVE, lw=0.8, alpha=0.22)
    ax2.plot(t[c:], np.exp(hs["loga"][c:]), color=style.SHARP, lw=0.8, alpha=0.20)
    ax2.plot(t[c:], roll(np.exp(hn["loga"]))[c:], color=style.NAIVE, lw=2.4, label="snapshot net price")
    ax2.plot(t[c:], roll(np.exp(hs["loga"]))[c:], color=style.SHARP, lw=2.4, label="SHARP net price")
    ax2.axvline(BREAK, color=style.OCHRE, lw=1.4, ls=(0, (4, 3)))
    ax2.set_ylabel("net price index"); ax2.set_xlabel("week")
    ax2.set_xlim(c, HORIZON-1); ax2.legend(loc="upper left", fontsize=10, ncol=2)
    style.titleblock(ax2, "why", "The rival's response rotates the demand curve the snapshot was optimising")

    fig.savefig(os.path.join(_ROOT, "figures", "fig6_pharma.png"), bbox_inches="tight")
    print("saved fig6_pharma.png")
