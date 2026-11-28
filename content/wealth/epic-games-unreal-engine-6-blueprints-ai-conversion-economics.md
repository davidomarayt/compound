---
title: "Epic Drops Blueprints From Unreal Engine 6: Who Pays for the AI Migration?"
seo_title: "Unreal Engine 6 Drops Blueprints: Epic's AI Migration Bet"
slug: "epic-games-unreal-engine-6-blueprints-ai-conversion-economics"
pillar: "wealth"
canonical_path: "/wealth/epic-games-unreal-engine-6-blueprints-ai-conversion-economics/"
publication_status: "published"
draft: false
date: "2026-11-28"
research_checked: "2026-11-28"
editorial_review_status: "pending"
author: "Compound Research"
summary: "Epic Games says Unreal Engine 6 will ship without Blueprints and its Actor framework, and that AI will make converting UE5 projects cheap. We look at what the change means for Epic's royalty model and for the studios that must move."
meta_description: "Epic says UE6 will drop Blueprints and rely on AI to convert UE5 games to Verse. How the royalty model shields Epic's near-term revenue, and where the risk lands."
tags: ["wealth", "private-company", "company-research", "company-epic-games", "epic-games", "video-games", "game-engines", "artificial-intelligence"]
hero_image_url: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Unreal_Engine_booth.jpg/1280px-Unreal_Engine_booth.jpg"
hero_image_alt: "Visitors crowd the Epic Games Unreal Engine booth at the Game Developers Conference in San Francisco on 1 March 2017; archival photograph, not the UE6 announcement."
hero_image_credit: "Official GDC via Wikimedia Commons, CC BY 2.0 (https://creativecommons.org/licenses/by/2.0/), 1 March 2017; resized/cropped."
hero_image_source: "https://commons.wikimedia.org/wiki/File:Unreal_Engine_booth.jpg"
require_pinned_hero: true
image: "/static/images/evergreen/epic-games-unreal-engine-6-blueprints-ai-conversion-economics.jpg"
social_image: "/static/images/evergreen/epic-games-unreal-engine-6-blueprints-ai-conversion-economics.jpg"
image_alt: "Visitors crowd the Epic Games Unreal Engine booth at the Game Developers Conference in San Francisco on 1 March 2017; archival photograph, not the UE6 announcement."
image_credit: "Official GDC via Wikimedia Commons, CC BY 2.0 (https://creativecommons.org/licenses/by/2.0/), 1 March 2017; resized/cropped."
image_source: "https://commons.wikimedia.org/wiki/File:Unreal_Engine_booth.jpg"
sources: [{"title": "Unreal Engine — An update on Blueprints and the path to UE6 (Marcus Wassmer)", "url": "https://www.unrealengine.com/news/an-update-on-blueprints-and-the-path-to-ue6"}, {"title": "Unreal Engine — Licensing options", "url": "https://www.unrealengine.com/en-US/license"}, {"title": "Game Developer — Epic Games no longer plans to include Blueprints or Actor Gameplay Framework in Unreal Engine 6, 23 November 2026", "url": "https://www.gamedeveloper.com/programming/unreal-engine-6-to-remove-blueprints-and-actor-gameplay-framework-from-the-beginning"}, {"title": "80 Level — Blueprints Will Be Removed In Unreal Engine 6", "url": "https://80.lv/articles/unreal-engine-6-will-not-include-blueprints-gameplay-framework"}, {"title": "Wikimedia Commons — archival photo, CC BY 2.0", "url": "https://commons.wikimedia.org/wiki/File:Unreal_Engine_booth.jpg"}]
---

Platform companies usually try hard to keep old code running. Breaking it pushes the cost of an upgrade onto customers, and gives them a moment to reconsider. Epic Games has just decided to break one of the most widely used parts of Unreal Engine, and is betting that AI will make the bill small enough that developers follow.

