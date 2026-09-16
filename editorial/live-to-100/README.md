# Compound Live to 100 — publication record

David authorised publication of Part 1 and completion/publication of Parts 2–4 on 16 September 2026. This supersedes the brief’s earlier publication hold and outlines-only follow-on scope.

## Part 1 release

- Canonical route: `/live-to-100/`, under the existing Health pillar.
- Publication and evidence-check date: 16 September 2026.
- Approximately 2,060 words of main prose, nine substantive sources, a five-chapter 0–100 timeline and two independent years-to-100 inputs.
- Shared four-part navigation; follow-on links remain unavailable until the relevant articles are published.
- Original coastal illustration, WebP, with alt text and explicit AI credit. See `image-provenance.md`.
- Article/Breadcrumb structured data, Open Graph/Twitter metadata and a single canonical route. No new pillar, dependency, analytics configuration or homepage redesign.

## Project and workflow

Repository `davidomarayt/compound`; production branch `claude/clever-babbage-uibieq`. Python static generator with Markdown/YAML content and Jinja templates. Read project README, DECISIONS, workflow and existing templates; no AGENTS.md was present. The existing GitHub Pages workflow deploys changes to content or site source. Publication uses that workflow.

Source: `content/health/live-to-100.md`; navigation: `content/series/live-to-100.yml`; presentation: `compound/site/templates/series_article.html`; styles and interaction: `compound/site/static/live-to-100.css` and `live-to-100.js`. Evidence and source limitations are in `claim-ledger.md`, with the Eurostat response archived alongside it. The original follow-on outlines are retained as the editorial plan for the three full articles now authorised.

## Verification and limitations

The pre-publication draft passed 51 Python tests, 17 direct JavaScript arithmetic/validation checks, JavaScript syntax and patch whitespace checks. Static HTML checks covered headings, IDs, anchors, internal routes, input labels, alt text and dimensions. Six principal colour pairs exceeded 7:1 contrast. Draft fixtures explicitly restore draft status independently of the production article.

The cloud browser rejected the local preview and file URLs under its URL policy, so the draft did not receive browser screenshot, mobile, keyboard, zoom or screen-reader validation. No workaround was attempted. These remain limits of the draft review, rather than a claim of full accessibility conformance. Public deployment and live-page checks are recorded separately when completed. No clinical or financial specialist review is claimed.

## Local review

`compound preview-file content/health/live-to-100.md --output review` creates a separate noindex review build. `compound build` creates production output. Preview generation protects source and production folders. Publication requires an explicit date and published status; route-conflict guards prevent accidental duplicate or reserved routes.
