"""
portfolio.py — Optimize a portfolio of decisions, not a single price.

A portfolio is a set of decision units (products / markets / segments) that share
regime risk. For each controller we simulate every unit, measure cumulative profit and
post-break drawdown, and score the portfolio by mean profit penalized by the CVaR of the
reflexivity drawdown. Allocation tilts a fixed "aggressiveness budget" toward units whose
risk-adjusted return survives the strategic regime.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

from .dgp import MarketParams
from .simulator import MarketSimulator, SimConfig
from .metrics import cvar


@dataclass
class DecisionUnit:
    name: str
    params: MarketParams
    cfg: SimConfig


def evaluate_unit(unit: DecisionUnit, controller_factory) -> dict:
    sim = MarketSimulator(unit.params, unit.cfg)
    ctrl = controller_factory(unit.params)
    hist = sim.run(ctrl)
    b = unit.cfg.break_week
    pre = hist["profit"][:b].sum()
    post = hist["profit"][b:].sum()
    total = hist["profit"].sum()
    baseline_post = hist["profit"][max(0, b - (len(hist["profit"]) - b)):b].mean() * (len(hist["profit"]) - b)
    drawdown = max(0.0, baseline_post - post)
    return dict(name=unit.name, total=total, pre=pre, post=post,
                drawdown=drawdown, hist=hist, ctrl=ctrl)


def evaluate_portfolio(units, controller_factory, cvar_level: float = 0.8, lam: float = 1.0):
    rows = [evaluate_unit(u, controller_factory) for u in units]
    totals = np.array([r["total"] for r in rows])
    drawdowns = np.array([r["drawdown"] for r in rows])
    port_cvar = cvar(drawdowns, cvar_level)
    score = totals.mean() - lam * port_cvar
    # risk-adjusted allocation of a unit-sum budget
    ra = totals / (drawdowns + np.median(drawdowns) + 1e-6)
    ra = np.clip(ra, 0, None)
    weights = ra / ra.sum() if ra.sum() > 0 else np.ones(len(rows)) / len(rows)
    return dict(rows=rows, total=totals.sum(), mean=totals.mean(),
                cvar_drawdown=port_cvar, score=score, weights=weights)
