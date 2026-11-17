---
title: "Anthropic's Self-Hosted Agents Shift the Security Boundary—and the Operating Bill"
seo_title: "Anthropic Self-Hosted Managed Agents: Security, Costs and Private Beta"
slug: anthropic-self-hosted-managed-agents-enterprise-control-economics
pillar: wealth
canonical_path: /wealth/anthropic-self-hosted-managed-agents-enterprise-control-economics/
publication_status: published
date: '2026-11-17'
research_checked: '2026-11-17'
editorial_review_status: pending
summary: "Anthropic's 12 November private beta lets enterprises run the Managed Agents control plane in their own environment. Local credentials and session history change security responsibility, not the need for model processing or operational discipline."
meta_description: "Claude self-hosted Managed Agents launched in private beta on 12 November 2026. Compare control-plane ownership, model routes, credentials, observability and operating costs."
tags: [wealth, private-company, company-research, company-anthropic, anthropic, enterprise-ai, agent-security, self-hosted, cloud]
hero_image_url: https://upload.wikimedia.org/wikipedia/commons/d/df/Dario_Amodei_at_TechCrunch_Disrupt_2023_03.jpg
hero_image_alt: "Anthropic CEO Dario Amodei speaking at TechCrunch Disrupt in September 2023; archival company photograph unrelated to the November 2026 product beta"
hero_image_credit: "TechCrunch / Kimberly White, Wikimedia Commons; CC BY 2.0 (https://creativecommons.org/licenses/by/2.0/), 20 September 2023, adapted archival crop"
hero_image_source: https://commons.wikimedia.org/wiki/File:Dario_Amodei_at_TechCrunch_Disrupt_2023_03.jpg
require_pinned_hero: true
image: /static/images/evergreen/anthropic-self-hosted-managed-agents-enterprise-control-economics.jpg
social_image: /static/images/evergreen/anthropic-self-hosted-managed-agents-enterprise-control-economics.jpg
image_alt: "Anthropic CEO Dario Amodei at TechCrunch Disrupt in September 2023, archival"
image_credit: "TechCrunch / Kimberly White, Wikimedia Commons; CC BY 2.0 (https://creativecommons.org/licenses/by/2.0/), adapted crop"
image_source: https://commons.wikimedia.org/wiki/File:Dario_Amodei_at_TechCrunch_Disrupt_2023_03.jpg
sources:
- title: "Anthropic — Operate Claude Managed Agents inside your security perimeter, 12 November 2026"
  url: https://claude.com/resources/articles/self-hosted-claude-managed-agents
- title: "Anthropic — Building always-on agents, 13 November 2026"
  url: https://claude.com/resources/articles/building-always-on-agents
- title: "Wikimedia Commons — TechCrunch documentary Dario Amodei photograph, CC BY 2.0"
  url: https://commons.wikimedia.org/wiki/File:Dario_Amodei_at_TechCrunch_Disrupt_2023_03.jpg
---

**Who holds the agent's credentials, logs and execution environment can matter more to a regulated buyer than who provides the language model.** Anthropic's new self-hosted Managed Agents option turns that security question into a product decision—and transfers a substantial operational burden back to the customer.

