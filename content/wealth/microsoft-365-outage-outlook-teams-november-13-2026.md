---
title: "Microsoft 365 outage: Outlook and Teams disruption continues into Friday"
seo_title: "Microsoft Outage Today: Outlook, Teams and 365 Status — 13 November 2026"
slug: microsoft-365-outage-outlook-teams-november-13-2026
pillar: wealth
canonical_path: /news/microsoft-365-outage-outlook-teams-november-13-2026/
draft: false
publication_status: published
date: '2026-11-13'
research_checked: '2026-11-13'
summary: "Microsoft 365 services including Outlook, Exchange Online and features of Teams and Copilot were disrupted globally. What Microsoft says went wrong and why the outage matters."
meta_description: "Microsoft 365 outage 13 November 2026: latest verified Outlook, Teams and Exchange Online status, cause, workarounds and business impact."
tags: [news, wealth, microsoft, msft, stock-msft, microsoft-365, outlook, teams, cloud, outage]
hero_image_url: "https://upload.wikimedia.org/wikipedia/commons/2/27/Microsoft_sign_closeup.jpg"
hero_image_alt: "A Microsoft sign at the company's Redmond campus, photographed in April 2005; archival image unrelated to the November 2026 outage."
hero_image_credit: "Derrick Coetzee / Wikimedia Commons — public domain, photograph from April 2005 (archival)."
hero_image_source: "https://commons.wikimedia.org/wiki/File:Microsoft_sign_closeup.jpg"
require_pinned_hero: true
image: /static/images/evergreen/microsoft-365-outage-outlook-teams-november-13-2026.jpg
social_image: /static/images/evergreen/microsoft-365-outage-outlook-teams-november-13-2026.jpg
image_alt: "Microsoft sign at Redmond campus, April 2005. Archival photograph, not a scene from the November 2026 Microsoft 365 disruption."
image_credit: "Derrick Coetzee / Wikimedia Commons, public domain (2005 archival photograph)."
image_source: "https://commons.wikimedia.org/wiki/File:Microsoft_sign_closeup.jpg"
sources:
  - title: "Microsoft public service health page"
    url: "https://sdf.status.cloud.microsoft/"
  - title: "Microsoft service-health incident descriptions — Exchange Online EX1550543 and Microsoft 365 MO1550821"
    url: "https://mailservices.isc.upenn.edu/computing/email/penno365/alerts/ms-incidents.html"
  - title: "RTÉ News, Microsoft outage drags on, 13 November"
    url: "https://www.rte.ie/news/business/2026/1113/1599061-microsoft-tech-outage/"
  - title: "Associated Press, Microsoft struggles to restore global services"
    url: "https://apnews.com/article/d92547a821930290db2964388016979a"
  - title: "Reuters reporting on worldwide Outlook and Teams disruptions"
    url: "https://live.euronext.com/en/financial-news/microsoft-outage-drags-hours-disrupting-outlook-teams-businesses-and-governments"
  - title: "Microsoft fiscal first-quarter FY2027 earnings announcement"
    url: "https://www.microsoft.com/en-us/Investor/earnings/FY-2027-Q1/press-release-webcast"
---
*Status checked 13 November 2026. This is a developing incident. Microsoft had reported partial signs of stabilisation, but a complete worldwide restoration was not confirmed in the official status updates available when this article was checked. The archive cover is a photograph from April 2005, not an image of the outage.*

