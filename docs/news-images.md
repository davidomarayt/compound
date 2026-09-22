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
