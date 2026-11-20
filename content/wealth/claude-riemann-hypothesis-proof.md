---
title: "Did Claude Solve the Riemann Hypothesis? What the Proof Claim Says"
seo_title: "Did Claude Solve the Riemann Hypothesis? What We Know"
slug: claude-riemann-hypothesis-proof
canonical_path: /news/claude-riemann-hypothesis-proof/
pillar: wealth
draft: false
publication_status: published
date: '2026-11-20'
research_checked: '2026-11-20'
editorial_review_status: pending
summary: "Anthropic mathematician Levent Alpöge says he found a proof with Claude. Here’s what he released and what independent experts still need to check."
meta_description: "Anthropic’s Levent Alpöge claims a Claude-assisted proof of the Riemann hypothesis. What the Lean release shows, what remains unverified and how the $1m prize works."
tags:
- news
- technology
- artificial-intelligence
- anthropic
- company-anthropic
- mathematics
image: /static/images/news/claude-riemann-hypothesis-proof.jpg
social_image: /static/images/news/claude-riemann-hypothesis-proof.jpg
image_alt: Archival photograph of mathematician Bernhard Riemann wearing glasses in 1863.
image_credit: "Unidentified photographer, 1863. Smithsonian Libraries via Wikimedia Commons. No known copyright restrictions. Cropped for publication."
image_source: https://commons.wikimedia.org/wiki/File:Portrait_of_Bernhard_Riemann_(1826-1866),_Mathematician_(2551069295).jpg
require_pinned_hero: true
sources:
- title: "Levent Alpöge — personal note and links to the Lean release"
  url: https://alpo.ge/remark.pdf
- title: "Clay Mathematics Institute — Riemann hypothesis and current status"
  url: https://www.claymath.org/millennium/riemann-hypothesis/
- title: "Clay Mathematics Institute — Millennium Prize rules"
  url: https://www.claymath.org/millennium-problems/rules/
- title: "Anthropic — August 2026 research on the Riemann zeta function"
  url: https://www.anthropic.com/research/riemann-zeta
- title: "The Verge — independent reporting on the proof claim"
  url: https://www.theverge.com/ai-artificial-intelligence/1010051/anthropic-riemann-hypothesis-millennium-prize-problem
---
Anthropic mathematician Levent Alpöge says he and Claude have found a proof of the Riemann hypothesis, a problem about the distribution of prime numbers that dates to 1859. In a note on his personal website on 20 November 2026, Alpöge also claims the argument proves the Generalized Riemann Hypothesis. As of publication, we found no public independent verification of the full proof, and the Clay Mathematics Institute still lists the original problem as unsolved. [Alpöge’s note](https://alpo.ge/remark.pdf) · [Clay Mathematics Institute](https://www.claymath.org/millennium/riemann-hypothesis/) · [The Verge](https://www.theverge.com/ai-artificial-intelligence/1010051/anthropic-riemann-hypothesis-millennium-prize-problem)

## What did Claude do?

Alpöge describes a collaboration. He says he steered the work towards an analogy with a simpler setting and credits Claude with suggesting a crucial step near the end. The note links to a 14-part archive of the proposed proof in Lean, software that checks formal mathematical arguments. The release includes the short note and the code, with a conventional exposition still to come. [Alpöge’s note](https://alpo.ge/remark.pdf)

## What is the Riemann hypothesis?

The prime number theorem describes how common primes are on average as numbers grow larger. The Riemann hypothesis concerns how far the actual count of primes can stray from that estimate. Bernhard Riemann linked those fluctuations to the places where a function called the Riemann zeta function equals zero. His conjecture says that every *non-trivial* zero lies on the same vertical line in the complex plane, where the real part is exactly ½.

Checking individual zeros can test the conjecture as far as the computation goes. A proof has to account for all of them, however far out they lie. The generalised version extends the corresponding claim to a family of related functions called Dirichlet L-functions. [Clay Mathematics Institute](https://www.claymath.org/millennium/riemann-hypothesis/) · [Alpöge’s note](https://alpo.ge/remark.pdf)

## How can mathematicians verify the Lean proof?

For an independent check, researchers need to reproduce the build and inspect exactly what the code proves. Lean checks a formal statement against its definitions and assumptions. Reviewers therefore need to confirm that the final theorem expresses the standard Riemann hypothesis and that its proof requires no unproved mathematical assumptions. The same checks apply separately to the claimed generalised result. A readable exposition would help specialists understand the argument and see which ideas might carry over to other problems. [Alpöge’s note](https://alpo.ge/remark.pdf)

## How does this compare with Claude’s August result?

In August, Anthropic reported that a research version of Claude raised the proven lower bound for the proportion of non-trivial zeros on the critical line from 41.6% to 67.2%. That was a guarantee about a share of the zeros and left open whether any lie elsewhere. The November claim is that every non-trivial zero lies on the line. [Anthropic’s August research](https://www.anthropic.com/research/riemann-zeta) · [Alpöge’s note](https://alpo.ge/remark.pdf)

## Has anyone won the $1 million prize?

Clay still lists the prize problem as unsolved. Before the institute considers a proposed solution, its rules require publication in a qualifying outlet, at least two years to pass after that publication, and broad acceptance by the international mathematics community. An independently reproduced Lean verification would be important evidence for the claim, while the prize follows Clay’s separate process. [Millennium Prize rules](https://www.claymath.org/millennium-problems/rules/)

## Why Anthropic investors are following the claim

The note appeared one day after Anthropic began trading on Nasdaq under the ticker ANT. If the result holds up, it would show Claude contributing to original research at the frontier of mathematics. The commercial questions are how often researchers can reproduce that kind of progress, what it costs in time and computing power, and whether research teams will pay for it at scale. [Anthropic’s Nasdaq debut and lock-up schedule](/news/anthropic-ipo-lockup-release-schedule/)
