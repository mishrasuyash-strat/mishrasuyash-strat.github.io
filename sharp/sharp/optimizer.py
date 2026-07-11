"""
optimizer.py — Turn a belief about the world into a price.

Three optimizers, mirroring the Framework:

  snapshot  : maximizes profit assuming the competitor is frozen at its current price.
              This is "What does price do?" — optimizing against a static equilibrium.
  reflexive : maximizes profit assuming the competitor best-responds, i.e. solves the
              Stackelberg fixed point c = BR(a). This is "What game am I playing?"
  dro       : distributionally-robust — maximizes the worst-case profit over an
              ambiguity set of best-response gains {kappa} and cross-price scenarios.
              "Optimize under ambiguity, not false precision."
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class Economics:
    alpha: float
    eps_own: float
    eps_cross: float
    marginal_cost: float = 0.30
    log_price_grid: np.ndarray = None
    x_level: float = 0.0
    gamma: float = 0.4

    def __post_init__(self):
        if self.log_price_grid is None:
            self.log_price_grid = np.linspace(np.log(0.5), np.log(2.2), 171)

    def demand(self, loga, logc):
        return np.exp(self.alpha + self.eps_own * loga + self.eps_cross * logc
                      + self.gamma * self.x_level)

    def profit(self, loga, logc):
        p = np.exp(loga)
        q = self.demand(loga, logc)
        return (p - self.marginal_cost) * q


def optimize_snapshot(econ: Economics, logc_current: float) -> float:
    prof = econ.profit(econ.log_price_grid, logc_current)
    return float(econ.log_price_grid[np.argmax(prof)])


def optimize_reflexive(econ: Economics, br_c0: float, br_kappa: float) -> float:
    logc = br_c0 + br_kappa * econ.log_price_grid          # competitor best-responds
    prof = econ.profit(econ.log_price_grid, logc)
    return float(econ.log_price_grid[np.argmax(prof)])


def optimize_dro(econ: Economics, br_c0: float, kappa_set, cross_set) -> float:
    """Maximin over an ambiguity set of best-response gains and cross-price elasticities."""
    worst = np.full_like(econ.log_price_grid, np.inf)
    for kap in kappa_set:
        for xc in cross_set:
            e2 = Economics(econ.alpha, econ.eps_own, xc, econ.marginal_cost,
                           econ.log_price_grid, econ.x_level, econ.gamma)
            logc = br_c0 + kap * econ.log_price_grid
            worst = np.minimum(worst, e2.profit(econ.log_price_grid, logc))
    return float(econ.log_price_grid[np.argmax(worst)])