**Microsoft 365 users around the world faced a major service disruption extending into Friday, 13 November 2026, after problems began on Thursday.** Outlook and Exchange Online were at the centre of the disruption, with effects reaching parts of Microsoft Teams, Copilot, administration and other workplace tools. People searching for **“Microsoft down today”** should distinguish between a broad Microsoft 365 incident and an outage of every Microsoft product: [Microsoft's public service-health page](https://sdf.status.cloud.microsoft/) identifies the services with confirmed degradation.

The timing matters for organisations in Ireland. Many companies, schools and public bodies use Microsoft 365 for email, calendars, meetings and identity-dependent workflows. If a mailbox or a Microsoft 365 integration becomes unreliable, an apparently simple problem sending an email can interrupt approvals, support tickets and scheduled meetings.

## Is Outlook or Microsoft Teams still down?

The [public Microsoft service-health status](https://sdf.status.cloud.microsoft/) showed degradation for Microsoft 365 business and consumer products during the incident. Microsoft said it was working to restore capacity and had seen some positive results with server stability. **Partial recovery does not mean every tenant, region or product has returned to normal.** Status can change after this article's verification time.

Based on Microsoft's incident descriptions, the main known effects included:

- **Outlook and Exchange Online:** users could be unable to reach mailboxes through Outlook on the web, desktop clients, mobile synchronisation or connected APIs; some message deliveries could be delayed.
- **Microsoft Teams:** features depending on Exchange Online, such as calendars and meeting scheduling, could fail. That does not mean all Teams calls and messages were unavailable everywhere.
- **Microsoft 365 Copilot:** customers could encounter difficulties accessing chat or connecting to email, calendar or files for work-related tasks.
- **SharePoint, Planner and admin tools:** individual functions dependent on Exchange Online or associated services could be affected, even if core file access remained functional.

These details were identified in service incidents **EX1550543** (Exchange Online) and **MO1550821** (multiple Microsoft 365 services). The [incident text reproduced by the University of Pennsylvania's PennO365 service](https://mailservices.isc.upenn.edu/computing/email/penno365/alerts/ms-incidents.html) provides a timestamped record of Microsoft's technical updates.

## What caused the Microsoft outage?

Microsoft's reported investigation focused on an overloaded process on affected servers responsible for establishing secure connections. Under heavy demand, the process stopped dealing reliably with requests, leading servers to become unresponsive. Engineers tested configuration changes, isolated and restarted parts of the affected infrastructure and applied traffic management while bringing capacity back online.

The service updates also described a recent **network configuration change correlated with the start of the impact**, which Microsoft began reverting while it investigated. A correlation at that stage was **not a completed root-cause investigation**. The company said its early changes were not improving service as expected, while later updates described some stabilisation.

Microsoft said it had **no indication of a cyberattack**, according to contemporaneous reporting by [Associated Press](https://apnews.com/article/d92547a821930290db2964388016979a) and [Reuters](https://live.euronext.com/en/financial-news/microsoft-outage-drags-hours-disrupting-outlook-teams-businesses-and-governments). That statement should not be misread as a final technical post-mortem.

## How widespread was the outage?

[Reuters](https://live.euronext.com/en/financial-news/microsoft-outage-drags-hours-disrupting-outlook-teams-businesses-and-governments) reported disruptions across businesses and government agencies, with complaints spreading beyond the Americas to parts of Asia-Pacific. At one point, Downdetector received **more than 130,000 US Outlook problem reports**. Downdetector counts reports of trouble, not distinct affected users or all Microsoft 365 subscribers, so it is not a reliable global customer-impact total.

For Ireland, [RTÉ's 13 November report](https://www.rte.ie/news/business/2026/1113/1599061-microsoft-tech-outage/) described continued Outlook and Teams problems and Microsoft's efforts to stabilise its systems. The international nature of the outage means local connectivity can be normal while an organisation's cloud-dependent email is unreliable.

## What can businesses and Microsoft 365 users do?

If your Outlook inbox is failing or your organisation cannot send or receive messages, check the [Microsoft public service-health page](https://sdf.status.cloud.microsoft/). Microsoft 365 administrators should also consult the service-health dashboard for their own tenant and the relevant incident IDs.

Practical, low-risk precautions include using an established alternative contact channel for urgent messages; checking whether Teams chat or calls remain functional before assuming they are down; avoiding repeated bulk retries that may complicate your own workflows; and verifying later whether delayed mail or automated tasks actually completed. If you administer a business service, document which dependencies have failed and monitor Microsoft's updates before applying unrelated configuration changes.

Treat unsolicited emails, calls or download links promising an immediate **“Microsoft outage fix”** with caution. There was no official basis for a consumer-side patch that could repair Microsoft's affected backend infrastructure.

## Does this mean Microsoft Azure is down?

**Not necessarily.** The confirmed problem centred on Microsoft 365 and Exchange-related infrastructure. Azure hosts an enormous variety of services, and the general Azure service-health dashboard has its own incident reporting. A business's Microsoft 365 integration failing is not proof that every Azure region or unrelated Azure service has failed. Check the specific service before making that claim.

## Why does the outage matter for Microsoft stock (MSFT)?

For investors, this incident is a test of the operational resilience underpinning Microsoft's recurring cloud subscriptions. Service interruptions can disrupt customers even when they do not permanently lose data. They can also prompt questions about incident response, architecture, contractual service credits and business continuity.

However, **the financial damage has not been quantified**. It would be unjustified to calculate a revenue or earnings hit directly from Downdetector complaints, or assume Microsoft's Azure growth has stopped because Microsoft 365 experienced a disruption. The cost to Microsoft will depend on the affected contracts, duration, applicable service-level terms, technical remediation and any longer-term effects on customers.

Microsoft's broader investment case remains connected to the profitability of cloud services and the capital required to support them. See Compound's [Microsoft stock research and quarterly dashboard](/stocks/msft/), our [analysis of Microsoft's AI investment and free cash flow](/wealth/microsoft-ai-capex-cash-flow/), and the [Microsoft and Azure business overview](/wealth/microsoft-azure-ai-returns-2026/).

## Microsoft outage today: frequently asked questions

### When did the outage begin?

Microsoft described Exchange Online connectivity trouble on Thursday, **12 November 2026**, with broader Microsoft 365 disruption continuing into Friday, 13 November. The precise start time depends on the affected service and incident record.

### Has Microsoft fixed the outage?

Microsoft reported some improving server stability while recovery continued, but **full resolution was not established in the official updates available when this story was checked**. Use the [live status page](https://sdf.status.cloud.microsoft/) for the latest tenant and product information, rather than treating a dated article as a real-time status service.

### Is Teams completely offline?

Not necessarily. Features that rely on Exchange Online, such as scheduling, have been affected. Core chat and meeting functionality can behave differently depending on the customer and feature.

### Was Microsoft hacked?

Microsoft said it had no indication the incident was a cyberattack. The final technical cause had not yet been formally established in the updates reviewed.

### Can the outage affect Ireland?

Yes. Irish businesses and other users may be affected because Microsoft 365 services and their dependencies are delivered through globally operated cloud infrastructure. An impact can occur even when a customer's own broadband is working normally.

*This article reports a developing incident using [Microsoft's status updates](https://sdf.status.cloud.microsoft/), the [published incident timeline](https://mailservices.isc.upenn.edu/computing/email/penno365/alerts/ms-incidents.html) and independently reported coverage. It is not a claim that all Microsoft products or all Azure services are offline. It is general information, not investment advice.*
