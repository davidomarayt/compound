# Compound social publishing

Compound can publish social posts directly from GitHub Actions when a new article is published.

## How it works

1. An article is published in `content/**`.
2. Its front matter contains a `social` block.
3. The `Publish social posts` GitHub Action detects a new publication.
4. The same article is posted to the enabled social platforms.
5. Ordinary edits to an already-published article do not trigger another social post.
6. A specific article can be posted manually with the workflow's `article_path` input.

The workflow starts in **dry-run mode** unless the repository variable `SOCIAL_DRY_RUN` is explicitly set to `false`.

## Article front matter

Use this structure:

```yaml
social:
  enabled: true
  x:
    enabled: true
    text: >-
      Ireland's Rent Tax Credit is increasing in Budget 2027.
      The new amount is not confirmed yet. Here is what renters need to know.
  linkedin:
    enabled: true
    text: >-
      Ireland's Rent Tax Credit will increase in Budget 2027, but the final
      amount has not yet been announced. We have broken down the current
      €1,000 individual credit, eligibility and what different increases
      would mean in practical euro terms.
  instagram:
    enabled: true
    caption: >-
      Rent Tax Credit update: an increase is confirmed for Budget 2027,
      but the new maximum has not yet been announced. Our guide explains
      the current credit, who qualifies and what to watch on Budget day.
    image_url: https://compound.ie/path-to-public-social-image.jpg
```

The workflow appends the canonical Compound article URL automatically.

## GitHub configuration

Open the repository's:

**Settings → Secrets and variables → Actions**

Add only the credentials for platforms you want to use. Do not place tokens in article files or commit them to the repository.

### Repository variables

- `SOCIAL_DRY_RUN` — keep `true` while testing; set to `false` to publish.
- `LINKEDIN_VERSION` — current supported LinkedIn Marketing API version in YYYYMM format.
- `META_GRAPH_VERSION` — current supported Meta Graph API version, for example `vXX.X`.

### Repository secrets

#### X
- `X_ACCESS_TOKEN` — user-context token authorised to create posts.

#### LinkedIn
- `LINKEDIN_ACCESS_TOKEN`
- `LINKEDIN_AUTHOR_URN` — member or organisation URN.

For a Company Page, the authenticated LinkedIn member must have the appropriate Page role and posting permission.

#### Instagram
- `META_ACCESS_TOKEN`
- `INSTAGRAM_USER_ID`

Instagram publishing also requires a public `image_url` in the article's social front matter.

## Approval before posts go live

The workflow uses the GitHub environment:

`social-production`

For an approval gate, create that environment under:

**Settings → Environments → social-production**

and add a required reviewer.

That gives a useful first-stage workflow:

**Compound article published → social run waits → reviewer approves → posts go live.**

When the process is proven, the approval requirement can be removed for fully automatic publishing.

## Editorial rule

Social copy should not just repeat the headline.

Each platform should give the useful point immediately:

- **X:** short, fast, key number or development.
- **LinkedIn:** slightly more analytical and explanatory.
- **Instagram:** simple visual headline plus concise practical explanation.

Every social post should send the reader into the article, and the article should then lead into relevant evergreen guides and tools.
