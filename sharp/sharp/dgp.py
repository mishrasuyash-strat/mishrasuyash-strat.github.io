"""
dgp.py — Structural data-generating process for reflexive causal markets.

Encodes the *mechanism* behind the Lucas-Critique-in-production failure:

    log q = alpha + eps_own * log(a) + eps_cross * log(c) + gamma * x + u

where
    a  = our price (endogenous: historically set in response to demand shock u)
    c  = competitor price
    x  = observed market state
    u  = latent demand shock (AR(1) confounder)
    z_a = cost shifter for us  (valid instrument for a)
    z_c = cost shifter for them (valid instrument for c)

Regimes
-------
STATIC:    competitor prices off its own cost only  -> exclusion restriction for z_a HOLDS.
STRATEGIC: competitor best-responds to our lagged price with gain kappa and latency L.
           Now z_a -> a -> (competitor best response) -> c -> q, so z_a leaks into demand:
           the exclusion restriction for z_a BREAKS and single-instrument IV of eps_own is biased.

This asymmetry is the whole story: an estimate that is clean in STATIC becomes an
estimate of *the absence of a response* — lethal the moment the response arrives.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np


@dataclass
class MarketParams:
    alpha: float = 3.0          # demand intercept (log)
    eps_own: float = -0.8       # true own-price elasticity
    eps_cross: float = 0.6      # true cross-price elasticity (dormant until competitor reacts)
    gamma: float = 0.4          # effect of market state x on demand
    # confounded pricing rule (observational world)
    phi: float = 0.7            # how much our price chases the demand shock u (endogeneity)
    psi_a: float = 0.9          # strength of our cost instrument z_a on our price
    # competitor
    c0: float = 0.0             # competitor base log-price
    psi_c: float = 0.9          # strength of competitor cost instrument z_c
    kappa: float = 0.85         # competitor best-response gain (strategic regime only)
    latency: int = 3            # competitor response latency in periods
    # noise
    u_rho: float = 0.5          # AR(1) persistence of demand shock
    u_sd: float = 0.25
    z_sd: float = 1.0
    x_sd: float = 1.0
    q_noise_sd: float = 0.05
    mc: float = 0.30           # marginal cost
    exp_jitter: float = 0.20   # deployed price-experimentation via cost instrument z_a (excludable)
    expl_sd: float = 0.10      # independent price-experimentation noise (keeps first stage < 1)


@dataclass
class Panel:
    """A generated market history. All arrays are 1-D of length n."""
    logq: np.ndarray
    loga: np.ndarray
    logc: np.ndarray
    x: np.ndarray
    z_a: np.ndarray
    z_c: np.ndarray
    u: np.ndarray
    regime: np.ndarray  # 0 = static, 1 = strategic
    params: MarketParams = field(repr=False, default=None)

    @property
    def n(self) -> int:
        return len(self.logq)

    def revenue(self) -> np.ndarray:
        return np.exp(self.loga) * np.exp(self.logq)


class ReflexiveMarket:
    """Simulates the structural market under a regime and (optionally) a firm policy."""

    def __init__(self, params: MarketParams | None = None, seed: int = 0):
        self.p = params or MarketParams()
        self.rng = np.random.default_rng(seed)

    def _draw_shocks(self, n: int):
        p = self.p
        u = np.zeros(n)
        e = self.rng.normal(0, p.u_sd, n)
        for t in range(1, n):
            u[t] = p.u_rho * u[t - 1] + e[t]
        z_a = self.rng.normal(0, p.z_sd, n)
        z_c = self.rng.normal(0, p.z_sd, n)
        x = self.rng.normal(0, p.x_sd, n)
        return u, z_a, z_c, x

    def generate(self, n: int, strategic: bool = False,
                 policy=None, break_at: int | None = None) -> Panel:
        """
        Generate a market panel.

        strategic : if True the competitor best-responds (STRATEGIC regime).
        policy    : optional callable f(t, x_t, z_a_t) -> log_price. If given, our price
                    is set by the policy (a *deployed* controller) rather than the
                    historical confounded rule. This is what makes the DGP reflexive:
                    the policy induces the competitor's response and hence the data.
        break_at  : if set, the market is STATIC before break_at and STRATEGIC after,
                    producing an in-sample regime shift.
        """
        p = self.p
        u, z_a, z_c, x = self._draw_shocks(n)
        loga = np.zeros(n)
        logc = np.zeros(n)
        logq = np.zeros(n)
        regime = np.zeros(n, dtype=int)

        for t in range(n):
            strat_t = strategic or (break_at is not None and t >= break_at)
            regime[t] = int(strat_t)

            # our price
            if policy is not None:
                loga[t] = policy(t, x[t], z_a[t])
            else:  # historical confounded pricing rule
                loga[t] = p.phi * u[t] + p.psi_a * z_a[t]

            # competitor price
            base_c = p.c0 + p.psi_c * z_c[t]
            if strat_t and t - p.latency >= 0:
                logc[t] = base_c + p.kappa * loga[t - p.latency]
            else:
                logc[t] = base_c

            # demand
            noise = self.rng.normal(0, p.q_noise_sd)
            logq[t] = (p.alpha + p.eps_own * loga[t] + p.eps_cross * logc[t]
                       + p.gamma * x[t] + u[t] + noise)

        return Panel(logq, loga, logc, x, z_a, z_c, u, regime, params=p)
