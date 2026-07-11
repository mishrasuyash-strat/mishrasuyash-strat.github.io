"""
reflexive.py — The mathematical core.

Define the Reflexive Operator  T : theta -> theta'  as the composition

    theta  --optimize-->  a*(theta)  --environment BR-->  c = BR(a*)
           --data-->  D(a*, c)  --re-estimate-->  theta'

A Reflexive Causal Equilibrium (RCE) is a fixed point  theta* = T(theta*):
an estimate that is still true after you have acted on it.

The naive/snapshot estimate is generally NOT a fixed point. Iterating T either
    contracts to an RCE           (reflexivity spectral radius rho_R < 1), or
    diverges / cycles             (rho_R >= 1)  -> the $1.5B markdown.

    rho_R  =  |dBR/da| * |da*/dtheta| * |dtheta_hat/d a|

estimated here by finite differences on the actual simulate->estimate pipeline.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

from .dgp import ReflexiveMarket, MarketParams
from .estimator import iv_single, iv_dml_twosided
from .optimizer import Economics, optimize_snapshot, optimize_reflexive
from .competitor import fit_best_response


def _deploy_policy(target_loga: float, psi_a: float):
    """A deployed policy: aim at target price, let cost shocks jitter it for identification."""
    def policy(t, x_t, z_a_t):
        return target_loga + psi_a * z_a_t
    return policy


@dataclass
class ReflexiveConfig:
    n: int = 1200
    honest: bool = True          # True -> two-sided IV-DML re-estimation; False -> single-IV (naive)
    seed: int = 0


def reflexive_operator(belief_eps: float, true_params: MarketParams,
                       cfg: ReflexiveConfig) -> float:
    """One application of T: optimize on belief, deploy in strategic world, re-estimate eps_own."""
    econ = Economics(alpha=true_params.alpha, eps_own=belief_eps,
                     eps_cross=0.0, marginal_cost=true_params.mc)   # belief ignores cross term (snapshot)
    target = optimize_snapshot(econ, logc_current=0.0)
    mkt = ReflexiveMarket(true_params, seed=cfg.seed)
    panel = mkt.generate(cfg.n, strategic=True,
                         policy=_deploy_policy(target, true_params.exp_jitter))
    est = iv_dml_twosided(panel, seed=cfg.seed) if cfg.honest else iv_single(panel)
    return est.eps_own


def iterate_to_rce(theta0: float, true_params: MarketParams, cfg: ReflexiveConfig,
                   max_iter: int = 20, tol: float = 1e-3):
    """Iterate the Reflexive Operator. Returns (trajectory, converged, theta_star)."""
    traj = [theta0]
    theta = theta0
    for _ in range(max_iter):
        theta_new = reflexive_operator(theta, true_params, cfg)
        traj.append(theta_new)
        if abs(theta_new - theta) < tol:
            return np.array(traj), True, theta_new
        theta = theta_new
    return np.array(traj), False, theta


def reflexivity_spectral_radius(true_params: MarketParams, cfg: ReflexiveConfig,
                                belief_eps: float, h: float = 0.05) -> dict:
    """
    Estimate rho_R = |dBR/da| * |da*/dtheta| * |dtheta_hat/da| by finite differences
    on the real pipeline. rho_R >= 1 flags a reflexively unstable regime.
    """
    # g1: dBR/da  (competitor response gain, from a strategic panel)
    mkt = ReflexiveMarket(true_params, seed=cfg.seed)
    probe = mkt.generate(cfg.n, strategic=True)
    br = fit_best_response(probe)
    g1 = abs(br.kappa)

    # g2: da*/dtheta  (how the snapshot-optimal price moves with the elasticity belief)
    econ_hi = Economics(true_params.alpha, belief_eps + h, 0.0, true_params.mc)
    econ_lo = Economics(true_params.alpha, belief_eps - h, 0.0, true_params.mc)
    a_hi = optimize_snapshot(econ_hi, 0.0)
    a_lo = optimize_snapshot(econ_lo, 0.0)
    g2 = abs(a_hi - a_lo) / (2 * h)

    # g3: dtheta_hat/da  (how the re-estimated elasticity shifts with the deployed price)
    da = 0.1
    def est_at(target):
        m = ReflexiveMarket(true_params, seed=cfg.seed)
        pan = m.generate(cfg.n, strategic=True,
                         policy=_deploy_policy(target, true_params.exp_jitter))
        return (iv_dml_twosided(pan, seed=cfg.seed) if cfg.honest
                else iv_single(pan)).eps_own
    base_target = optimize_snapshot(Economics(true_params.alpha, belief_eps, 0.0, true_params.mc), 0.0)
    g3 = abs(est_at(base_target + da) - est_at(base_target - da)) / (2 * da)

    rho = g1 * g2 * g3
    return {"rho_R": rho, "g1_dBR_da": g1, "g2_da_dtheta": g2,
            "g3_dtheta_da": g3, "stable": rho < 1.0}
