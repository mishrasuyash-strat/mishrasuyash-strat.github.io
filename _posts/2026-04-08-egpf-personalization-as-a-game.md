---
layout: post
title: "Personalization is a game, not a classification"
subtitle: "EGPF models physician engagement as an incomplete-information Bayesian game and lets equilibria steer what a model generates."
date: 2026-04-08 10:00:00 +0200
tags: [game-theory, personalization, category-theory]
reading: "3 min read"
---

When a physician weighs a new therapy, they are balancing clinical evidence, peer
signals, patient specifics, access and cost, personal risk tolerance, and plain
inertia — and their response shifts depending on how you engage them. That
feedback loop is what makes it a game rather than a prediction problem.

EGPF, the Equilibrium-Guided Personalization Framework, models the
pharma–physician interaction as an incomplete-information Bayesian game. Physician
"types" are inferred through functorial mappings from observational data;
equilibrium strategies then guide what a language model generates; and
information-theoretic feedback keeps the whole thing recalibrating over time. I
lean on category-theoretic structure — functors, natural transformations,
monoidal composition — so that physician archetypes are modular, composable, and
hold their shape under domain shift.

The framework also introduces a Rate-Distortion Equilibrium criterion that makes
the personalization-versus-privacy trade-off explicit rather than something you
discover after the fact.

Full paper on arXiv: [2604.06860](https://arxiv.org/abs/2604.06860).
