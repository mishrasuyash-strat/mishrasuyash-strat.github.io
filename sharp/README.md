# SHARP

**Strategic-Hedged Adaptive Re-estimation for Pricing** — reflexive causal inference for pricing in strategic, non-stationary markets.

> A causal price-elasticity estimate that is correct in the market that produced it can be lethal in the market its own deployment creates. When a competitor best-responds to your new price, the cross-price channel that was dormant in your training data wakes up, the exclusion restriction that identified your estimate breaks, and you optimise against a demand curve you personally destroyed. This is the **Lucas Critique in production**. SHARP is the mathematics of it, plus an agent that prices *the game* instead of the snapshot.

---

## Why this exists

Causal inference is the tool we reach for precisely when we intend to *act* — yet in competitive pricing an identified elasticity can be undone by its own deployment. This repository formalises that failure mode (a Reflexive Operator, its equilibrium, and two decision metrics), implements it as a working agentic controller, and tests it on a reproducible benchmark. Every figure is generated from this code.

## The three objects

| Object | Symbol | What it answers |
|---|---|---|
| **Reflexive Operator** | 𝒯 | belief → optimise → competitor best-responds → data → re-estimate → belief′ |
| **Reflexive Causal Equilibrium** | θ* = 𝒯(θ*) | an estimate that is *still true after you act on it* |
| **Reflexivity Gap** | 𝒢 | profit lost by optimising the world you *measured* vs. the world you *caused* |
| **Reflexivity spectral radius** | ρ_R | one estimable number: ρ_R < 1 → ship & re-estimate; ρ_R ≥ 1 → hedge |

## Install

```bash
pip install -e .
# or:  pip install -r requirements.txt
```

Python ≥ 3.10. Dependencies: numpy, scipy, pandas, scikit-learn, matplotlib.

## Quickstart

```bash
python examples/demo_headtohead.py        # the core result in ~20 lines
python examples/demo_reflexivity_gap.py   # 𝒢 and ρ_R vs. competitor aggression
python examples/demo_portfolio.py         # reflexivity changes portfolio construction
pytest -q                                 # the framework's claims, as checks
```

Minimal use:

```python
from sharp import (MarketParams, SimConfig, MarketSimulator,
                    NaiveSnapshotController, SharpController)

p = MarketParams(alpha=3.0, eps_own=-2.2, eps_cross=1.0, kappa=0.9,
                 mc=0.35, exp_jitter=0.34, expl_sd=0.10)
cfg = SimConfig(horizon=140, break_week=52, latency=3, seed=3)

naive  = MarketSimulator(p, cfg).run(NaiveSnapshotController(p, warmup=40))
sharp  = MarketSimulator(p, cfg).run(SharpController(p, warmup=40, window=40))
```

## What’s inside

```
sharp/
  dgp.py          structural reflexive DGP (static vs strategic competitor)
  estimator.py    naive OLS · single-IV · two-sided IV-DML (cross-fitted)
  competitor.py   fit competitor best-response gain κ and latency
  regime.py       CUSUM · Chow · first-stage-F monitoring
  optimizer.py    snapshot · reflexive (Stackelberg) · DRO pricing
  reflexive.py    the Reflexive Operator, RCE iteration, ρ_R (finite-diff)
  dynamics.py     linear best-response instance with closed-form ρ_R
  metrics.py      Reflexivity Gap · CVaR · regret
  simulator.py    discrete-event market clock (break, BR arrivals, expiry)
  controller.py   NaiveSnapshotController · SharpController (the agent)
  portfolio.py    score a book of decisions by mean − λ·CVaR(drawdown)
experiments/      canonical config + figure generators
examples/         runnable demos
paper/            LaTeX source + compiled PDF
blog/             self-contained tutorial (open blog/index.html)
tests/            pytest suite
```

## Headline result

Benchmark where the baseline is **not** a strawman — it ships a genuinely correct static
elasticity and is optimal in the static regime. The competitor turns strategic at week 52.

| Metric | Naive snapshot | SHARP |
|---|---|---|
| Seeds won (of 12) | 1 | **11** |
| Cumulative profit (post-warmup) | 1708 ± 222 | **1941 ± 223**  (+14.1%) |
| Uplift, pre-break | — | −0.3% (no premium) |
| Uplift, post-break | — | **+17.2%** |

Paired *t*-test on post-warmup profit: *t* = 6.7, *p* < 10⁻⁴. In a three-market portfolio,
SHARP cuts the CVaR of post-break drawdown ~9× and triples the risk-adjusted score.

## Case study: pharmaceutical pricing

The mechanism is documented in the wild. In **PCSK9 inhibitors** (2018–19) Amgen cut Repatha's
list price ~60% to $5,850 and Regeneron/Sanofi matched Praluent to the identical figure — a public
tit-for-tat on pre-rebate list prices. In **GLP-1 agonists** (2025–26) Novo cut cash prices
$499→$349 and Eli Lilly best-responded on its direct-to-consumer channel within weeks, followed by
35–50% list-price cuts. Both fit the reflexive pattern: a price set as if the rival would hold
still, then matched once deployed.

Pharma is a *sharper* instance, not a weaker one: the decision surface is **net price + formulary
access** (rebate-mediated), and exogenous **policy shocks** (IRA Medicare negotiation, government
deals) coincide with competitive activation — exactly what SHARP's regime detector and DRO mode
are for. Scope: this applies to *competitive branded* classes (2+ rivals contesting access), **not**
patent-protected monopoly. A calibrated branded-duopoly benchmark
(`experiments/pharma_case.py`) has SHARP winning 8/8 seeds at ~**+28%** cumulative net revenue.

## The agent’s loop

**sense** (rolling two-sided IV-DML + fit κ) → **detect** (CUSUM + first-stage-F) →
**reason** (reflexivity proxy ρ̂) → **act** (snapshot / Stackelberg / DRO). In the static
regime it reduces to the snapshot agent; it changes objective only when evidence warrants.

## Paper

`paper/sharp.pdf` — definitions, an existence/one-step-convergence result for the RCE under
honest identification, sign/monotonicity of 𝒢, and the ρ_R convergence dichotomy (closed form
in the linear instance), plus the experiments.

## Lineage & honest novelty

SHARP composes known ingredients — the **Lucas Critique** (diagnosis), **performative
prediction** (the RCE is the causal-and-strategic analog of a performatively stable point),
**double/debiased ML + 2SLS** (identification), **DRO** (the hedge) — into a decision loop. The
new pieces are small and practical: the **Reflexivity Gap** as a decision-facing cost, the
**reflexivity spectral radius** as an estimable ship/hedge rule, and the agent that switches its
own objective. Limits are real: a parametric single-gain competitor, constant-elasticity demand,
finite-difference ρ_R, and a simulated (if mechanism-faithful) benchmark.

## Contributing

Contributions and collaboration — especially on the two-adaptive-agents case (where both firms
learn) and tests on real data — are welcome.

## License

MIT © 2026 Suyash Mishra