On **12 November 2026**, Anthropic [introduced self-hosted Claude Managed Agents in private beta](https://claude.com/resources/articles/self-hosted-claude-managed-agents). Customers can operate the agent service in their own cloud or on-premises environment, including its harness, sandbox workers, database, credentials and session history. Model requests can be directed to Anthropic, a supported cloud provider or an organisation's own gateway.

This is a meaningful distinction from Anthropic's original fully hosted Managed Agents service and its intermediate self-hosted-sandbox arrangement. **It is not a statement that Claude's underlying model necessarily runs on-premises**, or that every organisation can already sign up: access is by request during the private beta.

## Three architectures solve different buyer problems

In the hosted approach, Anthropic operates the agent infrastructure. The customer concentrates on workflow design, authorisation and evaluating results, with fewer platform components to run.

With a self-hosted *sandbox only*, sensitive code execution stays in the customer's environment, but the rest of the agent control plane is still managed elsewhere. This reduces one class of data and execution exposure without moving the entire orchestration stack.

The newly announced model places the **complete control plane** with the customer. Anthropic says this includes the Managed Agents server, database, shell/file workers, secrets and session history. Developers use the same core agent APIs, but the organisation owns uptime, capacity, upgrades, backups and incident response for more moving parts.

The decision is not simply cloud versus on-premises. A team may already have mature cloud controls and be comfortable with hosted agents, while another may require explicit ownership of session logs and credentials under its operational policy.

## Control does not mean risk disappears

Anthropic highlights four security design principles. The agent harness and executable sandbox are separated. Credentials can be kept outside the sandbox, with proxies adding approved credentials to requests. Network access can be restricted to allowed hosts. Sessions record agent steps, tool calls and responses, with OpenTelemetry export for monitoring.

These are valuable architectural controls. They do not guarantee that a malicious instruction in a retrieved document is harmless, that every privileged action is appropriate, or that a misconfigured customer's firewall is safe. The enterprise remains responsible for access reviews, environment hardening, approval rules and incident handling.

A useful procurement test is to ask who can access the **tool execution environment**, who can read stored prompts and tool results, who manages the secrets manager, and what cross-border or third-party processing still occurs when a request leaves for a model endpoint.

Anthropic also says that an organisation's existing **zero-data-retention arrangement**, if one has been negotiated, applies to model requests under the same Messages API rules. Self-hosting does not automatically confer ZDR or independently guarantee a particular legal compliance status.

## The economics: platform control has its own cost

For many buyers, managed services are attractive because infrastructure operations are someone else's problem. Moving the platform into an internal environment can increase control while creating expenses for reliability engineering, security audits, log storage, monitoring and platform maintenance.

Consider a **hypothetical** service executing 12,000 business tasks weekly. That represents **624,000 tasks in 52 weeks**. Suppose **1%** require a six-minute human exception review. That creates 6,240 exception cases annually, or **624 labour-hours**. At an illustrative **€65 loaded hourly rate**, that is **€40,560 of annual review capacity** before model use, hosting, licensing or incident costs.

At a 3% exception rate, that illustrative review cost would rise to **€121,680**. This sensitivity calculation is not a claimed Anthropic failure rate, quotation or observed customer result. It demonstrates why improving oversight and task accuracy can matter more to the economic model than shaving a small amount off model tokens.

Self-hosting could reduce data-routing complexity or fit an existing security stack; it could also require additional on-call capacity. The announcement gives **no general self-hosting licence price, customer labour saving or published total cost of ownership**. There is no evidential basis for calling it cheaper than hosted by default.

## What procurement should ask before adopting the beta

Before committing, a company should establish who manages upgrades and vulnerability response, how sessions are backed up, whether network isolation can be independently tested, and how credentials are revoked when staff leave. It should test what happens when the model endpoint is unreachable while a tool action has already changed a production system.

A representative trial might use a non-production environment to execute approved tasks, attempt unauthorised network access, rotate a credential mid-session, crash a worker and restore the event history. The test should produce a documented audit trail, not only a successful task screenshot.

For sensitive deployments, procurement also needs clarity on contractual data processing, residency, model routing, retention, customer support obligations and beta limitations. Neither a private-beta announcement nor architectural claims substitute for those documents.

## Why this matters for Anthropic's enterprise strategy

Self-hosting gives organisations with stricter infrastructure policies another route to adopting Claude-powered agents. It could make the platform eligible for evaluations that a wholly hosted service cannot satisfy. However, **expanded technical eligibility is not reported revenue**, and no adoption numbers or economics have been disclosed.

This subject differs from our [always-on agent blueprint analysis](/wealth/anthropic-always-on-agents-business-case-permissions-cost/), which focuses on event queues, timers and recovery within an application. The new product decision is who actually operates the platform and carries the compliance and maintenance work. It also complements our analysis of [Claude service interruptions](/wealth/anthropic-claude-outage-enterprise-agent-reliability-november-2026/), without implying self-hosting removes dependencies on remote model availability.

Follow the [Anthropic private-company research hub](/companies/anthropic/) for primary-source updates. Anthropic has filed for a proposed IPO, but this product announcement alone does not establish a listing date or imply publicly traded Anthropic shares.

*Research checked 17 November 2026, based primarily on Anthropic's 12 November private-beta announcement. All task volumes and financial examples are illustrative. Photograph: TechCrunch / Kimberly White, September 2023, CC BY 2.0, archival adapted crop.*
