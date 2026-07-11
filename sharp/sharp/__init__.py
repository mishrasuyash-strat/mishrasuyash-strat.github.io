"""
SHARP — Reflexive Causal Equilibria for decision portfolios in strategic,
non-stationary markets.

SHARP = Strategic-Hedged Adaptive Re-estimation for Pricing.

Core idea: a causal estimate is only valid inside the regime that produced it. When you
act on it, you may change that regime (the Lucas Critique). SHARP seeks the Reflexive
Causal Equilibrium — an estimate that is still true after you have acted on it — and
hedges when no stable equilibrium exists.
"""
from .dgp import MarketParams, ReflexiveMarket, Panel
from .estimator import naive_ols, iv_single, iv_dml_twosided, Estimate
from .competitor import fit_best_response, BestResponse
from .regime import cusum, chow_test, scan_for_regime, RegimeSignal
from .optimizer import (Economics, optimize_snapshot, optimize_reflexive, optimize_dro)
from .reflexive import (reflexive_operator, iterate_to_rce,
                        reflexivity_spectral_radius, ReflexiveConfig)
from .metrics import reflexivity_gap, cvar, regret
from .simulator import MarketSimulator, SimConfig, window_panel
from .controller import NaiveSnapshotController, SharpController
from .portfolio import DecisionUnit, evaluate_unit, evaluate_portfolio

__version__ = "0.1.0"

from .dynamics import LinearGame  # noqa: E402
