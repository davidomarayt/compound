# Compound to-do list

## Analytics and search measurement

- [x] Create a Google Analytics 4 property named **Compound**.
- [ ] Set the GA4 reporting timezone to **Ireland** and currency to **EUR**.
- [x] Create a GA4 web data stream for `https://compound.ie` with Enhanced Measurement enabled.
- [x] Copy the `G-XXXXXXXXXX` Measurement ID and provide it for implementation.
- [x] Add the GA4 tag to the shared site template with analytics storage denied by default.
- [x] Configure Google Consent Mode for analytics visitors in Ireland and the EEA. Replace or integrate this control with a Google-certified CMP before AdSense personalised ads are enabled.
- [x] Verify page-view collection in GA4 Realtime after deployment.
- [x] Add editorial events for article-depth milestones at 25%, 50%, 75% and 90%.
- [x] Track source-link clicks, copy-link actions and use of interactive tools without collecting form values or personally identifying information.
- [ ] Confirm article reporting under **Reports → Engagement → Pages and screens**.
- [x] Create a Google Search Console Domain property for `compound.ie`.
- [x] Verify the Search Console property through the domain's DNS record.
- [x] Submit `https://compound.ie/sitemap.xml` in Search Console.
- [ ] Check indexing, search queries, article clicks and impressions after sufficient data accumulates.
- [x] Add the AdSense publisher ID and generate `ads.txt` once Google provides the `ca-pub-…` value.


## Content roadmap

- [ ] Build a **GLP-1 in Ireland hub** that organises the full cluster: access, cost, HSE/Medical Card coverage, treatment duration, stopping/weight regain, side effects, pregnancy, retatrutide and future GLP-1 articles. Link every GLP-1 article back to the hub and surface the GLP-1 Cost Calculator prominently.

## SEO growth sprint — 13 October 2026

- [x] Correct the €600 SEAI battery grant evergreen/news page to current open scheme and retain canonical URL.
- [x] Optimise metadata and targeted content for Salary-to-Hourly and Fuel Cost calculators, PIA, Irish standard drinks and Living Wage article.
- [x] Add relevant links from insurance guides into /insurance/ and from EV guide into /solar/; keep existing solar links in energy articles.
- [x] Audit sitewide, consent-gated solar_journey_click event; preserve single event per qualifying internal link click.
- [x] Add separate consented solar_installer_enquiry_submitted event for completed B2B FormSubmit enquiry; do not call this a homeowner lead.
- [x] Add automated SEO regression tests and document measurement/indexing checklist in docs/seo-growth-sprint-2026-10-13.md.
- [ ] Verify GA4 registration of source_path, destination_path, destination_step, journey_origin, source_type, link_area, audience; test event delivery/DebugView. **Blocked:** GSC Wizard subscription expired; Supermetrics GA4 not authenticated on 13 Oct 2026.
- [ ] Inspect Solar and Insurance hub URL indexing/canonicals in Google Search Console after connecting an active integration; verify sitemap status. **Blocked:** GSC Wizard subscription expired.
- [ ] Compare 14-day and 28-day post-change query-page CTR, clicks and position against pre-change data once reporting matures.
- [ ] Research an original, non-overlapping solar roof orientation guide (east/west vs south) with verified SEAI/PVGIS data and a pinned hero image before publishing.
- [x] Confirm latest GitHub Pages build and deployment succeeded (commit 23a83b377f530308c732bedd0761c39810135cb4); CI regression tests passed.
- [x] Verified GitHub Pages build, live URL checks, and solar mobile audit on prior SEO deployment (2a097fed738298c3cbd584caa06ed59953ee5913). Re-check after the new roof-orientation article and updated QA workflow deploy.


## New solar orientation evergreen — 13 October 2026

- [x] Check topic index/inventory; an east-versus-west roof-specific guide was not present.
- [x] Publish SEAI/JRC-grounded east- vs west-facing guide with irradiation visual, example economics, PVGIS instructions, approved Pexels image and canonical internal links.
- [x] Add specialist guide to Solar Hub and relevant evergreen solar pages.
- [x] Add automated tests and live build gate for the new guide, graph and pinned roof photo.
- [ ] Confirm the latest GitHub Pages deployment passes all checks, including the new photo. Check latest run at https://github.com/davidomarayt/compound/actions/workflows/site.yml.
- [ ] Re-test mobile render and hero/social image on the live specialist page.

## Performance follow-up

- [ ] Lighthouse: mortgage-calculator recorded 940ms TBT versus 350ms threshold in CI (13 Oct). Configuration updated to take three runs without relaxing the 350ms limit; determine whether this is noise or a persistent regression. If persistent, profile main-thread tasks and fix actual bottlenecks.
