# Compound News Radar

The News Radar is the discovery layer for Compound's future News section.

## Purpose

Every two hours, GitHub Actions checks a curated set of RSS feeds and maintains a single open GitHub issue titled:

**Compound News Radar**

The radar ranks recent items that may fit Compound's three editorial areas:

- Wealth
- Health
- Happiness

It is intentionally a discovery tool, not an autopublisher.

## Editorial workflow

When asked for recent Compound news ideas:

1. Review the latest News Radar.
2. Pick stories with a clear Irish health, wealth or quality-of-life consequence.
3. Independently research the story on the web.
4. Prefer primary sources: Government departments, Revenue, HSE, CSO, Central Bank, ECB, legislation and regulators.
5. Distinguish confirmed facts from proposals, reports and commentary.
6. Write the short Compound News article.
7. Link it to the relevant evergreen article(s) and tool(s).
8. Publish it.
9. Once the social credentials are connected, the social workflow can distribute the article to the enabled accounts.

## Current feeds

The initial feed set uses:

- Irish Examiner Ireland
- Irish Examiner Business
- Irish Examiner Lifestyle
- ECB official press RSS

The Irish Examiner explicitly provides free RSS feeds for parsing/use via a website or reader. ECB provides official RSS news feeds.

RTÉ RSS is **not** included in the automated feed set because RTÉ's published terms state that commercial use of its RSS feeds requires prior agreement. RTÉ can still be used as a normal reporting source during independent web research.

## Adding sources

Edit:

`config/news-feeds.yml`

Each feed can have:

- a name
- RSS URL
- default topic tags
- a source type
- a weighting

The radar deduplicates headlines, applies topic keywords and gives more recent items a freshness boost.

## Important

A feed headline must never be turned directly into a Compound article without verification. RSS is for discovery; the published article should be independently sourced.
