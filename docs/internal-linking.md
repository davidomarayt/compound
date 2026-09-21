# Internal linking: articles ↔ tools

Compound uses explicit editorial metadata rather than automatic keyword linking.

## For every new article

1. Ask whether an existing tool genuinely helps the reader act on or personalise the article.
2. If yes, add `related_tools` to the article front matter using the exact tool slug.
3. Use zero links when no tool materially improves the article. Most articles should need no more than 1–3; the build rejects more than 4.
4. Add an inline contextual link in the article body only when it reads naturally in the sentence. Do not insert links merely because a keyword appears.
5. Do not create geographic or keyword variants of the same article/tool purely to increase internal-link volume.

Example:

```yaml
related_tools:
- mortgage-overpayment-calculator
- mortgage-switch-calculator
```

The build validates every slug. It then renders a “Useful tools” module on the article and automatically adds the article to the related-reading section of each nominated tool. This makes the relationship bidirectional from one metadata declaration.

## Editorial standard

Prefer links that continue the user's question:

- explanation → personal calculation;
- calculation → evidence/context;
- broad guide → specialised tool;
- tool → relevant article explaining assumptions or limitations.

Avoid links where the relationship is only a shared word or broad pillar.

## Existing exceptions

BMI and the Compound Interest Calculator are bespoke legacy pages rather than entries in `content/tools.yml`, but they are included in the same linkable catalogue under:

- `bmi-calculator`
- `compound-interest-calculator`

## Publishing check

Before publishing a new article:

- sources and claims reviewed;
- related tools considered;
- `related_tools` added only where useful;
- any inline tool link uses descriptive anchor text;
- build/tests pass;
- live deployment verification passes.

This is the default Compound publishing methodology going forward.
