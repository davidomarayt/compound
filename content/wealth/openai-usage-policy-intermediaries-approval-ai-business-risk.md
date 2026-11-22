---
title: "OpenAI's New Model-Access Approval Rule: Which AI Businesses Need Permission?"
seo_title: "OpenAI Usage Policy November 2026: API Resellers and AI Business Risk"
slug: openai-usage-policy-intermediaries-approval-ai-business-risk
pillar: wealth
canonical_path: /wealth/openai-usage-policy-intermediaries-approval-ai-business-risk/
publication_status: published
date: '2026-11-22'
research_checked: '2026-11-22'
editorial_review_status: pending
summary: "OpenAI's 20 November usage-policy changes distinguish model-access intermediaries from ordinary applications and sharpen training and high-stakes rules. The commercial issue is how platforms control compliance without assuming every integration needs advance approval."
meta_description: "OpenAI's usage-policy update became effective 20 November 2026. What model-access intermediaries, AI app builders and enterprise buyers need to check."
tags: [wealth, private-company, company-research, company-openai, openai, api-platforms, ai-governance, developer-economics, compliance]
hero_image_url: https://upload.wikimedia.org/wikipedia/commons/d/d1/Open_AI_Forum_-_India_AI_Impact_Summit_2026.jpg
hero_image_alt: "A real February 2026 OpenAI Forum discussion at the India AI Impact Summit; archival photograph, not an image of the November policy change"
hero_image_credit: "Charlie4404 / Wikimedia Commons, CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/); photographed 20 February 2026, archival resized crop"
hero_image_source: https://commons.wikimedia.org/wiki/File:Open_AI_Forum_-_India_AI_Impact_Summit_2026.jpg
require_pinned_hero: true
image: /static/images/evergreen/openai-usage-policy-intermediaries-approval-ai-business-risk.jpg
social_image: /static/images/evergreen/openai-usage-policy-intermediaries-approval-ai-business-risk.jpg
image_alt: "Archival documentary photograph of an OpenAI-branded Forum panel in February 2026"
image_credit: "Charlie4404, CC BY-SA 4.0, Wikimedia Commons, February 2026; archival adapted crop"
image_source: https://commons.wikimedia.org/wiki/File:Open_AI_Forum_-_India_AI_Impact_Summit_2026.jpg
sources:
- title: "OpenAI — Usage policies effective 20 November 2026; update announced 21 October"
  url: https://openai.com/policies/usage-policies/
- title: "Wikimedia Commons — Charlie4404 OpenAI Forum photograph, CC BY-SA 4.0"
  url: https://commons.wikimedia.org/wiki/File:Open_AI_Forum_-_India_AI_Impact_Summit_2026.jpg
---

**The important business distinction in OpenAI's revised usage rules is between building a product *with* OpenAI models and selling other organisations direct *access* to those models.** For an AI software company, confusing those two cases can lead to unnecessary procurement friction—or an avoidable compliance problem.

OpenAI's [current Usage Policies](https://openai.com/policies/usage-policies/) took effect on **20 November 2026**. Their changelog dates the announcement to **21 October**, so this is an effective-date development rather than an unannounced policy issued on 22 November. The changes address model-training restrictions, high-stakes applications, children and teens, national-security uses and model-access intermediaries. The rules are OpenAI's contractual platform policy; they do not constitute legislation or a statement that every product will be legally permissible.

## The line between an application and an intermediary

The policy says a business operating a model-access intermediary service that enables third parties to **directly access OpenAI models** must obtain OpenAI's prior review and approval. It immediately clarifies that this requirement **does not apply solely because an application integrates OpenAI models to power its features or functionality**.

That sentence matters commercially. Consider two hypothetical services:

- A payroll application uses an OpenAI model behind the scenes to draft explanations of payslip entries. Customers interact with the payroll product, not a resold model endpoint. This alone is not the policy's stated trigger for intermediary preapproval.
- A developer platform offers other businesses a direct route to OpenAI models through its own gateway. The policy explicitly identifies this category as requiring prior review and approval.

Real services may combine these roles or use more complicated access arrangements. The examples illustrate the wording, **not a definitive classification or approval for any actual company**. Developers should document who controls prompts, authentication, model selection, billing and end-user access, then seek a determination from OpenAI where the boundary is unclear.

