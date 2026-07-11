"""
demo_portfolio.py — optimise a portfolio of decisions, not a single price.

Three products share regime risk but differ in how strategically their competitors
respond (kappa). We evaluate the whole book under the naive agent and under SHARP,
and report mean profit, the CVaR of the post-break reflexivity drawdown, and the
risk-adjusted allocation of an "aggressiveness budget".

    python examples/demo_portfolio.py
"""
import numpy as np
from sharp import (MarketParams, SimConfig, DecisionUnit,
                    evaluate_portfolio, NaiveSnapshotController, SharpController)

def unit(name, kappa, eps_cross, seed):
    p = MarketParams(alpha=3.0, eps_own=-2.2, eps_cross=eps_cross, gamma=0.3,
                     kappa=kappa, c0=0.0, mc=0.35, exp_jitter=0.34, expl_sd=0.10)
    cfg = SimConfig(horizon=140, break_week=52, latency=3, expiry=12, seed=seed, loyalty_eta=0.0)
    return DecisionUnit(name, p, cfg)

units = [unit("calm market",     kappa=0.3, eps_cross=0.6, seed=1),
         unit("contested market", kappa=0.9, eps_cross=1.0, seed=2),
         unit("knife-fight",     kappa=1.4, eps_cross=1.2, seed=3)]

naive_factory  = lambda p: NaiveSnapshotController(p, warmup=40, static_window=40)
sharp_factory = lambda p: SharpController(p, warmup=40, window=40)

for label, factory in [("NAIVE", naive_factory), ("SHARP", sharp_factory)]:
    res = evaluate_portfolio(units, factory)
    print(f"\n=== {label} portfolio ===")
    for r, w in zip(res["rows"], res["weights"]):
        print(f"  {r['name']:16s} total={r['total']:7.1f}  post-break drawdown={r['drawdown']:6.1f}  weight={w:4.0%}")
    print(f"  mean profit={res['mean']:.1f}   CVaR(drawdown)={res['cvar_drawdown']:.1f}   score={res['score']:.1f}")
