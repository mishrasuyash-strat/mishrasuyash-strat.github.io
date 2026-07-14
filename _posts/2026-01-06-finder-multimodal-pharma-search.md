---
layout: post
title: "One search box over everything"
subtitle: "Finder: multimodal, reasoning-aware retrieval across pharmaceutical text, images, audio, and video."
date: 2026-01-06
tags: [search, multimodal, retrieval]
reading: "2 min read"
---

Pharmaceutical knowledge is scattered across formats and buried in file systems —
regulatory filings, research reports, slide decks, images, audio, and video — and
traditional search struggles with most of it. Finder is a framework for searching
across those modalities from a single place.

It runs a hybrid vector search that combines sparse lexical matching with dense
semantic models, over a modular pipeline that ingests many formats, enriches
metadata, and stores everything in a vector-native backend. On top of that sits
reasoning-aware natural-language search, with hybrid fusion, chunking, and
metadata-aware routing across regulatory, research, and commercial content. In
deployment it has processed more than 291,000 documents, 31,000 videos, and over a
thousand audio files across 98 languages, reaching strong retrieval quality — mean
reciprocal rank around 0.90.

The point is less any single model and more the plumbing: making a large,
regulated, multimodal corpus genuinely findable.

Full paper on arXiv: [2603.15623](https://arxiv.org/abs/2603.15623).
