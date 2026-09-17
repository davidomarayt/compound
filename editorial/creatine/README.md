# Creatine article — publication record

Research checked: 17 September 2026. The user explicitly instructed: “Remove the calculator in the article it doesnt add anything. And then publish”. Publication is authorised following removal of the calculator.

## Files

- Article: `content/health/creatine-benefits-dosage-safety-ireland.md`
- Styles: `compound/site/static/creatine.css`
- Article-specific asset loading, draft presentation and prose class: `compound/site/templates/article.html`
- Built preview: `review/creatine-draft/preview/creatine-benefits-dosage-safety-ireland/index.html`
- Standalone review copy: `/workspace/scratch/8959693390a2/Compound_Creatine_Review.html`
- Persistent review file: `libfile_9a550fdef74481918410e2b9f75242e3`, version 0.

The article is marked `draft: false` and `publication_status: published`, dated 17 September 2026, with the explicit approval recorded in front matter. The linked review copy is the historical pre-approval draft and includes the now-removed calculator. The public article is the current version.

## Evidence boundaries

The article contains 18 source entries, with references beside the relevant claims. Numerical study claims were checked against original abstracts or full text. General protocols were checked against the ISSN position stand, NIH guidance and the original loading study. Current Irish sports guidance was checked on Sport Ireland's page; the older linked PDF was not treated as current guidance.

| Topic | Evidence used | Editorial boundary |
| --- | --- | --- |
| Muscle and strength | 2024 reviews, PMIDs 39074168 and 39519498 | Lean mass includes water; group averages are not individual promises. Limited female evidence does not prove a lack of benefit. |
| Adult dosing | PMID 8828669; ISSN 2017, PMC5469049 | Commonly studied monohydrate protocols, 3–5 g daily; loading optional. No individual prescription or children's protocol. |
| Timing and caffeine | PMC11703406 | No established narrow timing window; caffeine evidence is mixed. |
| Postmenopausal women | PMID 42141930 | Modest muscle/strength findings with training; no overall bone-density benefit established. |
| Kidney results | PMIDs 42035842 and 42507286 | Reassuring healthy-adult evidence, with duration limitations. Creatinine-based estimates and measured filtration can differ. Never dismiss an abnormal result without clinical interpretation. |
| Safety and special populations | PMC12702719; LactMed NBK501853; Sport Ireland | Healthy-adult findings do not automatically apply to kidney disease, pregnancy, breastfeeding or minors. |
| Hair loss | PMID 40265319 | 38 men completed a 12-week trial with no significant group differences; no lifetime guarantee. |
| Cognition | PMIDs 39070254, 42075005 and 40971619; EFSA 2024.9100 | Mixed outcomes, small trials and observational evidence. No dementia-prevention, driving-safety or sleep-replacement claim. EFSA did not establish the submitted cognitive health claim. |
| Buying in Ireland | Monohydrate review PMC7871530; current Sport Ireland supplement guidance | No brand endorsement, current retail-price claim or claim that batch testing eliminates risk. |

## Removal and verification

The cost comparison section, calculator script, script loading and calculator-only styles were removed at the user's request. The summary and search description were updated to remove promises of a calculator. The dosing comparison table, product-selection guidance and all 18 sources remain.

Pre-publication checks cover the full site build, article structure, references, internal destinations, absence of the removed tool and its assets, publication metadata and inclusion in homepage, health, search, RSS and sitemap. Live verification follows deployment.

The `creatine-guide` class belongs on the template's existing `.article-prose` element. Keep the article body as Markdown without an enclosing HTML wrapper.

## Publication handover

Base commit at drafting: `06996ed184be765d0331901509098b96b536b711` on `claude/clever-babbage-uibieq` in `davidomarayt/compound`.

The GitHub Pages workflow has no branch filter. Pushing the article or relevant site files on a separate branch can still trigger a deployment; no draft branch has been pushed.

Publish the article and remaining assets together after checking against the current remote state. Verify the deployed page, index/search/feed/sitemap and canonical metadata. No calculator asset should be deployed. Do not sign into Search Console: the user previously stopped that task.