In a post titled ["An update on Blueprints and the path to UE6"](https://www.unrealengine.com/news/an-update-on-blueprints-and-the-path-to-ue6), Epic executive Marcus Wassmer said that "UE6, including UE6 Early Access, won't include Blueprints or the Actor Gameplay Framework." Gameplay "will be built in Verse and on the new Scene Graph framework." Trade outlet [Game Developer](https://www.gamedeveloper.com/programming/unreal-engine-6-to-remove-blueprints-and-actor-gameplay-framework-from-the-beginning) reported the change on 23 November.

## What changed

Blueprints is Unreal's node-based visual scripting system. It lets designers and artists build gameplay without writing much code, and it is a large part of why smaller teams pick Unreal. Game Developer notes that Sandfall, the studio behind *Clair Obscur: Expedition 33*, has said the game was "95 percent built" with Blueprints.

In June, Epic had said Blueprints and Actors would coexist with the new framework in UE6 Early Access and 6.0, so UE5 projects could upgrade step by step. That plan is now withdrawn. Epic's reasoning, in its own words: "we expect AI to massively help with converting UE5 projects to UE6, if not make that process fully automatic." Epic says that also means it can deliver UE6 "on time (or sooner!)".

Epic did not give a UE6 release date or say how long UE5 will be supported. It said to expect "continued development on targeted UE5 features, fixes, and support" while UE6 is built, and that it has started bringing UE6 AI tooling back to UE5 with the UE 5.9 preview.

## Epic's evidence: Fortnite

The company's main proof point is its own game. Wassmer wrote that Epic tried using AI to convert the Blueprints for Fortnite Battle Royale to Verse, a project that "was expected to take years". The result, he said, is a working prototype of about 3 million lines of Verse code after porting more than 20,000 Blueprints. The team is still validating performance, memory use and architecture.

Epic's cost argument is that the cost of any given AI task has been falling "13x year over year", while the complexity of converting a game stays roughly constant, so it expects "modest conversion costs" by the time UE 6.0 ships.

Both claims are Epic's. A prototype is not a shipped game, and Fortnite was converted by the team that built both the engine and Verse, with unusual access to the code and its authors. A mid-sized external studio's experience may differ.

## Why the royalty model softens the risk for Epic

Epic is privately held and does not publish Unreal revenue. Its public [licensing terms](https://www.unrealengine.com/en-US/license) do show how it earns money from games: a 5% royalty on "all lifetime gross revenue above $1M that is directly attributable to the UE product, regardless of who collects it". Sales through the Epic Games Store are royalty-free. Non-game commercial users above $1 million in revenue over 12 months pay $1,850 per seat per year.

That structure matters here. A studio that refuses to move and stays on UE5 still pays the same royalty on the games it ships. For illustration only, a game earning $10 million in lifetime gross revenue would owe 5% of the $9 million above the threshold, or $450,000, whether it was built in UE5 or UE6.

So the near-term revenue risk from holdouts is small. Developers such as former Valve writer Chet Faliszek, who Game Developer reports said his team will stay on UE5, remain Epic customers.

## Where the risk does land

The real exposure is slower and harder to measure.

**New-project engine choice.** The decision that matters commercially is which engine a studio picks for its next game. If teams that relied on visual scripting conclude that Unreal's future demands a code-first, AI-assisted workflow they do not want, some will look at alternatives. Each lost project is several years of future royalties.

**Studio budgets absorb the migration.** Even if AI conversion works, someone pays for testing, performance work and retraining staff on Verse. Epic's claim of modest costs shifts that question to studios, many of which are under financial pressure.

**Workforce and skills.** Blueprints let non-programmers build gameplay. Moving to a programming language plus AI tooling changes who on a team can do that work, which is a cultural and organisational cost as well as a technical one.

## Why Epic may think it is worth it

The strategic payoff is a single technology stack. Verse is already the language of Unreal Editor for Fortnite, the tool creators use to build experiences inside Fortnite. A Verse-first UE6 lets Epic align its professional engine with its creator economy, and design the engine for what it calls "AI operability" from the start. Game Developer also links the move to Epic's broader shift towards an AI-first business model.

If AI conversion works as Epic describes, it gets a cleaner engine sooner without years of maintaining two frameworks. If it does not, the cost falls first on its customers, and only later, through engine choices, on Epic.

## What to watch

- A UE6 Early Access date and any formal UE5 support window.
- Published results from Epic's Fortnite conversion, especially performance and memory figures.
- Case studies from external studios that convert real UE5 projects, and the effort it took.
- Any change to Unreal licensing terms around UE6.

Follow the [Epic Games company research profile](/companies/epic-games/) for verified developments.

*Compound Research; research checked 28 November 2026. Engine plans and conversion figures are from Epic's own post and have not been independently verified. Licensing terms are from Epic's Unreal Engine licence page. The royalty example is hypothetical Compound arithmetic. Epic Games is privately held; no valuation, revenue or release date is implied. This is not investment advice.*

## Source record
- https://www.unrealengine.com/news/an-update-on-blueprints-and-the-path-to-ue6
- https://www.unrealengine.com/en-US/license
- https://www.gamedeveloper.com/programming/unreal-engine-6-to-remove-blueprints-and-actor-gameplay-framework-from-the-beginning
- https://80.lv/articles/unreal-engine-6-will-not-include-blueprints-gameplay-framework
