"""
competitor.py — Model the competitor's response as a strategic variable, not noise.

We fit a structural best-response  log c = c0 + kappa * log a(-L) + psi_c * z_c
by searching latencies L and regressing on the lagged own price (after conditioning
on the competitor's own cost instrument z_c). `kappa` is the best-response gain: how
hard the environment pushes back on your move. It is the first term of the reflexivity
spectral radius.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

from .dgp import Panel


@dataclass
class BestResponse:
    c0: float
    kappa: float          # response gain d log c / d log a
    latency: int
    r2: float

    def predict_logc(self, loga: np.ndarray, z_c: np.ndarray) -> np.ndarray:
        lag = np.empty_like(loga)
        lag[: self.latency] = loga[0] if len(loga) else 0.0
        lag[self.latency:] = loga[: len(loga) - self.latency]
        return self.c0 + self.kappa * lag


def fit_best_response(panel: Panel, max_latency: int = 6) -> BestResponse:
    best = None
    for L in range(0, max_latency + 1):
        if panel.n - L < 10:
            break
        lag = panel.loga[: panel.n - L]
        logc = panel.logc[L:]
        zc = panel.z_c[L:]
        X = np.column_stack([np.ones(len(logc)), lag, zc])
        beta, *_ = np.linalg.lstsq(X, logc, rcond=None)
        pred = X @ beta
        ss_res = np.sum((logc - pred) ** 2)
        ss_tot = np.sum((logc - logc.mean()) ** 2) + 1e-12
        r2 = 1 - ss_res / ss_tot
        if best is None or r2 > best.r2:
            best = BestResponse(c0=beta[0], kappa=beta[1], latency=L, r2=r2)
    return best
