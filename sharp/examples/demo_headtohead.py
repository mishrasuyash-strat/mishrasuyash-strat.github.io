"""
demo_headtohead.py — the core result in ~20 lines.

Run the naive snapshot agent and the SHARP agent on the same reflexive market
and print how each does before and after the competitor turns strategic.

    python examples/demo_headtohead.py
"""
import numpy as np
from sharp import (MarketParams, SimConfig, MarketSimulator,
                    NaiveSnapshotController, SharpController)

p = MarketParams(alpha=3.0, eps_own=-2.2, eps_cross=1.0, gamma=0.3,
                 kappa=0.9, c0=0.0, mc=0.35, exp_jitter=0.34, expl_sd=0.10)
cfg = SimConfig(horizon=140, break_week=52, latency=3, expiry=12, seed=3, loyalty_eta=0.0)

hn = MarketSimulator(p, cfg).run(NaiveSnapshotController(p, warmup=40, static_window=40))
hs = MarketSimulator(p, cfg).run(SharpController(p, warmup=40, window=40))

def split(h):
    pre = h["profit"][40:52].sum(); post = h["profit"][52:].sum()
    return pre, post, pre + post

for name, h in [("naive snapshot", hn), ("SHARP", hs)]:
    pre, post, tot = split(h)
    print(f"{name:16s}  pre-break={pre:7.1f}   post-break={post:7.1f}   total={tot:7.1f}")

_, npost, ntot = split(hn); _, spost, stot = split(hs)
print(f"\nSHARP post-break uplift : {100*(spost/npost-1):+.1f}%")
print(f"SHARP total   uplift   : {100*(stot/ntot-1):+.1f}%")
