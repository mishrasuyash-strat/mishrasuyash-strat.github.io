---
layout: post
title: "From long videos to clips people actually watch"
subtitle: "Turning clinical seminars and interviews into personalized highlight clips with audio and vision language models."
date: 2026-01-08 09:00:00 +0100
tags: [vlm, video, pharma]
reading: "2 min read"
---

A lot of valuable pharmaceutical content is locked inside long video and audio —
clinical-trial interviews, educational seminars — that nobody has time to watch
end to end, and annotating it by hand is slow and inconsistent.

We describe a domain-adapted video-to-clip pipeline that pairs audio language
models with vision language models to pull highlight clips out of long recordings.
Two pieces did most of the work: a reproducible Cut & Merge algorithm that handles
fade in/out, timestamp normalization, and audio-visual alignment so clips do not
feel stitched together; and a personalization step, driven by role definitions and
prompt injection, so the same source video yields different clips for different
audiences.

It is very much an engineering paper — built and measured on real content rather
than a toy benchmark.

Full paper on arXiv: [2601.05059](https://arxiv.org/abs/2601.05059).
