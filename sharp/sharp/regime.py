"""
regime.py — Regime detection as a first-class citizen.

An estimate is only valid inside the regime that produced it. These monitors watch for
the three tells from the Framework:
  * residual drift            -> CUSUM
  * a structural break        -> Chow test
  * instrument death          -> first-stage F collapse

If the instrument dies, you do not optimize. You re-estimate.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy import stats


@dataclass
class RegimeSignal:
    cusum_alarm: bool
    cusum_stat: float
    chow_p: float
    instrument_alive: bool
    first_stage_F: float
    break_index: int | None


def cusum(residuals: np.ndarray, threshold: float = 5.0) -> tuple[bool, float, int | None]:
    """Standardized recursive CUSUM of residuals. Returns (alarm, max_stat, break_idx)."""
    r = np.asarray(residuals, dtype=float)
    s = r.std(ddof=1) + 1e-12
    c = np.cumsum(r - r.mean()) / s
    stat = np.max(np.abs(c)) / np.sqrt(len(r))
    idx = int(np.argmax(np.abs(c))) if stat > threshold else None
    return stat > threshold, float(stat), idx


def chow_test(y: np.ndarray, X: np.ndarray, split: int) -> float:
    """Chow test for a structural break at `split`. Returns the p-value (small = break)."""
    def rss(yy, XX):
        b, *_ = np.linalg.lstsq(XX, yy, rcond=None)
        e = yy - XX @ b
        return e @ e
    n, k = X.shape
    pooled = rss(y, X)
    r1 = rss(y[:split], X[:split])
    r2 = rss(y[split:], X[split:])
    num = (pooled - (r1 + r2)) / k
    den = (r1 + r2) / (n - 2 * k)
    if den <= 0:
        return 1.0
    F = num / den
    return float(1 - stats.f.cdf(F, k, n - 2 * k))


def scan_for_regime(y: np.ndarray, X: np.ndarray, residuals: np.ndarray,
                    first_stage_F: float, F_floor: float = 10.0,
                    cusum_threshold: float = 5.0) -> RegimeSignal:
    alarm, stat, idx = cusum(residuals, cusum_threshold)
    # Chow at the CUSUM-implied break (fall back to the midpoint)
    split = idx if idx not in (None, 0) and idx < len(y) else len(y) // 2
    split = int(np.clip(split, X.shape[1] + 1, len(y) - X.shape[1] - 1))
    p = chow_test(y, X, split)
    return RegimeSignal(
        cusum_alarm=alarm, cusum_stat=stat, chow_p=p,
        instrument_alive=first_stage_F >= F_floor,
        first_stage_F=first_stage_F, break_index=idx,
    )
