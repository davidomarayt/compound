---
title: "OpenAI Wants a Shared AI Capability Meter. Could It Change the Economics of the Model Race?"
seo_title: "OpenAI Perplexity Proposal: AI Safety Thresholds and Business Costs"
slug: openai-perplexity-ai-safety-thresholds-business-economics
pillar: wealth
canonical_path: /wealth/openai-perplexity-ai-safety-thresholds-business-economics/
publication_status: published
date: '2026-11-23'
research_checked: '2026-11-23'
editorial_review_status: pending
summary: "OpenAI's 22 November proposal would compare model pretraining progress using a common prediction-loss measure. The business question is whether credible capability thresholds can manage safety without distorting competition or investment."
meta_description: "OpenAI proposed cross-lab AI capability measurements on 22 November 2026. Examine the proposal's limits, competitive incentives and implications for enterprise customers."
tags: [wealth, private-company, company-research, company-openai, openai, ai-safety, model-evaluation, compute, enterprise-ai, regulation]
hero_image_url: https://upload.wikimedia.org/wikipedia/commons/f/f6/Jakub_Pachocki_in_2012.jpg
hero_image_alt: "OpenAI chief scientist Jakub Pachocki photographed at the 2012 ICPC World Finals in Warsaw; archival image, not his November 2026 announcement"
hero_image_credit: "Izabela Majewska / ICPCNews via Wikimedia Commons, CC BY 2.0 (https://creativecommons.org/licenses/by/2.0/); photographed 16 May 2012; archival cropped photograph"
hero_image_source: https://commons.wikimedia.org/wiki/File:Jakub_Pachocki_in_2012.jpg
require_pinned_hero: true
image: /static/images/evergreen/openai-perplexity-ai-safety-thresholds-business-economics.jpg
social_image: /static/images/evergreen/openai-perplexity-ai-safety-thresholds-business-economics.jpg
image_alt: "Archival 2012 documentary photograph of Jakub Pachocki, the author of OpenAI's 2026 perplexity proposal"
image_credit: "Izabela Majewska / ICPCNews, CC BY 2.0 via Wikimedia Commons; 2012 archival photograph, cropped"
image_source: https://commons.wikimedia.org/wiki/File:Jakub_Pachocki_in_2012.jpg
sources:
- title: "OpenAI chief scientist Jakub Pachocki — Perplexity and Intelligence, 22 November 2026"
  url: https://openai.com/index/perplexity-and-intelligence/
- title: "Reuters — OpenAI scientist proposes cross-industry AI development limits, 22 November 2026"
  url: https://www.reuters.com/business/openai-scientist-proposes-industry-ai-limits-tied-model-intelligence-metric-2026-11-22/
- title: "Wikimedia Commons — Jakub Pachocki at ICPC 2012, Izabela Majewska / ICPCNews, CC BY 2.0"
  url: https://commons.wikimedia.org/wiki/File:Jakub_Pachocki_in_2012.jpg
---

**OpenAI is proposing a shared way to measure how powerful AI models are becoming. The financial question is not whether a new number will predict every capability. It is whether an agreed measurement could change when laboratories spend billions training larger models—and what assurances enterprise buyers can reasonably demand.**

