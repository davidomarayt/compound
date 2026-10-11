# Compound.ie editorial duplication check

Before proposing, writing or publishing any new article, evergreen guide, calculator, series chapter or company research piece:

1. Start with `EDITORIAL_TOPIC_INDEX.md` for a fast alphabetical lookup of published articles and calculators. Then check `CONTENT_INVENTORY.md` and search `data/content-inventory.json` for the requested title, search intent, close synonyms, audience question and related topics.
2. Check existing tools and embedded explanatory guides as well as editorial articles. A topic may already be covered by a tool, a guide, a chapter or an existing news article.
3. If existing content answers substantially the same user question, improve the original canonical page instead of publishing a competing article. Preserve established URLs and internal links.
4. If creating a new page for a genuinely distinct search intent, link it to other related guides and calculators, and use a relevant, non-repeated hero image. **For approved stock photography, set `hero_image_url`, `hero_image_alt`, `hero_image_credit`, `hero_image_source` and `require_pinned_hero: true` in front matter. Do not rely on only `image:`; `scripts/news_images.py` may otherwise replace it with an unrelated generic fallback. Check the actually rendered hero and social image on the live page.**
5. Earnings: never publish quarter-by-quarter article spam. Consolidate current and earlier fiscal-year quarterly results in each company's continuous stock research report, using actual company fiscal periods and confirmed reported numbers.
6. The inventory is generated from source by `python scripts/update_content_inventory.py`. The GitHub Actions inventory workflow regenerates it when content changes. When accuracy matters, check the live publishing files too: the inventory is a snapshot, not a substitute for validating publication status or factual claims.

This is a content *title and URL* catalogue, not evidence that all pages rank or have received organic traffic.
