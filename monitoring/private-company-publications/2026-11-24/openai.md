# OpenAI and Cisco's Shirudo: Can Live Security Protection Reduce the Cost of Waiting for a Patch?

**HELD — not published.** Proposed meta description: OpenAI and Cisco introduced Shirudo on 23 November. Examine the economics of temporary Linux runtime protection, testing, outage costs and the limits of the demonstration.

On 23 November, [OpenAI and Cisco introduced Shirudo](https://openai.com/index/introducing-shirudo/), an open-source project intended to protect running Linux workloads during the period between discovering a vulnerability and installing a permanent patch. Its commercial relevance is not primarily the price of another security tool. It is the cost of running infrastructure that cannot be taken offline whenever a software weakness is identified.

In a controlled demonstration, a safeguard generated using Codex prevented an attempted exploitation of an Elasticsearch service while that service remained running. Cisco's [technical account of the project](https://isovalent.com/blog/post/cisco-openai-shirudo/) is a second primary source for the demonstration, but both organisations are participants in the project rather than independent evaluators.

The result is promising evidence about one test. It is not evidence that an AI agent can safely protect any vulnerable application, that all emergency maintenance is avoidable or that the software is ready for deployment across a regulated enterprise.

## The gap between discovery and remediation

Finding a vulnerability and repairing every affected production service are different jobs. A permanent fix may require a release from an upstream supplier, compatibility testing, an approved maintenance window and an orderly rollout. Even when a fix exists, the organisation may be reluctant to restart a critical application during its busiest period.

This creates an economic trade-off. Operating a vulnerable service exposes the business to risk. Interrupting it for emergency maintenance can also disrupt customer activity, production or internal operations. A temporary runtime safeguard has potential value if it makes that interval safer without causing an equivalent disruption.

Shirudo is designed around targeted protections that operators can evaluate before authorising deployment. The companies describe signed safeguards, verification controls and the use of Linux runtime mechanisms. These measures support oversight, but do not replace application-level testing or organisational change control. A safeguard that rejects a legitimate request can create its own incident.

## Where OpenAI fits into the economics

The collaboration gives OpenAI's coding models a potential role in a recurring infrastructure problem: preparing and assessing temporary protections as new vulnerabilities emerge. Cisco contributes security and infrastructure experience. OpenAI describes the runtime as BSD 2-Clause licensed, with BPF programs offered under BSD and GPL terms.

An open-source runtime does not itself establish a new stream of subscription revenue for OpenAI. An enterprise might choose to pay for model usage, support, managed infrastructure or integration work around an open project. It might instead use different models, operate the system internally or decide that the cost and risks do not justify adoption.

For a privately held business, a project announcement is not a financial statement. Neither announcement supplies a contract value, projected profit, a customer rollout count or an independently measured reduction in incidents. The sensible investment question is whether the project can make reliable security operations less labour-intensive and improve demand for supporting services, rather than assigning an invented valuation to a software repository.

## An illustrative maintenance-cost model

Imagine an organisation with 25 affected services. Assume each service interruption has an internal economic cost of €200 per hour, and emergency maintenance would otherwise require eight hours of disruption per service. This is a deliberately simplified scenario, not a measurement of OpenAI, Cisco or any Shirudo customer.

| Illustrative case | Calculation | Estimated cost |
|---|---:|---:|
| Emergency intervention | 25 × 8 × €200 | €40,000 |
| Later intervention after temporary protection | 25 × 2 × €200 | €10,000 |
| Additional temporary-protection testing and operation | Assumed | €12,000 |
| Difference before other costs and risks | €40,000 − €10,000 − €12,000 | €18,000 |

The €18,000 difference is only a conditional cost comparison. It assumes the temporary protection really does permit a shorter interruption later. It excludes the potential cost of an unsuccessful safeguard, incident response, additional compute, and any effect on service quality. It is not a claim that temporary protection actually makes a permanent patch take less time.

If the scheduled intervention still required eight hours, the hypothetical runtime layer would add €12,000 of expense rather than produce a direct outage saving. Its value would then depend on the reduction in risk during the waiting period. That is why a sensible trial needs measured exposure and reliability, rather than a simple count of generated protections.

## What an enterprise pilot should measure

A meaningful evaluation should track how long it takes from vulnerability disclosure to approved temporary protection; the proportion of affected services covered; false blocking of legitimate requests; operational overhead; and the time required to remove the temporary measure after permanent remediation.

Different workloads should be assessed separately. An internal service with a small user population is not a substitute for evidence on a critical payment system. The same operator should also retain a record of who approved a protection and how a failed intervention can be reversed. A demonstration should not be confused with a security certification.

The strongest business case may emerge in organisations where the cost of waiting for maintenance is material and production change controls are mature. The least attractive case is one in which the temporary layer introduces complexity but the organisation already patches quickly.

For wider context, see [Compound's OpenAI company research](/companies/openai/) and [our earlier analysis of the Hacktron security partnership](/wealth/openai-hacktron-agent-security-third-party-risk/). Shirudo is a distinct question: how to manage the cost of exposure between discovery and permanent remediation.

*Compound Research draft; research checked 24 November 2026. All financial figures are illustrative, not forecasts or disclosed company results.*

## Source record
- https://openai.com/index/introducing-shirudo/
- https://isovalent.com/blog/post/cisco-openai-shirudo/
