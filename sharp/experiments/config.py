"""
config.py — the single source of truth for the SHARP benchmark.

Every figure, example, and reported number is generated from these exact
settings so the blog, the paper, and the repository never disagree.
"""
from __future__ import annotations
from sharp.dgp import MarketParams
from sharp.simulator import MarketSimulator, SimConfig
from sharp.controller import NaiveSnapshotController, SharpController

# --- structural truth of the market -----------------------------------------
PARAMS = dict(
    alpha=3.0,
    eps_own=-2.2,      # true own-price elasticity (elastic)
    eps_cross=1.0,     # cross-price elasticity — dormant until the competitor reacts
    gamma=0.3,         # market-state loading
    kappa=0.9,         # competitor best-response gain in the strategic regime
    c0=0.0,
    mc=0.35,           # marginal cost
    exp_jitter=0.34,   # price experimentation through the (excludable) cost instrument z_a
    expl_sd=0.10,      # idiosyncratic experimentation noise (keeps the first stage < 1)
    latency=3,         # competitor response latency (weeks)
)

# --- experiment horizon & agents --------------------------------------------
WARMUP = 40        # weeks of pure experimentation before either agent prices for profit
WINDOW = 40        # SHARP rolling re-estimation window
STATIC_WINDOW = 40 # naive agent's one-shot static estimation window
BREAK_WEEK = 52    # the regime shift: competitor switches from static to strategic
HORIZON = 140
EXPIRY = 12        # scheduled estimate-expiry events
COMPARE_FROM = WARMUP   # cumulative profit is compared post-warmup

# derived, for reference in prose
def effective_elasticity() -> float:
    return PARAMS["eps_own"] + PARAMS["eps_cross"] * PARAMS["kappa"]

def ce_optimal_price(eps: float, mc: float = PARAMS["mc"]) -> float:
    """Constant-elasticity monopoly optimum (interior when eps < -1)."""
    return mc * eps / (1.0 + eps)


def make_params() -> MarketParams:
    return MarketParams(**PARAMS)


def run_headtohead(seed: int):
    """Run naive vs SHARP on one seed. Returns (hist_naive, hist_sharp, naive, sharp)."""
    p = make_params()
    cfg = SimConfig(horizon=HORIZON, break_week=BREAK_WEEK, latency=PARAMS["latency"],
                    expiry=EXPIRY, seed=seed, loyalty_eta=0.0)
    naive = NaiveSnapshotController(p, warmup=WARMUP, static_window=STATIC_WINDOW)
    sth = SharpController(p, warmup=WARMUP, window=WINDOW)
    hn = MarketSimulator(p, cfg).run(naive)
    hs = MarketSimulator(p, cfg).run(sth)
    return hn, hs, naive, sth
