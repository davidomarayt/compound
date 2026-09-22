## What this calculator is for

This tool compares how solar generation can interact with household demand, EV charging and a battery. Its purpose is not to find a universally 'optimal' system, but to reveal where each generated kWh goes and what value it creates under your tariff assumptions.

## Basic and Advanced modes

**Basic** compares the available configurations from the same core solar quote, tariff, EV and battery inputs. The more technical assumptions use transparent defaults: 35% direct household solar use, 18 kWh/100 km EV consumption, 10% EV charging losses, 80% home charging, 35% of home-EV demand able to follow solar, 90% battery round-trip efficiency, 60% solar-surplus capture and 3 kWh/day of night charging when that option is enabled.

**Advanced** lets you replace those defaults with your own evidence. It also adds an optional **incremental smart-EV charger/control cost**. Leave that at €0 if the charger is already installed or its cost is outside the decision; include it if the extra hardware is part of the solar/EV investment you are comparing.

The results now expose the **20-year net benefit of each configuration**, not just the payback period and the name of the highest-value scenario. That makes the ranking auditable: you can see how far the modelled winner is ahead of solar only rather than treating the label as a black box.

## How to read the result

Look at **direct self-consumption**, **EV charging**, **battery-delivered energy**, **night-rate arbitrage** and **exports** separately. These flows have different economics.

## Worked example

A solar kWh used directly in the home may avoid a €0.30 import. The same kWh exported might earn a lower export rate. Sending it through a battery can improve timing but incurs round-trip losses and requires the battery capital cost.

## Irish context

Irish smart tariffs increasingly reward timing. CRU notes that time-of-use tariffs vary by period, while dynamic tariffs available from June 2026 can vary half-hourly. EVs and batteries are especially flexible loads, but the best tariff depends on actual usage.

## What can change the answer

Generation, battery size, round-trip efficiency, EV mileage, home-charging share, night rate, export payment and daytime import price all matter. A system that works well for a high-mileage EV household can be poor for a low-use home.

## Common mistakes to avoid

Do not count the same solar kWh twice. Do not assume all battery cycling is 'free' just because the charge happens at night. Include efficiency losses and battery cost. And do not use a generic EV consumption figure if your vehicle is materially different.

## Related Compound tools

Use the [Solar PV Payback Calculator](/solar-payback-calculator/) for the simpler economics, [EV Charging Cost Calculator](/ev-charging-cost-calculator/) for the car alone and [Electricity Cost Calculator](/electricity-cost-calculator/) for the household baseline.

## Frequently asked questions

### Is charging a battery at night always profitable?
No. The price spread must exceed efficiency losses and should be considered alongside battery wear/capital cost.

### Does EV charging increase solar self-consumption?
It can, if charging occurs when solar is available.

### Is exporting bad?
No. Export has value; whether self-use is better depends on import and export rates.

### Does this optimise half-hourly dispatch?
No. It is an annualised planning model.

## Value each kWh by what it replaces

The central optimisation principle is opportunity cost.

A solar kWh used directly in the home can avoid buying one kWh at the applicable import tariff. A solar kWh exported earns the export rate. A solar kWh stored in a battery gives up the export payment in exchange for a later avoided import, after round-trip losses.

The financially best route is therefore not always the route with the highest self-consumption percentage.

### EV charging creates another competing use

An EV can absorb a large amount of household electricity, but timing matters.

If the car can charge overnight on a very low tariff, using midday solar for the EV may save less money than exporting the solar and charging the car later at the cheaper night rate. If the alternative is expensive daytime import, the same solar-to-EV flow can be highly valuable.

Advanced mode lets you model these competing values instead of assuming every solar kWh used on-site is equally valuable.

### A battery needs an incremental test

Do not let panel savings make the battery look profitable.

Run the system without the battery first. Then add battery cost, efficiency, usable capacity and tariff-arbitrage assumptions. The difference between those two scenarios is the battery's **incremental value**.

A battery can still be chosen for resilience, backup or energy-independence reasons, but those benefits should be labelled separately from the financial return.

### Tariff spreads drive arbitrage

Night charging only creates value when the avoided later import is sufficiently more expensive than the night-rate energy used to charge the battery, after losses and any lost export opportunity.

Small tariff spreads can disappear once round-trip losses are included. Large spreads can make smart charging much more valuable.

This is why the optimiser exposes night-rate, import, export and battery-efficiency assumptions rather than using one blended electricity price.

### Optimise the system, not each device in isolation

Solar, EV and battery decisions interact. A larger PV array can increase export. Adding an EV can absorb some of that surplus. Adding a battery can shift more energy into evening hours. A cheap night tariff can then reduce the value of using solar for either the EV or the battery.

Use the [Solar Payback Calculator](/solar-payback-calculator/) for project-level PV economics, the [EV Charging Cost Calculator](/ev-charging-cost-calculator/) for vehicle charging, and this optimiser when the interaction between all three systems is the main question.

A robust result should remain sensible when you reduce solar generation, worsen battery efficiency or narrow the tariff spread. If the preferred setup only wins under one optimistic assumption, treat that as a warning that the optimisation is fragile.

## Method and limitations

The tool estimates annual solar generation, allocates energy to home use, EV use, battery and export under the entered percentages and capacity limits, and values each flow at the relevant tariff. It is not a half-hourly simulation.

### Useful sources

- [CRU — Smart meters and services](https://www.cru.ie/consumer-information/billing/smart-meters-and-services/)
- [SEAI — EV charging](https://www.seai.ie/plan-your-energy-journey/for-your-home/electric-vehicles/about-evs/ev-charging)

## Why “maximum self-consumption” is not always maximum value

Solar advice often treats self-consumption as the goal, but the financially relevant question is **what alternative each kWh replaces**.

If exported electricity earns €0.15/kWh and your EV would otherwise charge overnight at €0.10/kWh, diverting a solar kWh from export into the EV can actually reduce its immediate cash value. The opposite may be true for a daytime household load that would otherwise buy electricity at €0.35/kWh.

A battery introduces the same opportunity-cost question. Storing a surplus kWh sacrifices the export payment today in exchange for avoiding a later import, minus round-trip losses.

That is why this optimiser separates energy flows rather than simply rewarding the highest self-consumption percentage. The best configuration depends on tariff spreads and timing, not on a single headline percentage.

