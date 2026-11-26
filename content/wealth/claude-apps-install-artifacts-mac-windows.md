---
title: "Claude Apps: How to Install Claude Artifacts on Mac and Windows"
seo_title: "Claude Apps: Install Claude Artifacts on Mac and Windows"
slug: claude-apps-install-artifacts-mac-windows
pillar: wealth
canonical_path: /wealth/claude-apps-install-artifacts-mac-windows/
publication_status: published
draft: false
date: "2026-11-26"
research_checked: "2026-11-26"
editorial_review_status: pending
author: "Compound Research"
summary: "Claude can now turn an artifact into a Mac or Windows app. Here’s how to install one, what permissions it can request, and where it could save a small team time."
meta_description: "How to install Claude artifacts as apps on Mac and Windows, which Claude plans get the beta, and what to know about permissions, usage limits and connectors."
tags: [wealth, company-research, company-anthropic, stock-ant, anthropic, claude, productivity]
image: /static/images/evergreen/claude-apps-install-artifacts-mac-windows.jpg
social_image: /static/images/evergreen/claude-apps-install-artifacts-mac-windows.jpg
image_alt: "Archival photograph of a Claude-generated Markdown document in the Claude interface on a laptop, published July 2026."
image_credit: "Brett Wharton / Unsplash (Unsplash License). Archival photograph published 1 July 2026, cropped."
image_source: https://unsplash.com/photos/laptop-screen-displaying-claude-fable-3-is-currently-unavailable-message-dmmIt1jPW6w
hero_image_url: "https://images.unsplash.com/photo-1782876088379-fe9a85602678?rect=1500,0,3050,1600&w=1400&fm=jpg&q=82"
hero_image_alt: "Archival photograph of a Claude-generated Markdown document in the Claude interface on a laptop, published July 2026."
hero_image_credit: "Brett Wharton / Unsplash (Unsplash License). Archival photograph published 1 July 2026, cropped."
hero_image_source: https://unsplash.com/photos/laptop-screen-displaying-claude-fable-3-is-currently-unavailable-message-dmmIt1jPW6w
require_pinned_hero: true
sources:
  - title: "Anthropic — Turn artifacts into Mac and Windows apps, 24 November 2026"
    url: https://claude.com/resources/articles/install-as-app
  - title: "Claude Help Center — Install an artifact as an app"
    url: https://support.claude.com/en/articles/18516354-install-an-artifact-as-an-app
  - title: "Anthropic — Your apps can now open in Claude, 10 November 2026"
    url: https://claude.com/resources/articles/interactive-connectors-full-tool
  - title: "Unsplash — Photography license"
    url: https://unsplash.com/license
---

Anthropic began rolling out **Install as app** on 24 November. If Claude builds you an interactive calculator, tracker or dashboard as an artifact, you can now install it from Claude Desktop and open it in its own window on a Mac or Windows PC. The app has its own icon, can use Claude and supported connectors, and changes when the underlying artifact is edited. You need to be online and signed in to Claude Desktop to open it. [Anthropic’s announcement](https://claude.com/resources/articles/install-as-app).

For an Irish small business, a sensible first experiment is a weekly tool with a repeatable job, such as checking which customer quotes need a follow-up. The potential saving is in opening the same tool next Monday with your rules and layout already in place.

## How to install an artifact as a Claude app

1. **Update Claude Desktop.** Anthropic’s help page lists version 6.28899.0 or later for Mac and Windows. The beta is rolling out across Free, Pro, Max, Ultra, Team and Enterprise. Enterprise owners must enable it, and Team admins control access to the highest permission level.
2. **Build and test the artifact.** Describe the tool you want in Claude, then try it with a few representative examples. Check any calculations against results you already know.
3. **Choose Install as app.** In Claude Desktop, open the artifact, open its **Share** menu and select **Install as app**. Confirm when prompted. You can find installed apps in the Claude Apps folder on Mac or the Start menu on Windows.
4. **Start with the default permissions.** If the tool works with the information you type or paste in, leave access at that level. [Claude Help Center installation guide](https://support.claude.com/en/articles/18516354-install-an-artifact-as-an-app).

If **Install as app** is missing, check the desktop version and whether your organisation has enabled the feature. Anthropic also lists some artifact formats that cannot be installed, including Claude Docs, Slides and Sheets. [Anthropic’s rollout notes](https://claude.com/resources/articles/install-as-app).

## What permissions can Claude apps request?

| Permission | What it means for the user |
| --- | --- |
| Default | The app has the capabilities it would have in a browser. Start here for calculators and tools that work on pasted inputs. |
| App permissions | The app can ask for desktop features such as notifications, global keyboard shortcuts or a window that stays on top. |
| Full computer access | The app can ask to run programs or read, change or delete files without a separate prompt for each action. Claude limits who can grant this level to apps they build themselves or, on Team and Enterprise, apps made within their organisation. Organisation settings also apply. |

An approval is tied to the app’s current version. If someone edits the underlying artifact, Anthropic says Claude asks again for permissions. For a tool built around a connected service, check both what the app can do on the computer and what the connector can do in that account. [Anthropic’s permissions explanation](https://claude.com/resources/articles/install-as-app).

## A useful first project for a small business

Try a **quote follow-up tracker** with a made-up set of jobs. Give it quote IDs, amounts, dates sent and statuses. Have it highlight quotes that have gone unanswered for seven days, calculate the total value of open quotes and let you export the list. Keep email sending in the existing workflow while you check that the app flags the right rows.

Give Claude a prompt like this.

> Build an interactive artifact for tracking quotes. Let me paste a CSV with quote ID, amount in euros, date sent and status. Flag open quotes older than seven days and total the value of open quotes. Include sample rows and a CSV export. Use only the data I paste in.

Test cases worth trying include a quote dated exactly seven days ago, a row missing an amount and a quote already marked as accepted. Agree who updates the tool and where the authoritative quote list lives before colleagues rely on its output.

## Does installing a Claude app cost extra?

Installing the artifact uses your Claude account. Anthropic says building an app and any requests it sends to Claude count toward your plan’s existing usage limits. If you build a tracker that calls Claude for every row, measure what one typical run consumes before using it across the team. A seven-day flag based on a date can be calculated by the app itself. Reserve model calls for work like summarising notes that lack a fixed format. [Anthropic’s usage guidance](https://support.claude.com/en/articles/18516354-install-an-artifact-as-an-app).

## Claude desktop apps and apps inside Claude

Anthropic also uses the word *apps* for tools you can open **inside** Claude. On 10 November it announced fuller interactive connectors that let you work in supported services alongside the conversation. Opening a Notion page and editing it with Claude uses Notion’s connector. A reusable tracker you build as an artifact and install on your computer uses the desktop beta. [Anthropic’s interactive connectors announcement](https://claude.com/resources/articles/interactive-connectors-full-tool).

The distinction matters for Anthropic’s business. Connectors give people a reason to bring existing work into Claude. Installed artifacts give people a reason to return to a tool they built there. Whether that creates lasting value depends on how often people reopen those apps, how much maintenance they require, and how much paid Claude usage that repeat work generates. That is a related question to who pays when software teams embed AI in their products. [Read Compound’s analysis of Anthropic’s linked billing](/wealth/anthropic-linked-billing-api-customer-pays-agent-economics/).
