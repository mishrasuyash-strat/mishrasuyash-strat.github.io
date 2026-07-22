---
layout: post
title: "YUKTI: when the plan is only as good as the numbers you made up"
subtitle: "From a worded situation to robust, verifiable decisions — uncertainty typed in, Pareto frontiers that survive their assumptions, and a regret certificate."
date: 2026-06-22
tags: [decisions, optimization, robustness, llm]
reading: "5 min read"
---

Ask a language model to turn a messy, worded situation into a plan and it will
happily do it: read the paragraph, name an objective, fill in the coefficients,
call a solver, hand you the answer. The dominant autoformulation pipelines —
NL4Opt, OptiMUS, ORLM, OR-LLM-Agent — all work roughly this way. They commit to a
single objective and point-valued numbers, then solve once.

For anything low-stakes, that is fine. But for decisions that allocate real
budget, real effort, or real clinical attention, that confidence is exactly the
failure mode. Every number the model "read out" of the text is actually an
assumption. A plan that is optimal only if all of those guesses are exactly right
is not robust — it is a mimicry of computation. YUKTI is my attempt to change what
autoformulation is even aiming at.

## Represent the uncertainty, don't hide it

Instead of collapsing the situation into a single objective with fixed
coefficients, YUKTI's representation is a typed-proposition graph. Each
relationship in it carries more than a number: a shape prior for what kind of
quantity it is, the uncertainty around any coefficient, and provenance — where the
value came from in the first place. The uncertainty lives inside the intermediate
representation rather than being bolted on at the end, which is what makes the
later robustness analysis honest instead of cosmetic.

## Solve the right way for each piece

Different parts of a problem want different machinery, so YUKTI routes each stage
to the solver that fits — exact, nonlinear, or evolutionary — and couples the
stages by a distributional Pareto hand-off rather than a single hard number passed
downstream. Uncertainty flows through the pipeline instead of being discarded at
the first hop.

## Frontiers that survive their assumptions

The core construct is what I call an Assumption-Robust Pareto Frontier. Rather
than reporting one optimal plan, YUKTI resamples the assumptions themselves —
including structural, worst-case perturbations (ε-contamination) — and scores how
often each candidate action survives across that resampling. That survival rate, ρ,
is the honest signal: not "this is optimal," but "this action keeps looking good
even when the guesses are wrong." It is a very different thing to hand a
decision-maker.

## A certificate, not just an answer

Finally, YUKTI attaches a regret certificate — a bound on how much you could
regret the recommended action if the world turns out to lie within the modeled
uncertainty. The aim across all of it is a decision you can *defend* afterward,
not merely one that looked optimal on paper.

This sits at the center of what I keep returning to: high-stakes decisions should
be rigorous, verifiable, and defensible — especially when a language model is the
thing turning words into numbers.

Full paper on arXiv: [2607.09706](https://arxiv.org/abs/2607.09706).
