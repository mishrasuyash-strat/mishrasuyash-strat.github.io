---
layout: post
title: "Memory that has to earn its place"
subtitle: "Prism is an evolutionary memory substrate for multi-agent systems doing open-ended discovery."
date: 2026-04-08 09:00:00 +0200
tags: [agents, memory, evolution]
reading: "3 min read"
---

Long-running agent systems accumulate a lot of memory, and most of it is not worth
keeping in context. Prism — Probabilistic Retrieval with Information-Stratified
Memory — is an attempt to make memory behave like an economy, where entries have
to earn their place.

It pulls four usually-separate ideas into one decision-theoretic system:
file-based persistence, vector semantic memory, graph-structured relational
memory, and multi-agent evolutionary search. A few pieces I care about most: an
entropy-gated stratification that sorts memories into skills, notes, and attempts
by their Shannon information content; a causal memory graph that records
interventional edges and which agent produced what; a value-of-information
retrieval policy; and replicator-decay dynamics that treat a memory's confidence
as evolutionary fitness, converging to what I call an Evolutionary Stable Memory
Set.

On the LOCOMO benchmark it scores well above Mem0, and on evolutionary
optimization tasks a four-agent Prism improves substantially faster than a single
agent working alone.

Full paper on arXiv: [2604.19795](https://arxiv.org/abs/2604.19795).
