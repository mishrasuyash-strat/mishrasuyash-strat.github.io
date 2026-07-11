"""
rce_dynamics.py — the Reflexive Operator in its linear-quadratic instance.

The full framework's operator T is nonlinear, but its stability is governed by a
single modulus, the reflexivity spectral radius rho_R. Here we exhibit the
closed-form instance where that is transparent: linear demand + linear reaction
functions (a Bertrand-style best-response game).

    firm demand      q(a, c) = alpha + b_own * a + b_cross * c        (b_own < 0)
    firm best resp.  a*(c)   = (alpha + b_cross c - b_own mc) / (-2 b_own)
    rival reaction   c*(a)   = c0 + kappa * a

Iterating a_{k+1} = a*(c*(a_k)) is a cobweb whose slope is

    rho_R = |da*/dc| * |dc*/da| = kappa * b_cross / (2 |b_own|).

rho_R < 1  -> the naive re-optimize-each-period loop converges to the RCE.
rho_R >= 1 -> it diverges / oscillates: the empirical signature of the markdown.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class LinearGame:
    alpha: float = 10.0
    b_own: float = -1.0
    b_cross: float = 1.0
    mc: float = 1.0
    c0: float = 1.0
    kappa: float = 1.2

    def best_response_firm(self, c):
        return (self.alpha + self.b_cross * c - self.b_own * self.mc) / (-2.0 * self.b_own)

    def reaction_rival(self, a):
        return self.c0 + self.kappa * a

    @property
    def rho_R(self) -> float:
        return abs(self.kappa) * self.b_cross / (2.0 * abs(self.b_own))

    def fixed_point(self):
        """Solve a = a*(c0 + kappa a) in closed form (the RCE), if it exists."""
        s = self.b_cross / (-2.0 * self.b_own)       # da*/dc
        denom = 1.0 - s * self.kappa
        if abs(denom) < 1e-9:
            return None
        num = (self.alpha - self.b_own * self.mc) / (-2.0 * self.b_own) + s * self.c0
        a_star = num / denom
        return a_star, self.reaction_rival(a_star)

    def iterate(self, a0: float, steps: int = 14):
        """Return the cobweb trajectory [(a0,c0'),(a1,c1),...] of the naive loop."""
        a = a0
        traj_a, traj_c = [], []
        for _ in range(steps):
            c = self.reaction_rival(a)
            traj_a.append(a); traj_c.append(c)
            a = self.best_response_firm(c)
        return np.array(traj_a), np.array(traj_c)
