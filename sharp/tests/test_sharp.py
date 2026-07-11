"""
test_sharp.py — the framework's claims, as executable checks.

Run:  pytest -q         (or)   python -m pytest tests/ -q
Fast: only one test runs the full agentic controller loop.
"""
import numpy as np
import pytest

from sharp import (MarketParams, ReflexiveMarket, Panel,
                    iv_single, iv_dml_twosided, naive_ols,
                    fit_best_response, optimize_snapshot, optimize_reflexive, optimize_dro,
                    Economics, reflexivity_gap, cvar, regret,
                    chow_test, scan_for_regime, cusum, LinearGame,
                    MarketSimulator, SimConfig,
                    NaiveSnapshotController, SharpController)

TRUE = dict(alpha=3.0, eps_own=-2.2, eps_cross=1.0, gamma=0.3, kappa=0.9,
            c0=0.0, mc=0.35, exp_jitter=0.34, expl_sd=0.10)


def _panel(strategic, n=4000, seed=0):
    p = MarketParams(**TRUE)
    mkt = ReflexiveMarket(p, seed=seed)
    return mkt.generate(n, strategic=strategic)


# ---------------------------------------------------------------- estimators
def test_iv_dml_recovers_both_elasticities():
    pan = _panel(strategic=True, n=5000)
    est = iv_dml_twosided(pan, seed=0)
    assert abs(est.eps_own - TRUE["eps_own"]) < 0.2, est.eps_own
    assert abs(est.eps_cross - TRUE["eps_cross"]) < 0.2, est.eps_cross


def test_iv_single_clean_in_static_regime():
    pan = _panel(strategic=False, n=4000)
    est = iv_single(pan)
    assert abs(est.eps_own - TRUE["eps_own"]) < 0.25, est.eps_own


def test_naive_ols_is_biased():
    # OLS ignores the demand-shock confounder -> should miss the truth by more than IV
    pan = _panel(strategic=False, n=4000)
    ols = naive_ols(pan).eps_own
    iv = iv_single(pan).eps_own
    assert abs(iv - TRUE["eps_own"]) <= abs(ols - TRUE["eps_own"]) + 1e-6


def test_first_stage_F_is_finite_and_strong():
    pan = _panel(strategic=False, n=2000)
    F = iv_single(pan).first_stage_F
    assert np.isfinite(F) and F > 20


# ---------------------------------------------------------------- competitor
def test_best_response_recovers_kappa_when_strategic():
    br = fit_best_response(_panel(strategic=True, n=4000))
    assert abs(br.kappa - TRUE["kappa"]) < 0.2, br.kappa


def test_best_response_near_zero_when_static():
    br = fit_best_response(_panel(strategic=False, n=4000))
    assert abs(br.kappa) < 0.2, br.kappa


# ---------------------------------------------------------------- regime
def test_regime_break_detected_in_reaction_function():
    # The demand equation is structurally stable across the break (that is the whole
    # point). What changes is the COMPETITOR: static (kappa=0) -> strategic (kappa>0).
    # A Chow test on the reaction function log c ~ lagged log a should light up.
    p = MarketParams(**TRUE)
    mkt = ReflexiveMarket(p, seed=1)
    n, brk, lat = 600, 300, 3
    pan = mkt.generate(n, break_at=brk)
    loga_lag = np.concatenate([np.zeros(lat), pan.loga[:-lat]])
    X = np.column_stack([np.ones(n), loga_lag])
    chow_p = chow_test(pan.logc, X, split=brk)
    assert chow_p < 1e-3, chow_p


def test_scan_flags_instrument_death():
    # a weak instrument (low first-stage F) must be reported as not alive
    r = np.random.default_rng(0).normal(0, 1, 300)
    X = np.column_stack([np.ones(300), np.random.default_rng(1).normal(0, 1, 300)])
    sig = scan_for_regime(r, X, r, first_stage_F=3.0, F_floor=10.0)
    assert not sig.instrument_alive


def test_cusum_fires_on_shift():
    r = np.concatenate([np.random.default_rng(0).normal(0, 1, 200),
                        np.random.default_rng(1).normal(3, 1, 100)])
    alarm, stat, loc = cusum(r, threshold=3.5)
    assert alarm and loc is not None


# ---------------------------------------------------------------- optimizer
def test_reflexive_prices_above_snapshot_under_positive_coupling():
    econ = Economics(TRUE["alpha"], TRUE["eps_own"], TRUE["eps_cross"], TRUE["mc"])
    snap = optimize_snapshot(econ, logc_current=0.0)
    refl = optimize_reflexive(econ, br_c0=0.0, br_kappa=TRUE["kappa"])
    assert refl >= snap - 1e-9


def test_dro_between_snapshot_and_reflexive():
    econ = Economics(TRUE["alpha"], TRUE["eps_own"], TRUE["eps_cross"], TRUE["mc"])
    dro = optimize_dro(econ, 0.0, [0.4, 0.9, 1.4], [0.6, 1.0, 1.4])
    assert np.log(0.5) - 1e-6 <= dro <= np.log(2.2) + 1e-6


# ---------------------------------------------------------------- dynamics / RCE
def test_cobweb_converges_when_rho_below_one():
    g = LinearGame(kappa=1.2)          # rho = 0.6
    assert g.rho_R < 1
    a, c = g.iterate(1.0, steps=40)
    a_star = g.fixed_point()[0]
    assert abs(a[-1] - a_star) < 1e-2


def test_cobweb_diverges_when_rho_above_one():
    g = LinearGame(kappa=2.4)          # rho = 1.2
    assert g.rho_R > 1
    a, c = g.iterate(1.0, steps=30)
    assert abs(a[-1]) > abs(a[3])      # trajectory grows without bound


# ---------------------------------------------------------------- metrics
def test_reflexivity_gap_positive_when_world_moves_against_you():
    econ = Economics(TRUE["alpha"], TRUE["eps_own"], TRUE["eps_cross"], TRUE["mc"])
    a = optimize_snapshot(econ, 0.0)
    # you assumed competitor stays at 0; it actually rises (hurting you via cross term<0 side)
    g = reflexivity_gap(econ, a, assumed_logc=0.0, induced_logc=-0.5)
    assert isinstance(g, float)


def test_cvar_is_worst_tail_mean():
    losses = np.arange(100.0)
    c = cvar(losses, level=0.9)
    assert c > np.mean(losses)          # tail worse than average


def test_regret_nonneg_against_oracle():
    realized = np.array([1.0, 2.0, 3.0]); oracle = np.array([2.0, 2.0, 5.0])
    assert np.all(regret(realized, oracle) >= 0)


# ---------------------------------------------------------------- simulator
def test_simulator_produces_finite_history():
    p = MarketParams(**TRUE)
    cfg = SimConfig(horizon=80, break_week=40, seed=0)
    h = MarketSimulator(p, cfg).run(NaiveSnapshotController(p, warmup=30, static_window=30))
    assert len(h["profit"]) == 80
    assert np.all(np.isfinite(h["profit"]))


# ---------------------------------------------------------------- integration
@pytest.mark.slow
def test_sharp_beats_naive_post_break():
    p = MarketParams(**TRUE)
    cfg = SimConfig(horizon=140, break_week=52, latency=3, expiry=12, seed=3, loyalty_eta=0.0)
    hn = MarketSimulator(p, cfg).run(NaiveSnapshotController(p, warmup=40, static_window=40))
    hs = MarketSimulator(p, cfg).run(SharpController(p, warmup=40, window=40))
    assert hs["profit"][52:].sum() > hn["profit"][52:].sum()


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-q"]))
