---
title: "Databricks Can Now Share Data Across Regulated Clouds. Who Bears the Compliance Risk?"
seo_title: "Databricks Cross-Cloud OpenSharing: Government Clouds, Risk and Economics"
slug: databricks-cross-regulatory-cloud-sharing-governance-economics
pillar: wealth
canonical_path: /wealth/databricks-cross-regulatory-cloud-sharing-governance-economics/
publication_status: published
date: '2026-11-22'
research_checked: '2026-11-22'
editorial_review_status: pending
summary: "Databricks' 19 November cross-regulatory-domain OpenSharing availability connects certain commercial and government cloud environments, but customer governance and actual transfer restrictions still determine its business value."
meta_description: "Databricks made cross-regulatory-domain OpenSharing generally available on 19 November 2026. Examine support limits, permissions, security and enterprise costs."
tags: [wealth, private-company, company-research, company-databricks, databricks, data-governance, enterprise-ai, cloud-security, cloud-economics]
hero_image_url: https://upload.wikimedia.org/wikipedia/commons/3/3a/Data_%2B_AI_Summit_2026.jpg
hero_image_alt: "Real photograph of the Databricks Data and AI Summit in June 2026; archival company event, not the November cross-cloud release"
hero_image_credit: "Grant Terzakis / Databricks Comms via Wikimedia Commons, CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), photographed June 2026; archival resized crop"
hero_image_source: https://commons.wikimedia.org/wiki/File:Data_%2B_AI_Summit_2026.jpg
require_pinned_hero: true
image: /static/images/evergreen/databricks-cross-regulatory-cloud-sharing-governance-economics.jpg
social_image: /static/images/evergreen/databricks-cross-regulatory-cloud-sharing-governance-economics.jpg
image_alt: "Documentary photograph of Databricks' June 2026 Data and AI Summit, not the new sharing functionality"
image_credit: "Grant Terzakis / Databricks Comms, Wikimedia Commons, CC BY-SA 4.0; archival cropped photograph"
image_source: https://commons.wikimedia.org/wiki/File:Data_%2B_AI_Summit_2026.jpg
sources:
- title: "Databricks — November 2026 product release notes, 19 November generally available cross-regulatory-domain OpenSharing"
  url: https://docs.databricks.com/aws/en/release-notes/product/2026/november
- title: "Databricks — Cross-regulatory domain and cloud-region sharing support matrix"
  url: https://docs.databricks.com/aws/en/opensharing/share-data-databricks
- title: "Databricks — August 2026 $7bn-plus annualised revenue run-rate and financing announcement"
  url: https://www.databricks.com/company/newsroom/press-releases/databricks-grows-80-yoy-surpasses-7b-revenue-run-rate-scales
- title: "Wikimedia Commons — Grant Terzakis / Databricks Comms, Data and AI Summit 2026, CC BY-SA 4.0"
  url: https://commons.wikimedia.org/wiki/File:Data_%2B_AI_Summit_2026.jpg
---

**Sharing governed data between commercial and restricted cloud environments can reduce the cost of duplicated infrastructure, but it does not transfer the customer's legal responsibilities to the software supplier.** That is the investment and procurement question behind Databricks' latest OpenSharing announcement.

According to the company's [November product release notes](https://docs.databricks.com/aws/en/release-notes/product/2026/november), **cross-regulatory-domain Databricks-to-Databricks sharing became generally available on 19 November 2026**. The feature makes certain exchanges possible between commercial and government-oriented cloud deployments. Its effect is technical interoperability—not a blanket finding that any category of regulated information may legally cross a border or a security boundary.

## What changed on 19 November?

Previously, organisations operating multiple Databricks deployments across different regulatory environments could face greater difficulty delivering governed data to another deployment. The new OpenSharing capability provides supported paths for sharing data with recipients in other specified deployment environments.

