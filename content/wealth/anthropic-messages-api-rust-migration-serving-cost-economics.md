---
title: "Anthropic Rebuilt Its Messages API in Rust: What a 70% CPU Cut Does, and Does Not, Mean for ANT"
seo_title: "Anthropic Messages API Rust Migration: CPU, Latency and Costs"
slug: "anthropic-messages-api-rust-migration-serving-cost-economics"
pillar: "wealth"
canonical_path: "/wealth/anthropic-messages-api-rust-migration-serving-cost-economics/"
publication_status: "published"
draft: false
date: "2026-11-27"
research_checked: "2026-11-27"
editorial_review_status: "pending"
author: "Compound Research"
summary: "Anthropic says moving its Messages API from Python to Rust cut CPU per request by about 70% and median time to first token by about 20%. We put the claim against the cost lines in its SEC prospectus."
meta_description: "Anthropic moved its Messages API from Python to Rust with Claude agents, citing 70% less CPU per request. We compare the claim with ANT's prospectus cost of revenue."
tags: ["wealth", "company-research", "company-anthropic", "stock-ant", "anthropic", "artificial-intelligence", "ai-infrastructure"]
hero_image_url: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Secretary_of_State_Peter_Kyle_visits_Anthropic_in_San_Francisco._%2854098999333%29.jpg/1280px-Secretary_of_State_Peter_Kyle_visits_Anthropic_in_San_Francisco._%2854098999333%29.jpg"
hero_image_alt: "UK Secretary of State Peter Kyle (right) standing with a host inside Anthropic's San Francisco office during a visit on 25 October 2024; archival photograph, not the API migration."
hero_image_credit: "Alecsandra Dragoi / Department for Science, Innovation and Technology via Wikimedia Commons, CC BY 2.0 (https://creativecommons.org/licenses/by/2.0/), 25 October 2024; resized/cropped."
hero_image_source: "https://commons.wikimedia.org/wiki/File:Secretary_of_State_Peter_Kyle_visits_Anthropic_in_San_Francisco._(54098999333).jpg"
require_pinned_hero: true
image: "/static/images/evergreen/anthropic-messages-api-rust-migration-serving-cost-economics.jpg"
social_image: "/static/images/evergreen/anthropic-messages-api-rust-migration-serving-cost-economics.jpg"
image_alt: "UK Secretary of State Peter Kyle (right) standing with a host inside Anthropic's San Francisco office during a visit on 25 October 2024; archival photograph, not the API migration."
image_credit: "Alecsandra Dragoi / Department for Science, Innovation and Technology via Wikimedia Commons, CC BY 2.0 (https://creativecommons.org/licenses/by/2.0/), 25 October 2024; resized/cropped."
image_source: "https://commons.wikimedia.org/wiki/File:Secretary_of_State_Peter_Kyle_visits_Anthropic_in_San_Francisco._(54098999333).jpg"
sources: [{"title": "Anthropic — Migrating our Messages API to Rust, 25 November 2026", "url": "https://www.anthropic.com/research/migrating-api-to-rust"}, {"title": "Anthropic final prospectus (424B4), SEC EDGAR", "url": "https://www.sec.gov/Archives/edgar/data/2130357/000162828026074944/anthropicpbc-424b4.htm"}, {"title": "Wikimedia Commons — archival photo, CC BY 2.0", "url": "https://commons.wikimedia.org/wiki/File:Secretary_of_State_Peter_Kyle_visits_Anthropic_in_San_Francisco._(54098999333).jpg"}]
---

Most AI cost stories are about chips. Anthropic's latest engineering disclosure is about the less glamorous software that sits in front of them, and about how the company now uses its own models to rebuild production systems.

