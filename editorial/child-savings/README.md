# Child savings article — publication record

Status: approved for publication by David O’Mara with the explicit instruction “Publish” on 2026-09-17. Research checked 2026-09-17.

User requested particular care with inheritance tax and the handover at age 18 across different investments and ownership arrangements.

## Files

- `content/wealth/saving-for-your-child-ireland.md`: article, source links, draft metadata, calculator markup and accessible fallback.
- `compound/site/static/child-savings.js`: calculator, chart and validation.
- `compound/site/static/child-savings.css`: article comparisons and calculator styling.
- `compound/site/templates/article.html`: conditional assets and explicit draft presentation.

The approved public article is at `/wealth/saving-for-your-child-ireland/` and is included in the homepage, Wealth archive, search, feed and sitemap. The earlier standalone review HTML remains a historical draft.

## Editorial boundaries

- Separate beneficial ownership, legal control and liquidation; age 18 is not a universal tax event.
- A genuine completed bare-trust gift is different from a parent's promise to give their own savings later. Section 567 supports CGT look-through for absolute beneficial ownership; it does not classify every fund or policy or validate a particular deed.
- CAT uses the recipient's shared group threshold across relevant donors. The annual small-gift exemption requires a gift in the relevant year; it cannot be backdated and does not apply to inheritances.
- Ordinary company shares, funds under the relevant Irish/offshore regime, and life policies have different return-tax rules. The article does not classify a particular ETF.
- Gifts, death, sales, deemed disposal and assignments can be different events. Do not generalise the ordinary-share date-of-death cost basis to investment funds or policies, or to reaching age 18.
- Product/provider rules govern practical handover steps; no universal automatic payout is claimed.
- Discretionary-trust charges have timing rules and exemptions. A later-access requirement needs proper advice before gifting.
- Trust registration and the tax treatment of a minor's settled income require separate consideration.

## Principal source map

Full links are in the article frontmatter and inline. The source list contains 19 entries.

| Topic | Primary evidence |
|---|---|
| CAT rate, gifts near death | Revenue CAT overview |
| Annual €3,000 exemption, filing trigger | Revenue Small Gift Exemption |
| Group A €400,000; B €40,000; C €20,000; aggregation | Revenue thresholds, groups and aggregation pages |
| Absolute beneficial ownership; trustee transfer | Revenue Finance Act 2025 Notes for Guidance, TCA Part 19, section 567 |
| Minor settlement income and irrevocable accumulations | Revenue TCA Part 31, sections 794–796 |
| DIRT 33% | Revenue DIRT pages |
| State Savings product distinctions | Ireland State Savings product page |
| CGT 33%, €1,270 exemption and inherited acquisition cost | Revenue CGT overview and calculation pages |
| Fund rate 38% from 2026; eight-year events | Revenue TCA Part 27, sections 739B–739G and 747D–747E |
| Policy assignments, death, eight-year events, rate and set-off | Revenue TCA Part 26, sections 730C, 730D, 730F and 730GB |
| Assignment of a child's policy at outset | Zurich Child's Savings Plus page; illustration only, no recommendation |
| Same-event CGT credit against CAT | Revenue CGT/CAT credit page |
| Discretionary-trust charges and timing | Revenue DTT overview and initial-charge page |
| Beneficial-ownership registration | Revenue CRBOT |

## Verification

- 288 independent monthly-loop comparisons against the calculator formula passed, including zero and negative returns and observation ages before contribution start.
- Default €100 per month, 5% effective annual growth: age-18 balances €34,526 from birth; €21,738 from age five; €11,719 from age ten. Values rounded after calculation; all before tax and fees.
- 2% inflation example from birth: €24,173 purchasing power at the same default assumptions.
- CAT example: (€400,000 inheritance minus €303,000 remaining threshold) × 33% = €32,010.
- Share sale example: (€50,000 proceeds minus €30,000 basis minus €1,270 exemption) × 33% = €6,180.90.
- JavaScript syntax and git whitespace checks passed.
- Preview build, unique IDs, input labels, draft metadata, absence of analytics/advertising, internal link destinations and exclusion from published indexes/feed/sitemap passed.
- Initial chart sizing was corrected to reveal the SVG before measuring width; narrow layouts stack result panels and scroll comparison tables.
- Live browser visual verification remains incomplete: the available cloud browser blocked the localhost preview with `net::ERR_BLOCKED_BY_CLIENT`. No visual-pass claim is made.

## Publication

David explicitly approved publication on 2026-09-17 after receiving the complete draft. Publication metadata now records that approval and date. The site is deployed by the existing GitHub Actions workflow on the default branch, `claude/clever-babbage-uibieq`.

Approved URL: https://compound.ie/wealth/saving-for-your-child-ireland/

The earlier standalone review file remains a draft record and is not the public version. Tax rules should be rechecked when the article is substantively updated.
