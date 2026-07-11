"""
metrics.py — What reflexivity costs, measured.

Reflexivity Gap (G): the profit you were promised by the world you measured, minus the
profit you got in the world you induced by acting. It is the dollar value of the Lucas
Critique operating on your own P&L.

    G(policy) = profit(policy | assumed world) - profit(policy | induced world)
"""
from __future__ import annotations
import numpy as np

from .optimizer import Economics


def reflexivity_gap(econ: Economics, policy_loga: float,
                    assumed_logc: float, induced_logc: float) -> float:
    promised = econ.profit(policy_loga, assumed_logc)
    realized = econ.profit(policy_loga, induced_logc)
    return float(promised - realized)


def cvar(losses: np.ndarray, level: float = 0.95) -> float:
    """Conditional Value at Risk (expected loss in the worst (1-level) tail)."""
    losses = np.sort(np.asarray(losses))
    k = int(np.ceil(level * len(losses)))
    tail = losses[k:]
    return float(tail.mean()) if len(tail) else float(losses[-1])


def regret(realized: np.ndarray, oracle: np.ndarray) -> np.ndarray:
    return np.asarray(oracle) - np.asarray(realized)
