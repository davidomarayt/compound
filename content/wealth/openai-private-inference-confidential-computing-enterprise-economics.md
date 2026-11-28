---
title: "OpenAI's Private Inference Test: Why Business Privacy Is Becoming a Hardware-Capacity Product"
seo_title: "OpenAI Private Inference: What the Alpha Covers and Costs"
slug: "openai-private-inference-confidential-computing-enterprise-economics"
pillar: "wealth"
canonical_path: "/wealth/openai-private-inference-confidential-computing-enterprise-economics/"
publication_status: "published"
draft: false
date: "2026-11-28"
research_checked: "2026-11-28"
editorial_review_status: "pending"
author: "Compound Research"
summary: "OpenAI has begun testing Private Inference, which runs work on sealed-off confidential-computing hardware. Its own white paper shows a narrower scope than the headline, and the rollout depends on capacity OpenAI is still securing."
meta_description: "OpenAI is testing Private Inference with a small group of business customers. We compare the product page with OpenAI's own white paper and explain why capacity, not code, sets the pace."
tags: ["wealth", "private-company", "company-research", "company-openai", "openai", "artificial-intelligence", "enterprise-software", "data-privacy"]
hero_image_url: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/NVIDIA_H100_%28%E6%9E%81%E5%AE%A2%E6%B9%BEGeekerwan%29_004.png/1280px-NVIDIA_H100_%28%E6%9E%81%E5%AE%A2%E6%B9%BEGeekerwan%29_004.png"
hero_image_alt: "Four NVIDIA H100 data-centre accelerator cards lined up on a marble surface in June 2023; archival photograph of the class of AI hardware used for confidential computing, not OpenAI's own servers."
hero_image_credit: "极客湾Geekerwan via Wikimedia Commons, CC BY 3.0 (https://creativecommons.org/licenses/by/3.0/), 14 June 2023; resized/cropped."
hero_image_source: "https://commons.wikimedia.org/wiki/File:NVIDIA_H100_(%E6%9E%81%E5%AE%A2%E6%B9%BEGeekerwan)_004.png"
require_pinned_hero: true
image: "/static/images/evergreen/openai-private-inference-confidential-computing-enterprise-economics.jpg"
social_image: "/static/images/evergreen/openai-private-inference-confidential-computing-enterprise-economics.jpg"
image_alt: "Four NVIDIA H100 data-centre accelerator cards lined up on a marble surface in June 2023; archival photograph of the class of AI hardware used for confidential computing, not OpenAI's own servers."
image_credit: "极客湾Geekerwan via Wikimedia Commons, CC BY 3.0 (https://creativecommons.org/licenses/by/3.0/), 14 June 2023; resized/cropped."
image_source: "https://commons.wikimedia.org/wiki/File:NVIDIA_H100_(%E6%9E%81%E5%AE%A2%E6%B9%BEGeekerwan)_004.png"
sources: [{"title": "OpenAI — Private Intelligence (business privacy page)", "url": "https://openai.com/business/private-intelligence/"}, {"title": "OpenAI — Private Safety Processing technical white paper, 26 October 2026", "url": "https://openaiassets.blob.core.windows.net/%24web/pdf/c7284810-2252-462f-803e-075b0c95bccb/psp-whitepaper.pdf"}, {"title": "Computing.net — OpenAI Tests Private Inference as Customers Take Custody of Safety Records, 26 November 2026", "url": "https://computing.net/openai-tests-private-inference-as-customers-take-custody-of-safety-records/"}, {"title": "i10X News — OpenAI Tests Private Inference: What It Shields, and What It Still Does Not, 26 November 2026", "url": "https://i10x.ai/news/openai-private-inference-alpha-confidential-computing-what-it-covers"}, {"title": "Wikimedia Commons — archival photo, CC BY 3.0", "url": "https://commons.wikimedia.org/wiki/File:NVIDIA_H100_(%E6%9E%81%E5%AE%A2%E6%B9%BEGeekerwan)_004.png"}]
---

The most valuable work a business could hand to an AI model is often the work it is least willing to send: draft deal terms, patient records, unreleased results, source code. OpenAI's latest privacy step is aimed squarely at that reluctance. It is also a reminder that, in AI, privacy is starting to behave like a compute product with its own supply constraint.

