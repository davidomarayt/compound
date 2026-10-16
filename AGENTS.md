# Compound.ie editorial duplication check

Before proposing, writing or publishing any new article, evergreen guide, calculator, series chapter or company research piece:

1. Start with `EDITORIAL_TOPIC_INDEX.md` for a fast alphabetical lookup of published articles and calculators. Then check `CONTENT_INVENTORY.md` and search `data/content-inventory.json` for the requested title, search intent, close synonyms, audience question and related topics.
2. Check existing tools and embedded explanatory guides as well as editorial articles. A topic may already be covered by a tool, a guide, a chapter or an existing news article.
3. If existing content answers substantially the same user question, improve the original canonical page instead of publishing a competing article. Preserve established URLs and internal links.
4. If creating a new page for a genuinely distinct search intent, link it to other related guides and calculators, and use a relevant, non-repeated hero image. **For approved stock photography, set `hero_image_url`, `hero_image_alt`, `hero_image_credit`, `hero_image_source` and `require_pinned_hero: true` in front matter. Do not rely on only `image:`; `scripts/news_images.py` may otherwise replace it with an unrelated generic fallback. Check the actually rendered hero and social image on the live page.**
5. Earnings: never publish quarter-by-quarter article spam. Consolidate current and earlier fiscal-year quarterly results in each company's continuous stock research report, using actual company fiscal periods and confirmed reported numbers.
6. The inventory is generated from source by `python scripts/update_content_inventory.py`. The GitHub Actions inventory workflow regenerates it when content changes. When accuracy matters, check the live publishing files too: the inventory is a snapshot, not a substitute for validating publication status or factual claims.

This is a content *title and URL* catalogue, not evidence that all pages rank or have received organic traffic.

## Article cover photography policy (effective 16 October 2026)

- The publisher does **not** want AI-generated, synthetic, drawn or model-rendered article hero and social images. Use genuine, topic-specific photography with a source and permission/licence appropriate for editorial reuse.
- Preserve the real subject and date. If a newer-event image is unavailable, a relevant licensed archival photograph is acceptable only when explicitly labelled as archival, with its true capture date, and never represented as footage of the new event.
- Include photographer/publisher credit, original source URL, licence/permission basis, accurate image alt text and corresponding Open Graph/Twitter image. Never scrape or republish unlicensed news-agency images.
- Fail build rather than substitute a generic calculator, desk, AI art or unrelated stock image. The Mag 7 publishing workflow enforces documentary photograph metadata before publication.

## Required image QA for manually authored news

- Manually authored news must not silently reuse generic finance photos, calculators, desks, laptops, kitchens or unrelated stock images.
- Before publishing a new manual article, assign a unique, topic-specific cover and social image. Prefer an original illustration or an approved attributed photograph. For a custom local cover, set `image`, `social_image`, `image_alt`, `image_credit`, `image_source` and `require_pinned_hero: true`; ensure the asset actually exists before the news-image processor runs. Stock photos use the separately supported `hero_image_url` and approved credit fields.
- The pipeline must fail the build, rather than show a generic placeholder, if a required pinned image is absent or invalid.
- Verify the rendered article cover AND actual Open Graph/Twitter image after building, not just the markdown image description. These checks are part of publication, not optional polish.
