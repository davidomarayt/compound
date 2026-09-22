## What this calculator is for

This tool compares how solar generation can interact with household demand, EV charging and a battery. Its purpose is not to find a universally 'optimal' system, but to reveal where each generated kWh goes and what value it creates under your tariff assumptions.

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

