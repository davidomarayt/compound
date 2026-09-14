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
- [ ] Add the AdSense publisher ID and generate `ads.txt` once Google provides the `ca-pub-…` value.
