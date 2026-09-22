## What this calculator is for

This calculator estimates the electricity needed to drive an EV and the cost of charging it. It accounts for vehicle efficiency, distance and charging losses so the grid energy purchased can be higher than the energy reaching the battery.

## How to read the result

The important inputs are **kWh/100 km**, annual distance, charging efficiency and electricity rate. Home charging and public fast charging can have very different prices.

## Worked example

An EV using 18 kWh/100 km over 15,000 km needs 2,700 kWh at the battery. At 90% charging efficiency, the grid must supply about 3,000 kWh. At €0.20/kWh, that is about €600 a year.

## Irish context

SEAI says home charging is generally the cheapest option and notes that a domestic charger can deliver up to around 7.4 kW AC. SEAI also highlights time-of-use tariffs and the €300 home-charger grant subject to eligibility.

## What can change the answer

Weather, motorway speed, cabin heating, charging losses, tyre choice and battery temperature all affect consumption. Public charging can be materially more expensive than home night-rate charging.

## Common mistakes to avoid

Do not multiply battery capacity by the number of charges per year unless you actually discharge the full battery each time. Base cost on distance and efficiency. Also avoid comparing a cheap night rate with petrol cost while assuming all charging will happen at home if you regularly use public rapid chargers.

## Related Compound tools

Use the [Electricity Cost Calculator](/electricity-cost-calculator/) for the home tariff, [Fuel Cost Calculator](/fuel-cost-calculator/) for petrol/diesel comparison and [Solar + EV + Battery Optimiser](/solar-ev-battery-optimiser/) for solar charging.

## Frequently asked questions

### Is charging loss real?
Yes. More electricity is drawn from the grid than reaches the battery.

### Is home charging always cheapest?
Usually cheaper than high-speed public charging, but tariffs differ.

### Does charger power change energy cost?
It changes speed; cost depends mainly on kWh price and losses.

### Can solar make charging free?
Solar has an opportunity value and system cost, so 'free' is an oversimplification.

## Home charging, public charging and time of use

The same EV can have very different running costs depending on **where and when** it is charged. Home charging on a low night or smart-tariff rate can be substantially cheaper than repeated use of high-speed public DC chargers.

SEAI notes that home charging is generally the cheapest option and that public high-speed charging is usually more expensive. That means a realistic annual model should reflect your actual charging mix rather than assuming every kWh comes from the cheapest home rate.

Smart tariffs add another layer. If the car is parked overnight, scheduled charging can shift a large flexible load into cheaper periods. From June 2026, dynamic tariffs can also vary every half-hour, so the cheapest time may change day by day.

For a fair petrol-versus-EV comparison, include charging losses and use a blended electricity price if some charging happens away from home. The headline battery efficiency number alone is not enough.

## Advanced mode: model where you actually charge

The cheapest home tariff is not a realistic annual charging price if a meaningful share of your energy comes from public chargers. Advanced mode therefore lets you enter the share charged at home and a separate average public-charging price.

Compound creates a weighted charging price from those two inputs and applies it to the grid energy required after charging losses. The annual-distance input then converts the result into yearly grid kWh and euro cost.

Advanced mode also includes a petrol/diesel comparison using the L/100 km and fuel price you enter. This is an **energy-cost comparison only**. It does not claim an EV is cheaper overall, because purchase price, depreciation, finance, insurance, tax, tyres, servicing and charging-hardware costs are outside that number.

The home/public split can matter as much as vehicle efficiency. An EV charged almost entirely overnight at home can have very different energy economics from the same EV relying heavily on rapid public charging.

## Think in kilometres first, tariffs second

The cleanest way to understand EV charging cost is to separate vehicle efficiency from electricity price.

Start with the car's energy use in kWh per 100 km. Then estimate how many kilometres you actually drive. That gives the energy the vehicle needs before charging losses are added. Only after that should you apply the mix of home, night-rate and public-charging prices.

This avoids a common mistake: comparing one EV quoted at a cheap home tariff with another example that assumes expensive rapid charging. The vehicle can be identical while the charging pattern changes the result materially.

### Charging losses belong in the model

Energy drawn from the wall is usually higher than energy stored in the battery because charging is not perfectly efficient. The calculator therefore separates road energy demand from electricity purchased.

If a car needs 18 kWh/100 km at the battery, the household may need to buy more than 18 kWh from the meter to deliver that energy. Charging temperature, equipment and power level can affect the exact loss, so the efficiency input should be treated as an estimate rather than a universal constant.

### Home versus public charging can dominate the economics

For many Irish drivers, the most important EV-cost variable is not the battery size but the share of charging completed at home.

A driver doing most charging on a competitive overnight tariff can have a very different annual energy bill from someone using rapid public charging frequently. Advanced mode lets you enter that split directly.

Run at least three scenarios:

- mostly home charging,
- a realistic mixed pattern,
- and a high-public-charging case.

The spread between them is a useful measure of how dependent the savings are on access to home charging.

### Compare with an ICE car carefully

The **annual saving versus ICE** result is an energy-cost comparison only. It does not claim the EV is cheaper to own overall.

For a full ownership decision you still need purchase price, finance, depreciation, motor tax, insurance, tyres, servicing and any charger-installation cost. Use the [Fuel Cost Calculator](/fuel-cost-calculator/) for the petrol/diesel side and the [Lifetime Cost Calculator](/lifetime-cost-calculator/) for the whole-vehicle comparison.

### Solar and smart charging

Solar can reduce imported electricity, but a solar kWh used by the car also gives up whatever export value that kWh would otherwise have earned. Similarly, charging overnight at a very low smart-tariff rate can sometimes be financially preferable to diverting solar from a higher-value export.

That is why the [Solar + EV + Battery Optimiser](/solar-ev-battery-optimiser/) is better for households trying to coordinate tariffs, solar and storage rather than merely estimate annual EV charging cost.

SEAI's current EV guidance explains home charging and charging options; CRU guidance is the better reference for smart-meter and tariff structures.

## Method and limitations

The calculator estimates vehicle energy from distance × kWh/100 km, adjusts for charging efficiency and multiplies by the electricity price entered.

### Useful sources

- [SEAI — Charging an electric vehicle](https://www.seai.ie/plan-your-energy-journey/for-your-home/electric-vehicles/about-evs/ev-charging)
- [CRU — Smart meters and tariffs](https://www.cru.ie/consumer-information/billing/smart-meters-and-services/)