The [documented support matrix](https://docs.databricks.com/aws/en/opensharing/share-data-databricks) matters more than the general marketing shorthand. The availability described includes relevant flows between some commercial environments and **AWS GovCloud**, **GovCloud for the US Department of Defense**, and **Azure China** deployments. But it does **not** claim that every pair is supported. For example, the documentation identifies some unsupported combinations involving **Azure China and GovCloud**, **Google Cloud and GovCloud DoD**, and **Azure Government**.

This is why an enterprise architect should check the *actual provider, deployment region and recipient pair*, not simply label two workspaces as Databricks and assume they can exchange data. Databricks also cautions in the release notes that features may arrive in individual workspaces after the announcement date.

## Data access is not the same as legal authorisation

The most dangerous misunderstanding is that a generally available product feature confers permission to transfer sensitive data. A cloud service can provide identity, permission management and technical isolation while the customer remains responsible for classification, sovereignty obligations, contract terms and the applicable law.

That distinction is especially important for government, defence, healthcare and regulated financial users. An organisation might be technically able to send a dataset to another region but still be prevented from doing so by a procurement contract, retention policy or data-protection rule. The supported cloud combinations are software capabilities; **they are not endorsements by a regulator**, security accreditations for a particular customer's workload, or a substitute for an information-governance assessment.

The sensible control is to require a documented data-owner approval before adding a new sharing recipient. Permissions should cover the exact dataset and intended use, with a process for revocation, periodic review and incident handling.

## Why a cross-domain share can be valuable

Suppose a large enterprise keeps duplicate reference data in several cloud environments. Each copy has to be refreshed and checked. Divergent versions can produce inconsistent analytics, especially when business rules change.

A governed share may reduce some duplication by allowing authorised recipients to access a maintained source. That can shorten the time needed to onboard a new analytical team or make a curated table available to another department. Yet the economics depend on whether that architecture actually replaces copies, what data transfer and compute still cost, and how much governance is added.

Consider a **fictional organisation** maintaining six copies of a reference dataset. Assume each copy requires **five staff hours per month** for manual reconciliation, a total of **30 hours**. If a supported sharing setup eliminates four copies and reduces ongoing reconciliation to **10 hours monthly**, it frees **20 hours**. At a hypothetical labour cost of **€65 per hour**, that is **€1,300 of labour-capacity value per month** before infrastructure expense.

If new permissions administration and audit checks require eight hours monthly, net released effort is **12 hours**, worth **€780 in theoretical capacity**, not guaranteed cash savings. All these numbers are assumptions, not published customer results, Databricks guidance or a claim about margins.

| Illustrative monthly task | Before sharing | Hypothetical after |
|---|---:|---:|
| Manual data reconciliation | 30 hours | 10 hours |
| New permission and audit administration | 0 hours | 8 hours |
| Total staff effort | 30 hours | 18 hours |
| Net capacity released at €65/hour | — | €780 |

An actual business case also needs a measurement of storage, network egress, compute charges, governance tooling, implementation work and potential reliability costs.

## New integration paths create new risks

Sharing may make the sender's data easier to reach, but the receiving team's need for it does not settle whether sharing is appropriate. A poorly scoped grant can expose more rows or columns than intended. Teams should verify whether recipients need raw records or could use aggregated and masked versions instead.

A second risk is unexpected dependence. If downstream users rely on a dataset that can change without notice, analyses may break or silently diverge. Agreements should specify schema evolution, quality checks, ownership, refresh expectations and who can stop a problematic share.

There is also the danger of overlooking the product's configuration-dependent transport mechanisms. Databricks documents different approaches to access in different environment combinations, including cases involving **pre-signed URLs**. That can influence credential management, audit logging and security reviews. A technical preview should test the actual transfer path rather than assume a uniform security model.

## What the financial disclosures prove—and what they do not

In August 2026, Databricks [said](https://www.databricks.com/company/newsroom/press-releases/databricks-grows-80-yoy-surpasses-7b-revenue-run-rate-scales) it had passed a **$7 billion annualised revenue run-rate** and announced a **$5 billion financing at a $190 billion valuation**. Those are the company's own dated statements. An annualised run-rate is not the same as audited full-year revenue; a financing valuation is not an exchange-traded share price.

The 19 November technical release supplies **no separate adoption, booking, revenue, gross-margin or operating-profit number** for cross-domain OpenSharing. There is a plausible commercial rationale: more interoperable data could support enterprise expansion, renewals and usage. Whether that occurs at an attractive margin requires real customer evidence.

This differentiates the new story from our [Databricks EMEA investment analysis](/wealth/databricks-three-billion-emea-investment-agent-platform-distribution/), which concerns regional spending and distribution, and our [always-on Genie analysis](/wealth/databricks-always-on-genie-enterprise-agent-economics/), which measures possible task-level value from agents. Cross-domain OpenSharing concerns **where governed data can move, who approves access, and what that costs**.

## The procurement checklist that actually matters

Before adopting the feature, an enterprise should map sender/recipient environment pairs against the published support matrix, document the legal basis for the transfer, test least-privilege recipient permissions, confirm audit and revocation controls, and establish a rollback mechanism. It should then compare actual data-reconciliation effort, compute and transfer costs against its previous architecture.

The commercial promise is substantial if organisations can operate fewer duplicate pipelines while maintaining clear controls. The uncertainty is just as important: Databricks has announced technical general availability in supported combinations, **not universal regulatory clearance or independently verified savings**.

For ongoing source-backed research see the [Databricks private-company profile](/companies/databricks/). The company remains privately held, and its last announced financing value is not a public quote.

*Research checked 22 November 2026. Product availability announcement dated 19 November; check each workspace rollout and the live support matrix before implementation. Cover: authentic June 2026 Databricks summit photograph, Grant Terzakis / Databricks Comms, CC BY-SA 4.0, archival.*
