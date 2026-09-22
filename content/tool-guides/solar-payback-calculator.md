## What this calculator is for

This tool estimates how long a domestic solar PV system could take to recover its net upfront cost through avoided electricity purchases, export payments and, where selected, battery arbitrage.

## Basic and Advanced modes

**Basic** is deliberately solar-only. It keeps the first calculation focused on the quote, grant, array size, expected annual generation, household electricity use, direct self-consumption and import/export rates. Even if an old shared scenario contains EV or battery values, Basic mode does not silently include them.

**Advanced** adds a home-charged EV and/or battery. EV value is based on the grid tariff that solar charging would actually displace. Battery value includes round-trip losses, the export income displaced when surplus is stored, and optional cheap-rate grid charging.

The Advanced results now show the battery's **incremental annual value and battery-only simple payback** against the same solar/EV scenario without a battery. That is often a more useful buying question than looking only at the payback of the combined solar-plus-battery package.

## How to read the result

Payback is not a guarantee. The result is only as strong as the assumptions for generation, self-consumption, import tariff, export rate, battery efficiency and system cost. Compare the solar-only and solar-plus-battery cases separately.

## Worked example

The calculator's default household-demand assumption is **4,200 kWh a year**. Replace it with your own annual usage from bills where possible.

A 4 kWp system qualifies for up to €1,800 under the current SEAI domestic grant structure if the property and applicant meet the conditions. If the post-grant system cost is €7,000 and annual value is €1,000, simple payback is about seven years before degradation, maintenance or tariff changes.

## Irish context

SEAI's 2026 domestic grant is €700 per kWp up to 2 kWp and €200 per additional kWp up to 4 kWp, capped at €1,800. The home must meet current eligibility rules, including being built and occupied before 2021 and having no previous funded solar PV at the MPRN.

## What can change the answer

If you have an **EV**, daytime solar charging can increase self-consumption. If you also have a battery, **night**-rate charging can create a separate arbitrage opportunity, but the price spread must be large enough to overcome round-trip efficiency losses and the battery's capital cost.

Roof orientation, shading, local generation, household demand, daytime usage, export price and future electricity prices all affect value. A battery can increase self-consumption but adds capital cost and efficiency losses.

## Common mistakes to avoid

Do not assume every generated kWh saves the full import price; exported electricity is valued differently. Do not assume a battery automatically improves payback. And do not use grant money in the model unless you actually qualify.

## Related Compound tools

Use the [Electricity Cost Calculator](/electricity-cost-calculator/) for the baseline bill, [Solar + EV + Battery Optimiser](/solar-ev-battery-optimiser/) for a more detailed energy-flow model, and [Whole-House Retrofit Planner](/whole-house-retrofit-planner/) for broader upgrade sequencing.

## Frequently asked questions

### Is a bigger solar system always better?
Not necessarily. Roof space, demand, export value and marginal generation matter.

### Does a battery always pay back?
No.

### Is the €1,800 grant automatic?
No. Eligibility and approval conditions apply.

### Does the calculator model panel degradation?
The main payback result uses the assumptions described and does not fully model every long-term degradation factor.

## Model self-consumption before chasing headline generation

Solar economics depend on what happens to each generated kilowatt-hour. Electricity used in the home can avoid buying power at the retail import rate, while exported electricity earns the export rate available from the supplier. Those two values are not necessarily equal.

That is why self-consumption is a critical assumption. A household with daytime demand, an EV that can charge during solar hours, a heat pump or a well-managed battery may use a larger share of generation behind the meter than a low-daytime-use household.

Advanced mode is designed to expose those assumptions rather than hide them inside a single payback figure.

### The 2026 SEAI grant should be treated as an eligibility input

SEAI's domestic Solar PV grant remains capped at €1,800 in 2026. The published structure is €700 per kWp up to 2 kWp and €200 per additional kWp up to 4 kWp, with the maximum grant reached at 4 kWp.

Eligibility is not automatic. SEAI states that the property needs an MPRN, must have been built and occupied before 2021, and must not previously have received solar PV funding for that MPRN under the scheme. The calculator therefore separates “grant eligible” from system size instead of assuming every installation receives €1,800.

### Battery payback is a separate investment decision

A battery can increase self-consumption and may add value through night-rate charging and tariff arbitrage, but its economics should be tested separately from the panels.

Compare:

- solar without battery,
- solar plus battery,
- and the incremental battery cost versus the incremental annual benefit.

The **battery incremental payback** output is more useful than allowing panel savings to make the battery appear to pay for itself. A battery can be strategically valuable for backup, tariff management or self-sufficiency even where its standalone financial payback is weaker; those non-financial benefits should be kept separate from the pure return calculation.

### Stress-test the quote

Run at least three cases before signing:

- a conservative generation case,
- your central estimate,
- and a favourable case.

Then lower the assumed import rate, export rate or self-consumption percentage and check whether the project still looks acceptable. A proposal that only works under very optimistic tariffs or generation is more fragile than one that remains attractive under conservative inputs.

For broader home-energy sequencing, use the [Whole-House Retrofit Planner](/whole-house-retrofit-planner/) and [BER Energy Cost Calculator](/ber-energy-cost-calculator/).

See SEAI's current [Solar Electricity PV Grant](https://www.seai.ie/grants/home-energy-grants/individual-grants/solar-electricity-grant) guidance for eligibility and 2026 grant values.

## Method and limitations

The tool estimates annual generation from system size and generation-per-kWp, values direct self-use, EV use, battery-delivered energy and exports, subtracts the eligible grant from cost and divides net cost by annual value for simple payback.

### Useful sources

- [SEAI — Solar electricity grant](https://www.seai.ie/grants/home-energy-grants/individual-grants/solar-electricity-grant)
- [SEAI — Individual home energy grants](https://www.seai.ie/grants/home-energy-grants/individual-grants)

## Simple payback is useful, but it is not the whole investment case

A simple payback period answers one question: how many years of current estimated annual savings are needed to recover the net upfront cost?

It does **not** account for the time value of money, financing interest, panel degradation, inverter replacement, maintenance or future tariff changes. A 7-year payback and a 10-year payback therefore should not be treated as precise forecasts.

Solar also has a different risk profile from a financial investment. Much of the benefit comes from reducing future electricity purchases, so the value depends on the electricity price you would otherwise have paid. Export income is a separate revenue stream and can change with supplier rates.

A robust decision should still look attractive when you lower generation slightly, reduce export payments and avoid assuming unusually high future electricity prices.