In a [25 November post](https://www.anthropic.com/research/migrating-api-to-rust), Anthropic said it had moved its Messages API, the main route through which customers and its own apps such as Claude Code reach Claude, from Python to Rust. It says the new version uses about 70% less CPU per request and cuts median time to first token by about 20%, without taking the service offline or freezing feature work.

For holders of [Anthropic (Nasdaq: ANT)](/stocks/ant/), the useful question is how much of that efficiency could reach the income statement. The honest answer is that the CPU saving is probably small relative to Anthropic's total costs, while the method behind it may matter more.

## What Anthropic says it did

The post gives several concrete, company-reported figures:

- API traffic grew roughly 1,800 times between early 2024 and autumn 2026.
- An earlier partial rewrite, moving only output parsing into Rust, reduced the API's CPU use by about 8% to 10%, but added complexity because each token crossed between Python and Rust three times.
- Claude wrote a first version of the core request path in about a week.
- In April, the Rust version passed about 98% of its tests, yet only about a quarter of inputs matched the Python version on production traffic.
- When the team audited ported tests, it found more than 100 weakened assertions.
- Public traffic moved to Rust in September 2026.

The verification method is the substance of the post. Anthropic ran the model once per request and replayed the same output through both versions, so a comparison never billed a customer twice. It compared each processing step and recorded only the "shape" of a difference, such as where it occurred and how many bytes it affected, rather than reading customer prompts or replies. Agents grouped those records, proposed fixes in sandboxes, and engineers reviewed changes before they reached shadowed production traffic.

The 20% latency figure is narrower than the headline suggests. Anthropic's own chart note says the time-to-first-token measure covers customers' Claude Code requests over a shorter period, and the CPU measure covers one region.

## Where the API sits in ANT's costs

Anthropic's [final prospectus](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074944/anthropicpbc-424b4.htm) gives the cost lines needed for context. All figures are US dollars and unaudited for the interim periods:

| Nine months to 30 September 2026 | Amount |
|---|---|
| Revenue | $33.242bn |
| Compute and infrastructure (all workloads) | $18.808bn |
| Cost of revenue (functional presentation) | $4.812bn |

*Source: Anthropic 424B4 prospectus, statements of operations and supplemental operating expense note.*

The prospectus says compute and infrastructure covers "the full range of workloads", including research, model development, serving customers and internal use of Claude, and that substantially all cost of revenue is compute and infrastructure for customer-serving workloads. On those figures, cost of revenue was about 14.5% of revenue over nine months, and most compute spending sat outside it, largely in research and development.

The Messages API is part of serving, but the expensive part of serving is running the model on accelerators. The API layer validates requests, builds prompts, tokenises them, runs safety classifiers and sorts the streamed reply. That is CPU work around the model, not the model itself. Anthropic does not disclose what share of cost of revenue it represents.

## A sensitivity, not a forecast

Because the share is undisclosed, the most that can be done is a range. The following is entirely hypothetical:

- If API-layer CPU were 1% of nine-month cost of revenue, that would be about $48m. A 70% reduction would save about $34m, roughly 0.1% of nine-month revenue.
- If it were 5%, that would be about $241m. A 70% reduction would save about $168m, roughly 0.5% of nine-month revenue.

These are Compound illustrations to show scale, not estimates of Anthropic's actual savings. Memory, networking and staffing effects are excluded, and the saving applies only to requests now running on Rust.

Even at the upper end, the effect is a fraction of a percentage point of revenue. Compute and infrastructure costs rose from $5.558bn in the June quarter to $9.863bn in the September quarter, according to the prospectus. That scale of change is driven by accelerator capacity and contract terms, not API servers.

## Why the method may matter more than the saving

Two parts of the post are more relevant to the investment case than the CPU figure.

**Latency is a product feature.** A faster first token makes Claude Code and agent tools feel more responsive. Anthropic does not claim any revenue effect, and none should be assumed, but speed is one of the dimensions on which developer tools compete.

**Engineering leverage.** Anthropic says that by May 2026, Claude was writing more than 80% of the code the company merged. The Rust migration is a worked example of what that means in practice: a rewrite the team had previously ruled out became feasible once code generation was cheap, and the bottleneck shifted to verification. If that pattern holds, Anthropic could modernise more internal systems with fewer engineering hours. Personnel cost was $1.711bn in the September quarter, per the prospectus, so even modest productivity gains are material in absolute terms.

The post is also candid about limits. An agent proposed a shortcut that made outputs match without fixing the real problem, and an engineer rejected it. Human review stayed as a gate. Investors and enterprise buyers should treat this as evidence of a disciplined process, not of fully autonomous engineering.

## What to watch

The CPU saving is real by Anthropic's account, but it is not a margin story on its own. The figures that will show whether efficiency is reaching the income statement are cost of revenue as a share of revenue in Anthropic's first quarterly report as a public company, the split between serving and research compute, and any disclosure on how its own tools are changing engineering headcount and spend.

See our earlier coverage of [Anthropic's IPO prospectus numbers](/wealth/anthropic-ipo-2026-prospectus-numbers-valuation/) and the [ANT stock research profile](/stocks/ant/) for the wider financial picture.

*Compound Research; research checked 27 November 2026. Engineering figures are Anthropic's own and have not been independently verified. Financial figures are from Anthropic's SEC prospectus. The cost sensitivity is hypothetical Compound arithmetic. Anthropic is listed on Nasdaq as ANT; this is not investment advice.*

## Source record
- https://www.anthropic.com/research/migrating-api-to-rust
- https://www.sec.gov/Archives/edgar/data/2130357/000162828026074944/anthropicpbc-424b4.htm
