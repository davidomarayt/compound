# Mag 7 automated research pilot (16 October – 12 November 2026)

The Mag 7 Research Desk runs at 08:17 UTC on the default branch
`claude/clever-babbage-uibieq`. GitHub may delay scheduled runs. The deterministic
rotation is Tesla, Microsoft, Nvidia, Apple, Amazon, Alphabet, Meta, repeated
for four weeks. Dates outside the pilot do not publish.

## Secure credential configuration

Open https://github.com/davidomarayt/compound/settings/secrets/actions and choose
**New repository secret**. Name it exactly `ANTHROPIC_API_KEY` and enter an
Anthropic API key authorised for Compound's research and editorial API usage.
Use an existing authorised key if available, or create one in the Anthropic
Console with API billing/credits and access to the configured models and web
search. Never put its value in chat, repository files, issues or workflow logs.
A chat subscription or the GitHub token is not a substitute for this API key.

This job does not select a GitHub environment: a secret stored only in an
environment will not reach it. Configure the repository secret above. Optional
repository Actions variables `MAG7_MODEL` and `MAG7_EDITOR_MODEL` override the
script's model defaults. Both generation and independent review require access.

## Publication gates and observable failures

The publisher reads SEC-backed financial profiles, checks existing topics,
researches and drafts using web search, validates sources and article structure,
and runs a separate editorial review. It downloads a company-specific approved
Unsplash photograph with attribution and archival context. No synthetic images,
filler or generic fallback is permitted. The workflow checks the rendered photo,
SEO/social metadata and complete site build before committing, then dispatches
`site.yml`. A commit or successful dispatch is not proof of a live deployment.

Missing credentials and any research/editorial/photo errors write a skipped audit
and return nonzero, making Actions fail visibly. Every attempt uploads its audit
and copies it into the run summary. The original date/ticker issue remains a
historical record; subsequent attempts are available in their run summaries and
artifacts even if that issue already exists. An editorial rejection is a reason
to investigate or skip, never to bypass checks.

## Recover the missed assignments

The 17 October Microsoft and 18 October Nvidia attempts skipped because the key
was unavailable (issues #44 and #45). After adding the secret and applying these
fixes:

1. Open Actions → **Mag 7 Research Desk** → **Run workflow**.
2. Select `claude/clever-babbage-uibieq`, set `date` to `2026-10-17`, and run it.
3. Inspect research, independent review, image/build and commit results. Follow
   the dispatched `site.yml` run and check the live article, cover and social image.
4. Repeat with `date` set to `2026-10-18` after the first attempt completes.
5. Reconcile the original issues only once the actual outcome has been checked.

Use a new manual dispatch with an explicit date, not a rerun of an old scheduled
job: scheduled runs have no date input and the script defaults to the current
date. Recovered articles retain deterministic assignment-based slugs and
`assignment_date`, but use the current date for publication and review; research
uses currently available evidence. Existing canonical article files cannot be
overwritten. Duplication or insufficient evidence may correctly block recovery.

Do not regard the workflow as operational until a credential-backed run passes
and its page is verified live. After the pilot, review indexing, clicks,
stock-page referrals, engagement and ad earnings before extending it.
