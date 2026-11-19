---
title: "OpenAI's Astra for Law Leads a Legal AI Benchmark. Why Does It Still Miss Four in Five Tasks?"
seo_title: "Astra for Law 6.2: Benchmark Results, Legal AI ROI and Risks"
slug: openai-astra-law-legal-benchmark-reliability-economics
pillar: wealth
canonical_path: /wealth/openai-astra-law-legal-benchmark-reliability-economics/
publication_status: published
date: '2026-11-19'
research_checked: '2026-11-19'
editorial_review_status: pending
summary: "OpenAI's 17 November update gives Astra for Law wider enterprise access and stronger legal scores. A 20.8% all-pass rate shows both its commercial promise and limits."
meta_description: "Astra for Law led a legal AI benchmark at 20.8% full credit. We examine hallucinations, token economics, human review and enterprise adoption."
tags: [wealth, private-company, company-research, company-openai, openai, legal-ai, law-firms, model-evaluation, enterprise-ai]
hero_image_url: https://upload.wikimedia.org/wikipedia/commons/f/f8/Supreme_Court_from_Library_of_Congress.jpg
hero_image_alt: "United States Supreme Court seen from the Library of Congress in January 2023; archival photo, not OpenAI's November 2026 release"
hero_image_credit: "Packer1028 / Wikimedia Commons, CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/), 13 January 2023 archival photograph, cropped"
hero_image_source: https://commons.wikimedia.org/wiki/File:Supreme_Court_from_Library_of_Congress.jpg
require_pinned_hero: true
image: /static/images/evergreen/openai-astra-law-legal-benchmark-reliability-economics.jpg
social_image: /static/images/evergreen/openai-astra-law-legal-benchmark-reliability-economics.jpg
image_alt: "United States Supreme Court viewed from the Library of Congress; real archival image unrelated to the new model"
image_credit: "Packer1028, Wikimedia Commons, CC0 1.0; 13 January 2023, adapted crop"
image_source: https://commons.wikimedia.org/wiki/File:Supreme_Court_from_Library_of_Congress.jpg
sources:
- title: "OpenAI — Astra for Law leads in legal intelligence, 17 November 2026"
  url: https://openai.com/index/astra-law-6-2/
- title: "OpenAI — Introducing GPT-6.2 Astra and Sol, 17 November 2026"
  url: https://openai.com/index/introducing-gpt-6-2-astra-sol/
- title: "Wikimedia Commons — Supreme Court archival image, CC0"
  url: https://commons.wikimedia.org/wiki/File:Supreme_Court_from_Library_of_Congress.jpg
---
**OpenAI's updated Astra for Law is a useful case study in the difference between winning an AI benchmark and safely finishing professional work.** Its specialist legal configuration ranks first on a demanding test, but it meets *every* requirement on only about one in five assignments. Firms considering AI procurement should judge the whole reviewed workflow, not the leaderboard position.

