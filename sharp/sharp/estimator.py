"""
estimator.py — Causal estimators for the response function.

Three estimators, in increasing order of honesty:

1. naive_ols        : ignores endogeneity. Biased by the demand-shock confounder.
2. iv_single        : instruments OUR price only (z_a). Clean in a static market;
                      silently biased once the competitor best-responds, because z_a
                      then affects demand through the competitor -> exclusion breaks.
                      This is the "half the identification problem" estimator.
3. iv_dml_twosided  : the Framework's answer. Cross-fitted DML partials the market
                      state out with ML, then 2SLS with TWO instruments (z_a, z_c)
                      for TWO endogenous prices (a, c) -> identifies eps_own AND eps_cross.

Each returns an Estimate with point values, an approximate 95% CI for eps_own, and the
first-stage F statistic (our instrument-strength / "is the instrument still alive" gauge).
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold

from .dgp import Panel


@dataclass
class Estimate:
    eps_own: float
    eps_cross: float | None
    se_own: float
    first_stage_F: float
    method: str

    @property
    def ci_own(self):
        return (self.eps_own - 1.96 * self.se_own, self.eps_own + 1.96 * self.se_own)


def _ols(X: np.ndarray, y: np.ndarray):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    n, k = X.shape
    dof = max(n - k, 1)
    sigma2 = (resid @ resid) / dof
    XtX_inv = np.linalg.pinv(X.T @ X)
    cov = sigma2 * XtX_inv
    return beta, cov, resid


def naive_ols(panel: Panel) -> Estimate:
    X = np.column_stack([np.ones(panel.n), panel.loga, panel.logc, panel.x])
    beta, cov, _ = _ols(X, panel.logq)
    return Estimate(beta[1], beta[2], np.sqrt(cov[1, 1]), np.nan, "naive_ols")


def _first_stage_F(endog: np.ndarray, instruments: np.ndarray, controls: np.ndarray) -> float:
    # F test of the excluded instruments in the first-stage regression of endog on [controls, instruments]
    n = len(endog)
    Xr = controls
    Xf = np.column_stack([controls, instruments])
    _, _, res_r = _ols(Xr, endog)
    _, _, res_f = _ols(Xf, endog)
    rss_r, rss_f = res_r @ res_r, res_f @ res_f
    q = instruments.shape[1]
    k = Xf.shape[1]
    # guard the near-perfect-fit degeneracy: floor the residual variance at a small
    # fraction of the endogenous variance so F stays finite and interpretable.
    tss = float(np.var(endog) * n) + 1e-12
    denom = max(rss_f / max(n - k, 1), 1e-6 * tss / max(n - k, 1))
    F = ((rss_r - rss_f) / q) / denom
    return float(min(F, 1e4))


def iv_single(panel: Panel) -> Estimate:
    """2SLS of eps_own using only z_a. logc treated as an ignored/exogenous nuisance."""
    controls = np.column_stack([np.ones(panel.n), panel.x])
    F = _first_stage_F(panel.loga, panel.z_a[:, None], controls)
    # First stage: loga ~ controls + z_a
    Z = np.column_stack([controls, panel.z_a])
    beta_fs, _, _ = _ols(Z, panel.loga)
    loga_hat = Z @ beta_fs
    # Second stage: logq ~ controls + loga_hat
    X2 = np.column_stack([controls, loga_hat])
    beta, cov, _ = _ols(X2, panel.logq)
    return Estimate(beta[-1], None, np.sqrt(cov[-1, -1]), F, "iv_single")


def iv_dml_twosided(panel: Panel, n_splits: int = 5, seed: int = 0,
                    n_estimators: int = 200, min_samples_leaf: int = 5) -> Estimate:
    """
    Cross-fitted DML (Robinson partialling-out) + 2SLS with two instruments.

    Step 1: residualize logq, loga, logc, z_a, z_c on x using cross-fitted RF.
    Step 2: 2SLS with endogenous [loga~, logc~] and instruments [z_a~, z_c~].

    n_estimators / n_splits are exposed so the online agentic loop can run a
    light cross-fit (fast, refit every few weeks) while offline analysis uses
    the heavy forest. Identification is unchanged; only the nuisance learner
    fidelity moves.
    """
    y = panel.logq
    X = panel.x[:, None]
    cols = {"q": y, "a": panel.loga, "c": panel.logc, "za": panel.z_a, "zc": panel.z_c}
    res = {k: np.zeros_like(v, dtype=float) for k, v in cols.items()}

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    for tr, te in kf.split(X):
        for k, v in cols.items():
            m = RandomForestRegressor(n_estimators=n_estimators, min_samples_leaf=min_samples_leaf,
                                      random_state=seed, n_jobs=-1)
            m.fit(X[tr], v[tr])
            res[k][te] = v[te] - m.predict(X[te])

    D = np.column_stack([res["a"], res["c"]])       # endogenous
    Z = np.column_stack([res["za"], res["zc"]])      # instruments
    # first stage: D on Z
    PZ = Z @ np.linalg.pinv(Z.T @ Z) @ Z.T
    D_hat = PZ @ D
    # second stage: q_res on D_hat
    beta, cov, _ = _ols(D_hat, res["q"])
    F = _first_stage_F(res["a"], Z, np.ones((panel.n, 1)))
    return Estimate(beta[0], beta[1], np.sqrt(cov[0, 0]), F, "iv_dml_twosided")
