---
layout: post
title: "Gluing local decisions into a global one"
subtitle: "A short, concrete take on why sheaf-style thinking is useful for multi-agent systems."
date: 2026-06-28
tags: [multi-agent, sheaf-theory, decisions]
reading: "5 min read"
math: true
---

Suppose you have several agents, each an expert on a slice of a problem. Agent
$A$ knows region $U$, agent $B$ knows region $V$, and their regions overlap on
$U \cap V$. Each returns a *local* answer. The practical question is simple to
state and annoying to answer: **when do the local answers glue into a single
global one you can trust?**

This is exactly the question a sheaf is built to answer.

## The gluing condition

Write $s_U$ for $A$'s answer on $U$ and $s_V$ for $B$'s on $V$. A consistent
global decision exists precisely when the two agree on the overlap:

$$
s_U\big|_{U \cap V} \;=\; s_V\big|_{U \cap V}.
$$

When that holds, the sheaf axioms promise a *unique* section $s$ on
$U \cup V$ restricting to each local answer. When it fails, there is no honest
global decision — and pretending otherwise is where a lot of ensemble systems
quietly go wrong.

The useful move is to make disagreement a *measurable* quantity rather than a
silent failure. Define an overlap discrepancy

$$
\eta(U, V) \;=\; d\!\left(s_U\big|_{U\cap V},\; s_V\big|_{U\cap V}\right),
$$

for some metric $d$ on answers. If $\eta = 0$ everywhere, you can glue. If not,
$\eta$ tells you *where* and *how badly* your agents conflict.

## In code

A tiny sketch of the check, over a set of agents with named domains:

```python
from itertools import combinations

def overlap_discrepancy(agents, metric):
    """agents: dict name -> {"domain": set, "answer": callable(x)}"""
    report = {}
    for (na, a), (nb, b) in combinations(agents.items(), 2):
        overlap = a["domain"] & b["domain"]
        if not overlap:
            continue
        eta = max(metric(a["answer"](x), b["answer"](x)) for x in overlap)
        report[(na, nb)] = eta
    return report

def can_glue(report, tol=0.0):
    return all(eta <= tol for eta in report.values())
```

`can_glue` is deliberately strict. In practice you set a tolerance and treat
`overlap_discrepancy` as a diagnostic: the pairs with the largest $\eta$ are the
ones worth a human's attention before anything gets signed off.

## Why bother

Most multi-agent systems combine outputs by *averaging* or *voting*. Both hide
the one thing you most want to know in a high-stakes setting: whether the agents
actually agree where their knowledge overlaps. Sheaf-style gluing refuses to
average over a genuine contradiction — and gives you a number for how far from
consistent you are.

That's the whole pitch: **don't glue what doesn't agree, and measure the gap when
it doesn't.**