On Wednesday 25 November, chief executive Sam Altman said on X that OpenAI had started testing **Private Inference** with a small group of business customers, as reported by [Computing.net](https://computing.net/openai-tests-private-inference-as-customers-take-custody-of-safety-records/) and others. OpenAI's [Private Intelligence page](https://openai.com/business/private-intelligence/) lists it as "Alpha" and describes it as combining "confidential computing with strict controls designed to protect your prompts and responses while the model processes them".

## What confidential computing changes

Most enterprise AI privacy promises so far have been about what happens *after* a request. OpenAI's Zero Data Retention (ZDR), for eligible API workflows, means prompts and responses are not kept once processing finishes. That answers a storage question. It does not change the fact that, while the model is working, the data is readable in memory on the provider's servers.

Confidential computing targets that gap. OpenAI's [Private Safety Processing white paper](https://openaiassets.blob.core.windows.net/%24web/pdf/c7284810-2252-462f-803e-075b0c95bccb/psp-whitepaper.pdf), published on 26 October 2026, explains the mechanism: software runs inside a hardware-backed trusted execution environment that isolates protected memory from the rest of the infrastructure, "including human access". Keys to decrypt customer content are released only after the environment proves, through hardware attestation, that it is running approved software.

In plain terms, the promise moves from "we will not look" towards "our systems are built so that operators cannot look".

## The scope is narrower than the headline

Reading the product page alongside the white paper is instructive.

- **The product page** says Private Inference protects prompts and responses "while the model processes them" and labels it an "API Preview" in its request diagram.
- **The white paper** is more cautious. It describes Private Inference as "an optional protection that extends operator access protections and attestation to eligible safety-inference workloads", and says it "does not automatically cover the initial API request" or "every OpenAI system".
- In its planned-enhancements section, the paper says OpenAI expects to extend confidential computing "beyond the protected safety-inference stack when necessary technology, capacity, and product commitments are met".
- It also says the paper covers first-party OpenAI traffic only: "Amazon Bedrock and other third-party distribution arrangements are outside its scope."

The alpha may already go further than the October document; Altman's post and the product page suggest that is the direction. But OpenAI has not published alpha documentation, supported models, regions, prices or a general-availability date. Until it does, a buyer should assume protection covers what OpenAI has put in writing, and no more.

## Why capacity is the real constraint

The interesting economic detail is the phrase "capacity" in OpenAI's own text. According to reports of the announcement, the OpenAI lead for the work, Shekar, called the test a first step and said the company is lining up confidential-compute capacity for a much larger rollout, without giving a date.

That matters for three reasons.

**It is not a software toggle.** Confidential inference needs accelerators and servers configured for trusted execution, attestation services and key-release infrastructure. Every request served that way needs capacity drawn from that pool, which competes with OpenAI's other demands for compute.

**It segments the customer base.** If confidential capacity is scarce, OpenAI has to decide who gets it first. The obvious candidates are the customers for whom privacy is a gating requirement rather than a preference: banks, insurers, healthcare providers, law firms and public bodies. Those are also the buyers with the largest contracts that AI vendors have found hardest to win for sensitive workloads.

**It creates a pricing question OpenAI has not answered.** No price has been disclosed. If confidential inference costs more to run, OpenAI could charge a premium, fold it into enterprise contracts or absorb it to win deals. Each choice says something different about how it values regulated-industry revenue. Compound would not assume any of them until OpenAI publishes terms.

## Customers are taking custody of the safety records

The other half of OpenAI's privacy package moves work onto the customer's own infrastructure. Under ZDR with Private Safety Processing, the white paper says content selected for asynchronous safety review is encrypted and written to a storage container the customer controls, and that customers configure that storage "to retain the encrypted data for at least 30 days". OpenAI keeps only an index entry with operational metadata and a storage reference, which is deleted after 30 days, and its ability to decrypt the content expires after the same period.

That design reduces what OpenAI holds. It also hands customers an operational job: provisioning regional cloud storage, managing access and keeping records for the minimum period. If encryption, storage authorisation or regional checks fail, the white paper says the write is blocked. For a large enterprise with a security team, that is a reasonable trade. For a small business, it is cost and complexity that ZDR alone did not require.

The white paper is also candid about an open gap: PSP "currently does not impose a limit on the total information disclosed across repeated reviews of the same content", although access is logged. OpenAI says it expects to add limits.

## The competitive picture

OpenAI is not alone. On 23 November, Anthropic opened its Enterprise Frontier Safeguards to business users in beta, which we covered in [who pays for private AI monitoring](/wealth/anthropic-enterprise-frontier-safeguards-monitoring-costs/). Both companies are converging on the same idea: keep customer content in customer-controlled storage, and let automated, attested systems rather than people do the safety review.

The difference OpenAI is reaching for with Private Inference is protection during processing itself. The vendor that can prove that, in a way a customer's own software can verify before sending data rather than through an audit report afterwards, will have a strong argument in regulated procurement. As far as published documents show, that verification step is not yet available to customers directly.

## What to watch

- Alpha documentation: whether Private Inference covers the main model call or mainly safety inference, and which models and regions it supports.
- Price: whether confidential inference carries a premium over standard API rates.
- Capacity and timing: any date for broader availability, which will indicate how quickly OpenAI can secure trusted-execution hardware.
- Customer-side attestation: whether customers can verify the environment themselves.

For OpenAI's wider business picture, see the [OpenAI company research profile](/companies/openai/) and our recent coverage of [ChatGPT's shared usage meter](/wealth/openai-chatgpt-shared-usage-allowance-codex-metering-economics/).

*Compound Research; research checked 28 November 2026. Product and architecture details are from OpenAI's Private Intelligence page and its 26 October 2026 white paper. Altman's and Shekar's remarks are as reported by Computing.net and i10X News; Compound did not independently verify the posts. OpenAI is privately held; no valuation, price or launch date is implied. This is not investment advice.*

## Source record
- https://openai.com/business/private-intelligence/
- https://openaiassets.blob.core.windows.net/%24web/pdf/c7284810-2252-462f-803e-075b0c95bccb/psp-whitepaper.pdf
- https://computing.net/openai-tests-private-inference-as-customers-take-custody-of-safety-records/
- https://i10x.ai/news/openai-private-inference-alpha-confidential-computing-what-it-covers
