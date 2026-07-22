---
layout: post
title: "A calculus of discernment: what an insight is worth, and why forgetting is a skill"
subtitle: "Measuring decision-relevant insight, the value of a sequence of observations, and treating forgetting as higher-order learning."
date: 2026-07-21
tags: [decisions, information-theory, agents, foundations]
reading: "5 min read"
---

Two ideas have been bothering me for a while. The first: most systems that
"learn" treat every new piece of information as weakly positive — worth storing,
worth attending to. But in real decisions, only a fraction of what you learn
actually changes what you do. The rest is trivia that quietly raises your costs.
The second: we talk about *forgetting* as failure, as something to be minimized.
In practice, deciding what to drop is one of the most important things an agent
does.

This paper is my attempt to make both precise. I call it a calculus of
discernment.

## Decision-relevant insight

The starting move is to stop scoring information by how surprising or novel it is,
and start scoring it by whether it would change a decision. An observation that
shifts your chosen action — or your confidence in it — has value; one that leaves
the decision untouched, however interesting, does not. That reframing turns
"insight" from a vague compliment into something you can measure against a
downstream choice, which is the only place its value is ever actually realized.

## The value of a sequence

Insights rarely arrive alone, and they are not additive. The tenth data point on a
question you have already resolved is worth almost nothing; the single observation
that breaks a tie can be worth everything. So the object of interest is not an
isolated insight but the *value of a sequence* of them — how much a whole ordered
stream of observations moves your decisions, accounting for redundancy and order.
This is where the calculus earns its name: it gives you a way to compose and
compare sequences rather than points, which is much closer to how evidence
actually accumulates.

## Forgetting as higher-order learning

If value is decision-relative and sequences have diminishing returns, then
forgetting stops being loss and becomes an operation in its own right. Dropping
what no longer changes any decision is not damage — it is a second-order form of
learning: learning *what not to carry*. Done well, it keeps an agent's working
memory pointed at the few things that still move outcomes, instead of drowning in
everything it has ever seen. That is the sense in which forgetting is a skill
rather than a bug.

## Grounding it

I did not want this to be only a framework, so the paper includes a pre-registered
empirical study — 30 seeds, 100 iterations — together with a reference
implementation and a companion interactive demo. Pre-registering mattered to me:
it held the calculus to the predictions it makes *before* seeing the numbers,
rather than letting me fit a flattering story afterward.

It connects to a thread that runs through most of my work — making the reasoning
behind a decision legible and defensible, rather than assuming that more
information is always better. Sometimes the most rigorous thing a system can do is
decide what to ignore.

Full paper on arXiv: [2607.18275](https://arxiv.org/abs/2607.18275).