## The economics of a new approval dependency

An intermediary may make money by adding security, billing, monitoring, regional routing or customer support around model access. These conveniences can create real value, but the November rule makes upstream approval an explicit dependency for the category described.

That dependency can affect launch sequencing. A platform that signs customers before resolving model-access permissions could have to revise its architecture or contractual terms. On the other hand, an approved intermediary could use clearer operating arrangements to build trust with enterprise customers. **Neither result is a disclosed OpenAI revenue figure**: the company has not released application counts, approval times, intermediary fees or the commercial effect of this update.

The prudent operational approach is to document platform architecture, identify which party holds the OpenAI relationship and make any necessary provider approval a prelaunch condition—not an afterthought. This is a project-management recommendation, not a claim that all integrations require advance consent.

## Model training: a different type of restriction

The policy also prohibits using OpenAI models or outputs to create or supply training material or signals for models intended as **alternatives or substitutes** for OpenAI services, unless the applicable agreement expressly permits the use. Its examples include generating training tasks, reinforcement-learning environments, labels, preference scores and filtering trajectories. The restriction can apply even if the OpenAI customer is only preparing data for somebody else.

OpenAI separately says research, software development, model evaluation, benchmarking and product development remain permitted **within these boundaries**. Consequently, it would be inaccurate to claim that ordinary benchmarking is banned or that every use of generated text in software development amounts to prohibited model training.

For an enterprise contracting with several model vendors, the practical question is data provenance. Teams need to know whether evaluation outputs are being retained solely for product QA or routed into a competing model's training pipeline. Clear retention rules and access controls reduce ambiguity; they do not automatically grant exceptions to provider terms.

## Human review still matters in consequential workflows

Another material rule prohibits automation of high-stakes actions in sensitive areas **without human review**. OpenAI lists finance and credit, legal and medical services, housing, employment, education and other consequential settings. It also restricts offering tailored advice that requires professional licensing without appropriate licensed-professional involvement.

That is narrower than saying AI may never assist financial or medical work. A human-reviewed research summary is different from an unsupervised system that makes a credit decision or transmits a high-impact application. Organisations should map precisely which steps affect a person's rights or access to services, then assign accountable human decision-makers.

The company also says national-security, intelligence and law-enforcement use requires prior review and approval, while reserving case-by-case exceptions subject to safeguards. These provisions cannot be understood by reading only a product announcement; the current policy and applicable service agreement remain the controlling references.

## A hypothetical cost of governance

Suppose a fictional platform has 30 customer integrations and spends **two staff hours** reviewing the access architecture and data flows for each integration. At an illustrative fully loaded cost of **€60 per hour**, the initial review effort is **60 hours or €3,600**. If six complex integrations need an additional four hours each, the example rises to **84 hours or €5,040**.

These are invented staffing assumptions, not OpenAI charges, industry estimates or projected compliance costs. The exercise shows why a clear reusable classification checklist can be more efficient than improvising a new decision for every deal. It excludes legal advice, engineering changes and any wait for provider review.

## What buyers and investors should watch

OpenAI may benefit from partners that help businesses adopt its models, but a partner ecosystem must also prevent uncontrolled redistribution and unsafe downstream use. The trade-off is between developer distribution and the cost of enforcing an intelligible access boundary.

For purchasers, the key due-diligence questions are who provides access, which party handles abuse reports, whether high-stakes actions require review, how model-generated outputs are reused and what happens if upstream authorisation changes. A good contract and a recoverable architecture may be more important than a superficial model-price discount.

This is separate from our analysis of [OpenAI's enterprise procurement through AWS Marketplace](/wealth/openai-aws-marketplace-enterprise-procurement-economics/), which concerns purchasing, and the [Hacktron agent-security partnership](/wealth/openai-hacktron-agent-security-third-party-risk/), which concerns technical integration risk. Follow the [OpenAI private-company research profile](/companies/openai/) for future source-backed developments. OpenAI has no listed stock price in this directory.

*Sources checked 22 November 2026. The policy was announced on 21 October and took effect on 20 November; the analysis does not imply a new government law, an approved intermediary or a quantified revenue impact. Archival cover shows an actual OpenAI-branded February 2026 event, not the policy's issuance.*
