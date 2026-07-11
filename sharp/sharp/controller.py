"""
controller.py — The decision agents.

NaiveSnapshotController : ships one clean static-window IV estimate and prices against a
    frozen competitor forever. Wins for a quarter, then pays for it. The trap in the images.

SharpController : the agentic loop.
    sense   -> rolling two-sided IV-DML on a fresh window; fit competitor best response
    detect  -> CUSUM residual monitor + first-stage F floor  = "is my instrument alive?"
    reason  -> reflexivity spectral-radius proxy  rho = |kappa| * |eps_cross / (1+eps_own)|
    act     -> stable & static      : snapshot optimize
               strategic detected   : reflexive (Stackelberg) optimize
               reflexively unstable : DRO / hedged optimize under an ambiguity set
    SHARP = Strategic-Hedged Adaptive Re-estimation for Pricing.
"""
from __future__ import annotations
import numpy as np

from .dgp import MarketParams
from .estimator import iv_single, iv_dml_twosided
from .competitor import fit_best_response
from .optimizer import Economics, optimize_snapshot, optimize_reflexive, optimize_dro
from .regime import cusum
from .simulator import window_panel


class NaiveSnapshotController:
    name = "Naive snapshot"

    def __init__(self, params: MarketParams, warmup: int = 20, static_window: int = 35):
        self.p = params
        self.warmup = warmup
        self.static_window = static_window
        self.belief = None
        self.log = {"mode": [], "eps": [], "F": []}

    def decide(self, state, hist):
        t = state["t"]
        if t < self.warmup:
            self.log["mode"].append("warmup"); self.log["eps"].append(np.nan); self.log["F"].append(np.nan)
            return 0.0
        if self.belief is None:                       # estimate once, in the static window
            pan = window_panel(hist, t, min(t, self.static_window), self.p)
            est = iv_single(pan)
            self.belief = est
        econ = Economics(self.p.alpha, self.belief.eps_own, 0.0, self.p.mc)
        logc_last = hist["logc"][-1] if len(hist["logc"]) else 0.0
        self.log["mode"].append("snapshot")
        self.log["eps"].append(self.belief.eps_own)
        self.log["F"].append(self.belief.first_stage_F)
        return optimize_snapshot(econ, logc_last)     # prices against a frozen competitor


class SharpController:
    name = "SHARP"

    def __init__(self, params: MarketParams, warmup: int = 20, window: int = 40,
                 F_floor: float = 8.0, cusum_thr: float = 3.5, rho_thr: float = 0.6):
        self.p = params
        self.warmup = warmup
        self.window = window
        self.F_floor = F_floor
        self.cusum_thr = cusum_thr
        self.rho_thr = rho_thr
        self.est = None
        self.br = None
        self.last_refit = -999
        self.log = {"mode": [], "eps": [], "eps_cross": [], "F": [], "rho": [], "alarm": []}

    def _refit(self, hist, t):
        pan = window_panel(hist, t, self.window, self.p)
        self.est = iv_dml_twosided(pan, seed=0, n_splits=3, n_estimators=60)
        self.br = fit_best_response(pan)
        self.last_refit = t

    def decide(self, state, hist):
        t = state["t"]
        if t < self.warmup:
            for k, v in zip(self.log, ["warmup", np.nan, np.nan, np.nan, np.nan, False]):
                self.log[k].append(v)
            return 0.0

        need_refit = (self.est is None) or state["expired"] or (t - self.last_refit >= 6)
        if need_refit and t >= self.window:
            self._refit(hist, t)
        elif self.est is None:
            self._refit(hist, min(t, len(hist["logq"])))

        # residual CUSUM on the recent window using the current structural model
        w = min(self.window, t)
        loga_w = np.asarray(hist["loga"][t - w:t], dtype=float)
        logc_w = np.asarray(hist["logc"][t - w:t], dtype=float)
        logq_w = np.asarray(hist["logq"][t - w:t], dtype=float)
        x_w = np.asarray(hist["x"][t - w:t], dtype=float)
        pred = (self.p.alpha + self.est.eps_own * loga_w
                + (self.est.eps_cross or 0.0) * logc_w
                + self.p.gamma * x_w)
        resid = logq_w - pred
        alarm, cstat, _ = cusum(resid, self.cusum_thr)

        kappa = abs(self.br.kappa) if self.br else 0.0
        eps_cross = self.est.eps_cross or 0.0
        denom = abs(1.0 + self.est.eps_own) + 1e-3
        rho = kappa * abs(eps_cross) / denom              # reflexivity spectral-radius proxy
        instrument_dead = self.est.first_stage_F < self.F_floor

        econ = Economics(self.p.alpha, self.est.eps_own, eps_cross, self.p.mc)
        if instrument_dead:
            # identification has genuinely failed -> don't optimize a point, hedge.
            kap_set = [max(0.0, kappa * s) for s in (0.6, 1.0, 1.4)]
            cross_set = [eps_cross * s for s in (0.6, 1.0, 1.4)]
            target = optimize_dro(econ, self.br.c0 if self.br else 0.0, kap_set, cross_set)
            mode = "DRO"
        elif alarm or rho >= self.rho_thr:
            # strategic response detected and tractable -> play the Stackelberg game.
            target = optimize_reflexive(econ, self.br.c0 if self.br else 0.0, kappa)
            mode = "reflexive"
        else:
            logc_last = hist["logc"][-1] if len(hist["logc"]) else 0.0
            target = optimize_snapshot(econ, logc_last)
            mode = "snapshot"

        for k, v in zip(self.log,
                        [mode, self.est.eps_own, eps_cross, self.est.first_stage_F, rho, bool(alarm)]):
            self.log[k].append(v)
        return target