On **22 November 2026**, OpenAI chief scientist Jakub Pachocki published [“Perplexity and Intelligence”](https://openai.com/index/perplexity-and-intelligence/). He argued that laboratories should compare progress on pretraining prediction accuracy, using a common benchmark, and develop safety measures around the pace of that progress. Reuters [reported the proposal on the same date](https://www.reuters.com/business/openai-scientist-proposes-industry-ai-limits-tied-model-intelligence-metric-2026-11-22/).

This is **a proposal from one company's scientist**, not an agreed industry pact, enacted law, binding development cap or announcement that OpenAI has stopped training models. Neither the paper nor the reporting establishes a timetable for adoption by competitors.

## What the proposed measurement actually captures

A language model predicts tokens. A held-out evaluation set—material not used to train the model—can test how well it predicts text it has not seen. Cross-entropy loss, closely related to perplexity, summarises the error. **Lower loss ordinarily means better prediction on that specific dataset.**

Pachocki points to OpenAI's own measurements: approximately **0.99 for GPT-3.5** and **0.91 for GPT-4** on its current evaluation corpus. He says progress below 0.8 has coincided with important advances in areas including mathematics and cybersecurity. Those figures are **company-reported internal measurements**, not an independently verified league table of every rival model.

The attraction is simplicity. Instead of debating each new benchmark when a model launches, laboratories might compare a common, pre-agreed metric. That could help safety teams decide when deeper evaluations, independent audits or additional deployment precautions become necessary.

But the metric is not identical to general intelligence. A score changes with the test data, tokenizer, distribution and evaluation method. Training-phase prediction quality can also miss capability gains created later by tools, reinforcement learning, longer reasoning or specialised fine-tuning.

## Why a common threshold is a commercial decision

Training investment depends partly on expected performance gains. If a voluntary threshold required extra safety work before a model can be deployed, the threshold could add time and operating costs to the development schedule.

That need not be bad business. A credible release process could reduce the expected cost of preventable incidents and make procurement easier for customers subject to security or regulatory scrutiny. The same process could hurt a smaller laboratory if evidence collection and independent evaluation are expensive fixed costs.

The economic trade-off is therefore asymmetric. Large firms with established evaluation teams might absorb a new requirement more easily than firms trying to compete with a narrow set of models. Conversely, smaller firms could benefit from a common standard that makes safety claims comparable without requiring customers to trust marketing.

Competition matters too. A laboratory has an incentive to disclose enough to influence shared standards, but not enough to reveal every research advantage. Pachocki acknowledges that publishing OpenAI's own measurements tells competitors something about its progress. An agreement would require compatible data, good-faith participation and safeguards against selective reporting.

## A transparent worked example of the cost, not a forecast

Consider a hypothetical laboratory evaluating two launch approaches:

| Illustrative assumption | Faster release | Extra safety gate |
|---|---:|---:|
| Evaluation staff | 12 people | 18 people |
| Fully loaded monthly cost per person | €15,000 | €15,000 |
| Extra work before deployment | None | 2 months |
| **Incremental staffing cost** | **€0** | **€540,000** |

The extra €540,000 is **6 additional people × €15,000 × 2 months, plus the original 12-person team's two months of additional work?** No: only comparing the staffing uplift would be €180,000. A complete two-month postponement with all 18 people costs €540,000 gross, but it is not necessarily all *incremental* to an existing budget. This distinction is central to evaluating any proposed pause.

For a more directly comparable scenario, **six incremental evaluation specialists employed for two months at €15,000 monthly cost create €180,000 in additional staffing expense**. That excludes compute, external audits, delayed revenue, avoided failures and the work those specialists might otherwise perform. It is a hypothetical sensitivity calculation, not OpenAI spending guidance.

A real economic assessment would also ask whether a later launch improves reliability enough to reduce refund costs, operational interruptions or the number of human reviewers customers need. Without those numbers, there is no defensible single “cost of AI safety” estimate.

## What buyers and investors should verify

Enterprise purchasers should avoid treating a low perplexity figure as proof that a model can autonomously handle sensitive workflows. Relevant evidence includes task-specific failure rates, security tests, incident reporting, the ability to revoke access and human controls over high-impact actions.

Investors assessing [OpenAI's private-company research profile](/companies/openai/) should distinguish an internal research proposal from a binding commitment that changes spending or revenue projections. There are no new independently verified company-level revenue, profit or valuation figures in this announcement.

The existing [analysis of OpenAI's model-access policy](/wealth/openai-usage-policy-intermediaries-approval-ai-business-risk/) covers current service restrictions, a different matter from this voluntary cross-lab measurement idea. Its [Astra model launch analysis](/news/openai-gpt-6-2-astra-sol-pricing-performance-2026/) addresses consumer-facing prices and performance, which cannot be inferred from the research metric alone.

## The test for a useful common standard

A workable system would need publicly specified evaluation methods, controlled test-data access, reporting that other laboratories could reproduce, and governance that prevents a company from unilaterally declaring itself compliant. It would also need to define what happens when models improve through techniques that do not materially change the chosen pretraining score.

That is the larger business question prompted by 22 November's research: **could the model industry agree on a measurement that makes safety obligations more credible without locking in today's leading companies?** The primary source makes the intellectual case for a shared measure. Whether rivals adopt it—and whether it changes research budgets or enterprise buying decisions—remains unverified.

*Compound Research analysis, 23 November 2026. This is not investment advice. Company-supplied model results and the hypothetical cost example are explicitly labelled; no industry agreement or new regulation is claimed.*