On **17 November 2026**, OpenAI [announced a new Astra for Law configuration](https://openai.com/index/astra-law-6-2/) built on GPT-6.2 Astra, with a specialised search index and legal-research instructions. All ChatGPT Enterprise customers can **request** access through the Trusted Access Program; access is not automatically enabled for every subscriber. The company also offers a request route for API use. OpenAI disclosed no standalone Astra for Law sales, number of paying users, contractual fee schedule or measured client profit uplift.

## First place does not mean ready for unsupervised legal advice

The headline result is **20.8% full credit** on Harvey's LAB-AA benchmark, ahead of 15.0% for general GPT-6.2 Astra and 13.1% for Muse Wonder Full. LAB-AA tests 120 professional assignments across 24 legal areas. Full credit requires every tested requirement to be satisfied without a material unsupported claim. Put another way, **79.2% of assignments did not receive full credit** under this demanding definition.

That does not mean 79.2% of outputs are worthless or wholly wrong. Many may be useful drafts. It does mean a firm cannot infer from the leading score that four out of five complicated legal tasks can now be delegated end to end without independent checking.

OpenAI reports **0.03 material hallucinations per assignment**, versus **0.59** for Claude Opus 5.5 in the comparison. The numbers are averages within that particular evaluation, not probabilities that a customer's next legal document will contain an error. Benchmark prompts, tested model versions, available tools and instructions all matter. Companies should obtain task-level and jurisdiction-level evidence before transferring the figures to their own practice.

## The business case is accepted work, not draft volume

Legal AI has two potential economic channels. First, research and first-draft preparation may require fewer junior hours. Second, better-prepared work could improve turnaround and enable lawyers to spend more time on judgement, client meetings and negotiation. Neither benefit is guaranteed, and neither is identical to a reduction in employment costs.

Consider a purely **illustrative** 100-matter pilot. Suppose ordinary preliminary research takes three hours per matter. A legal agent takes 45 minutes to run and requires 90 minutes of lawyer review, source checking and correction. That is **2.25 hours per matter**, or **75 minutes less** than the existing three-hour process. Across 100 matters, the capacity released would be **75 hours**. At an illustrative fully loaded rate of €120 per hour, the gross capacity equivalent is **€9,000**.

These figures are editorial assumptions, **not measurements from OpenAI, Harvey or law firms**. Change the review burden to 2.5 hours and the AI workflow becomes slower than the original process even before software charges and training. Savings also depend on whether recovered hours are sold, used productively or actually eliminate an expense.

Crucially, the LAB-AA **20.8% full-credit score must not be multiplied by the hours illustration** to predict acceptance. A firm's matters may not resemble the test, and human checking can rescue partial outputs. The right operational evidence is how many deliverables a named reviewer accepts, with how many errors, in what total time.

## Does a specialist configuration justify its premium?

OpenAI's legal release reports about **64,000 output tokens per assignment** for Astra for Law on LAB-AA, compared with about **139,000** for the best-scoring non-OpenAI configuration mentioned. The general GPT-6.2 Astra API list price is **$8 per million input tokens** and **$40 per million output tokens**, with **$0.40 per million cached input tokens**, according to OpenAI's [model announcement](https://openai.com/index/introducing-gpt-6-2-astra-sol/).

At the *general* $40-per-million output rate, 64,000 output tokens would cost **$2.56** for output alone, before input, search tools, other services, retries or any different product-specific terms. **That is not an Astra for Law quote:** the legal configuration is access-controlled, and OpenAI did not publish a distinct all-in legal-service price in this release.

The arithmetic is relevant because a lower token bill can be overwhelmed by the expensive part of law: supervision. If a 20-minute review is required, the lawyer's time can outweigh the underlying model output bill by orders of magnitude. A procurement comparison should therefore include approved use cases, staff review cost, access terms, data handling, auditability and the cost of a consequential error.

## The legal index is an asset, but coverage is not accuracy

OpenAI says its specialist index grew **34% since September**, adding more than **80 million URLs** and reaching **over 310 million**. The company also says the index covers more than 99.9% of published US precedential case law and now incorporates material from the UK, Australia and Canada.

Coverage can improve the chance of retrieving an important authority; it cannot by itself establish that the model correctly applies it, distinguishes binding from persuasive precedents or notices that a statute has changed. Irish practitioners should be particularly careful: UK and US legal coverage is not proof of comprehensive Republic of Ireland law or practice requirements. OpenAI has not disclosed a separate Irish-law benchmark for this configuration.

The second evaluation, Vals AI's Legal Research Bench, reported full-credit answers on **112 of 208** questions, or **53.8%**, on 16 November. That result is a different task set from LAB-AA's 20.8%. Presenting the two percentages as a single performance series would be misleading.

## Trusted Access is a commercial funnel, not a sales disclosure

Extending the ability to request access from a handful of pilot firms to all Enterprise customers potentially increases the addressable sales funnel. But a request is not approval, adoption, usage growth or a renewal. Model vendors benefit only when law firms see durable advantages after training, governance and information-security work.

A responsible legal rollout begins with low-risk internal research where every source can be inspected. Measure elapsed time, total staff hours, error severity, cited-source fidelity and acceptance by an accountable lawyer. Exclude sensitive client materials until confidentiality and retention requirements are explicitly resolved. Courts and regulated clients, not model leaderboards, ultimately define the consequences of a mistake.

**Our assessment:** a specialist legal search layer may let OpenAI sell workflows rather than undifferentiated tokens. Its current disclosed scores support a serious, controlled pilot—not a claim that the practice of law can be safely automated. Nor do they prove a particular revenue figure for privately held OpenAI.

For broader context, compare the [GPT-6.2 launch and pricing analysis](/news/openai-gpt-6-2-astra-sol-pricing-performance-2026/), our [enterprise procurement economics](/wealth/openai-aws-marketplace-enterprise-procurement-economics/) and the [OpenAI research hub](/companies/openai/). Neither benchmark performance nor the calculations above are personalised legal or investment advice.

*Research checked 19 November 2026; product announcement dated 17 November. Numerical workflow scenarios are hypothetical. Photo: Packer1028, United States Supreme Court seen from the Library of Congress, 13 January 2023, CC0; archival and unrelated to the model announcement.*