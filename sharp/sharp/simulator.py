"""
simulator.py — Event-based simulation of a reflexive market.

A discrete-event engine on a weekly clock. Scheduled events carry the strategic
dynamics that make the world non-stationary:

    REGIME_BREAK : the market switches from static to strategic.
    BR_ARRIVAL   : the competitor's best response to a past price lands (after latency).
    EXPIRY       : the current estimate expires and must be refreshed.
    SHOCK        : an exogenous demand shock (e.g. stimulus, rotation to services).

The engine is agnostic to the controller: pass any object with .decide(state, history).
This is the substrate for simulation, forecasting, and portfolio optimization.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import heapq
import numpy as np

from .dgp import MarketParams, Panel


@dataclass(order=True)
class Event:
    time: int
    kind: str = field(compare=False)
    payload: dict = field(compare=False, default_factory=dict)


@dataclass
class SimConfig:
    horizon: int = 104          # weeks
    break_week: int = 26        # competitor turns strategic here
    latency: int = 3
    expiry: int = 8             # estimate expiry cadence (weeks)
    window: int = 40            # rolling estimation window
    shock_week: int | None = None
    shock_size: float = 0.0
    loyalty_eta: float = 0.0    # slow customer defection when pricier than rivals (0 = off)
    seed: int = 0


class MarketSimulator:
    def __init__(self, params: MarketParams, cfg: SimConfig):
        self.p = params
        self.cfg = cfg
        self.rng = np.random.default_rng(cfg.seed)

    def run(self, controller):
        p, cfg = self.p, self.cfg
        rng = self.rng
        H = cfg.horizon

        # scheduled events
        heap: list[Event] = []
        heapq.heappush(heap, Event(cfg.break_week, "REGIME_BREAK"))
        for w in range(cfg.expiry, H, cfg.expiry):
            heapq.heappush(heap, Event(w, "EXPIRY"))
        if cfg.shock_week is not None:
            heapq.heappush(heap, Event(cfg.shock_week, "SHOCK"))

        strategic = False
        shock = 0.0
        comp_target_logc = p.c0          # competitor current log-price
        loyalty = 1.0                    # slow customer-base stock; leaks when you are pricier
        # AR(1) demand shock
        u = 0.0

        hist = {k: [] for k in
                ["loga", "logc", "logq", "z_a", "z_c", "x", "regime", "profit", "expiry", "loyalty"]}
        events_log = []

        for t in range(H):
            expired = False
            while heap and heap[0].time == t:
                ev = heapq.heappop(heap)
                events_log.append((t, ev.kind))
                if ev.kind == "REGIME_BREAK":
                    strategic = True
                elif ev.kind == "EXPIRY":
                    expired = True
                elif ev.kind == "SHOCK":
                    shock = cfg.shock_size
                elif ev.kind == "BR_ARRIVAL":
                    comp_target_logc = ev.payload["logc"]

            # exogenous draws
            e = rng.normal(0, p.u_sd)
            u = p.u_rho * u + e
            z_a = rng.normal(0, p.z_sd)
            z_c = rng.normal(0, p.z_sd)
            x = rng.normal(0, p.x_sd) + shock
            shock *= 0.6  # shock decays

            state = dict(t=t, strategic=strategic, expired=expired,
                         comp_logc=comp_target_logc, z_a=z_a, x=x)
            # controller picks a target log-price; cost shock z_a + idiosyncratic
            # experimentation noise jitter it (the latter keeps the instrument < 1).
            target_loga = controller.decide(state, hist)
            nu = rng.normal(0, p.expl_sd)
            loga = float(np.clip(target_loga + p.exp_jitter * z_a + nu, np.log(0.5), np.log(2.2)))

            # competitor: own cost always; if strategic, schedule a best response
            base_c = p.c0 + p.psi_c * z_c
            if strategic:
                future_logc = base_c + p.kappa * loga
                heapq.heappush(heap, Event(t + cfg.latency, "BR_ARRIVAL",
                                           {"logc": future_logc}))
            logc = comp_target_logc if strategic else base_c

            noise = rng.normal(0, p.q_noise_sd)
            # slow share leak: lose customers when you are pricier than the competitor
            gap = loga - logc
            if gap > 0:
                loyalty -= cfg.loyalty_eta * gap
            else:
                loyalty += 0.4 * cfg.loyalty_eta * (-gap)
            loyalty = float(np.clip(loyalty, 0.35, 1.15))

            logq = (p.alpha + p.eps_own * loga + p.eps_cross * logc
                    + p.gamma * x + u + noise + np.log(loyalty))
            price = np.exp(loga)
            profit = (price - p.mc) * np.exp(logq)

            for k, v in zip(hist, [loga, logc, logq, z_a, z_c, x,
                                   int(strategic), profit, int(expired), loyalty]):
                hist[k].append(v)

        for k in hist:
            hist[k] = np.array(hist[k])
        hist["events"] = events_log
        return hist


def window_panel(hist: dict, end: int, window: int, params: MarketParams) -> Panel:
    lo = max(0, end - window)
    def arr(key):
        return np.asarray(hist[key][lo:end], dtype=float)
    n = len(hist["logq"][lo:end])
    return Panel(arr("logq"), arr("loga"), arr("logc"),
                 arr("x"), arr("z_a"), arr("z_c"),
                 np.zeros(n), np.asarray(hist["regime"][lo:end]), params=params)
