# Automatic images for Compound News

Every published News article must have an image.

## Image order

1. **Pexels photo** — when the repository secret `PEXELS_API_KEY` is configured.
2. **Compound branded fallback** — generated automatically if Pexels is unavailable or no key is configured.

The News pipeline does not scrape photographs from newspapers, RSS feeds or source pages.

## Why Pexels

The Pexels API provides free programmatic access to its photo library. Pexels content is available for commercial use under the Pexels licence. Compound stores the photographer name and Pexels photo-page link in each article so visible credit can be rendered below the image.

The pipeline downloads:
- a 1200 × 627 landscape crop for the website / Open Graph image;
- an 800 × 1200 portrait crop for Instagram.

## One-time setup

Create a Pexels API key and add it in:

**GitHub → compound → Settings → Secrets and variables → Actions → New repository secret**

Name:

`PEXELS_API_KEY`

Until that secret exists, News still publishes safely with a unique branded fallback graphic.

## Choosing the right image

When creating a News article, add a deliberate search phrase:

```yaml
news_image_query: 'US dollars finance interest rates economy'
```

Keep it visual and generic rather than trying to reproduce the event itself.

Examples:
- Fed decision → `US dollars finance interest rates economy`
- ECB decision → `euro currency banking finance`
- Irish housing data → `Ireland houses homes property`
- medicines story → `medical research laboratory medicine`
- wellbeing/community → `Ireland community outdoors wellbeing`

For sensitive health stories, prefer neutral scientific/clinical imagery rather than implying that a photographed person has the condition discussed.

## What the workflow writes

The image script adds:

```yaml
image: /static/images/news/<slug>.jpg
image_alt: ...
image_credit: 'Photographer on Pexels'
image_source: https://www.pexels.com/photo/...
social_image: /static/images/news/<slug>-portrait.jpg
```

The article template already shows the photo credit.

Instagram automatically uses `social_image` if the article does not specify a separate Instagram image URL.

## Enforcement

The site build now fails if a **published News article** reaches the builder without an image. Because the image step runs before the site build and has a fallback, this acts as a genuine guarantee rather than an editorial reminder.

Evergreen Health, Wealth and Happiness articles are not forced to use generic images.


## Stock research and company-specific editorial photography

Published company research and stock news (tagged `stocks`, `company-research`,
or `stock-<ticker>`) must use an editorially checked photograph of the
actual company, product, facility, or identified business subject. A generic
calculator, paperwork, boardroom, or finance/market stock photo is never an
acceptable substitute.

Pin the approved image explicitly in front matter, including attribution:

```yaml
tags: [stocks, tesla, spacex]
hero_image_url: "https://www.nasa.gov/wp-content/uploads/2026/10/55563235995-2bae0fafbc-o.jpg"
hero_image_alt: "SpaceX Falcon 9 rocket launches from Cape Canaveral on 1 October 2026."
hero_image_credit: "NASA / Joel Kowsky (public domain)"
hero_image_source: "https://www.nasa.gov/image-article/nasas-spacex-crew-13-launches/"
```

Alternatively pin an individually reviewed `pexels_photo_id`. Check licensing
and ensure that the photo really depicts the company. The image pipeline
**blocks stock editorial publication** if the pinned source cannot be
downloaded or if it would otherwise fall back to an unrelated photo. Source
attributions should identify the actual photographer/rights holder.

Automated SEC earnings reports are currently a separate data-first format:
their charts are company-specific, but their pages intentionally do not
attach unsourced or mismatched generic photographs.
