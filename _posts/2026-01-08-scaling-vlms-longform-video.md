---
layout: post
title: "What breaks when the videos get long and the budget doesn't"
subtitle: "Benchmarking 40+ vision-language models for long-form pharmaceutical video under real GPU, latency, and cost limits."
date: 2026-01-08 10:00:00 +0100
tags: [vlm, video, benchmarks]
reading: "3 min read"
---

Most vision-language-model evaluations use short clips and quietly assume you have
all the GPUs you want. Neither holds in an industrial setting, where you are
processing long-form video under hard limits on compute, latency, and cost.

This paper reports what happened when we built a GenAI framework to do exactly
that at scale — over 200,000 PDFs, 25,326 videos across eight formats, and
hundreds of multilingual audio files in more than twenty languages. Alongside the
architecture, we ran an empirical comparison of more than forty VLMs on two public
benchmarks, Video-MME and MMBench, plus a proprietary set of videos spanning
fourteen disease areas.

Out of that came a handful of findings about what actually matters for long-form
video reasoning: where multimodality earns its keep, how attention behaves as
sequences grow, and the trade-offs you hit once resources are genuinely
constrained rather than assumed away.

Full paper on arXiv: [2601.04891](https://arxiv.org/abs/2601.04891).
