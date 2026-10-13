---
title: "Solar Project Builder Ireland: Your Installation Quote Brief"
canonical_path: /solar/get-quotes/
meta_description: "Build a detailed solar installation quote brief in Ireland: roof orientation, pitch, shading, electricity use, battery preferences and budget. Private, free, no account."
---
<div class="sol-shell sol-subpage sol-project" data-solar-brief data-solar-project data-solar-leads-active="false" data-solar-leads-api="https://compound-solar-api.vercel.app" data-turnstile-sitekey="">
  <nav class="sol-subcrumb" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/solar/">Solar</a> / <span aria-current="page">Solar project brief</span></nav>
  <header class="sol-project-hero">
    <div><p class="sol-ey">COMPOUND SOLAR / PROJECT BUILDER</p><h1>One solar project. <em>Clearer quotes.</em></h1><p>Build a useful installation brief once, rather than starting again with every provider. Fill in what you know; choose <strong>Not sure</strong> wherever technical details need an installer to check.</p>
      <div class="sol-project-status"><span><strong>Free</strong> homeowner tool</span><span><strong>No account</strong> required</span><span><strong>Private</strong> until you choose to share</span></div>
    </div>
    <aside class="sol-project-progress" aria-live="polite"><span class="sol-ey">PROJECT READINESS</span><div class="sol-project-progress-score" data-sp-progress>0%</div><div class="sol-project-track"><span data-sp-progress-bar></span></div><p data-sp-progress-note>Fill in key details to make your project easier to quote.</p><small>Readiness measures completeness, not roof suitability or whether a quotation is guaranteed.</small></aside>
  </header>
  <section class="sol-project-disclosure" aria-label="How this tool handles your information">
    <strong><span aria-hidden="true">ⓘ</span> This is a private quote-brief builder, not a live lead marketplace.</strong>
    <p>The information stays in this browser tab. Compound does not receive, save, sell or send your form answers to installers. Copy the brief only when you choose to share it yourself. Secure accounts and homeowner-approved installer introductions are planned but not available yet.</p>
  </section>
  <div class="sol-project-navigation" aria-label="Project sections">
    <a href="#sol-project-home">01 Property</a><a href="#sol-project-roof">02 Roof</a><a href="#sol-project-energy">03 Electricity</a><a href="#sol-project-preferences">04 System</a><a href="#sol-project-contact">05 Sharing</a>
  </div>
  <section class="sol-project-body">
    <div class="sol-project-sections">
      <section class="sol-project-step" id="sol-project-home" aria-labelledby="sol-project-home-heading">
        <div class="sol-project-step-head"><span>01 / PROPERTY AND TIMING</span><h2 id="sol-project-home-heading">Tell us about the property.</h2><p>These details help an installer establish whether the job fits their service area and availability.</p></div>
        <div class="sol-fields">
          <label>County <small>Essential for matching providers</small><select data-sb="county" data-sp="county"><option value="">Select county</option><option>Carlow</option><option>Cavan</option><option>Clare</option><option>Cork</option><option>Donegal</option><option>Dublin</option><option>Galway</option><option>Kerry</option><option>Kildare</option><option>Kilkenny</option><option>Laois</option><option>Leitrim</option><option>Limerick</option><option>Longford</option><option>Louth</option><option>Mayo</option><option>Meath</option><option>Monaghan</option><option>Offaly</option><option>Roscommon</option><option>Sligo</option><option>Tipperary</option><option>Waterford</option><option>Westmeath</option><option>Wexford</option><option>Wicklow</option></select></label>
          <label>Nearest town / general area <small>Do not enter your street address</small><input data-sp="area" type="text" maxlength="70" placeholder="e.g. Kells"></label>
          <label>Do you own or make decisions for this property? <select data-sp="role"><option value="">Choose an answer</option><option>Owner</option><option>Joint owner</option><option>Authorised decision-maker</option><option>Not yet the decision-maker</option></select></label>
          <label>Building type <select data-sp="building"><option value="">Choose an answer</option><option>Detached house</option><option>Semi-detached house</option><option>Terraced house</option><option>Bungalow</option><option>Apartment or managed building</option><option>Commercial / farm building</option><option>Other / not sure</option></select></label>
          <label>Solar project <select data-sp="project"><option>New rooftop solar PV</option><option>Ground-mounted solar PV</option><option>Expand an existing system</option><option>Battery retrofit only</option><option>Not sure</option></select></label>
          <label>When would you like installation? <select data-sp="timing"><option value="">Choose a timeframe</option><option>As soon as practical</option><option>Within 3 months</option><option>3–6 months</option><option>6–12 months</option><option>Researching options</option></select></label>
          <label>Rough installation budget <select data-sp="budget"><option value="">Prefer not to say / unsure</option><option>Under €5,000</option><option>€5,000–€8,000</option><option>€8,000–€12,000</option><option>€12,000–€16,000</option><option>€16,000+</option></select></label>
          <label>Protected building or conservation area? <select data-sp="protected"><option>Not sure</option><option>No known restrictions</option><option>Protected structure</option><option>Architectural conservation area</option><option>Other possible planning issue</option></select></label>
        </div>
      </section>
      <section class="sol-project-step" id="sol-project-roof" aria-labelledby="sol-project-roof-heading">
        <div class="sol-project-step-head"><span>02 / ROOF AND SITE</span><h2 id="sol-project-roof-heading">Describe where panels might go.</h2><p>Turn the 360° compass below to set the actual direction and pitch for each roof face. A roof survey must still verify the final panel layout and structural suitability.</p></div>
        <div class="sol-fields">
          <label>Mounting location <select data-sb="roof" data-sp="roof"><option>Pitched roof</option><option>Flat roof</option><option>Ground mount</option><option>Unsure</option></select></label>
          <label>Roof sections you want to use <select data-sp="faces"><option value="1">One roof face</option><option value="2">Two roof faces</option><option value="unknown">Not sure</option></select></label>
          <input data-sp="azimuth" type="hidden" value="">
          <input data-sp="pitch" type="hidden" value="">
          <p class="sol-project-roof-readout">Primary roof face: <strong data-sp-primary-output>Not yet selected</strong></p>
          <label>Approximate usable roof area (m²) <input data-sp="areaM2" type="number" min="0" max="1000" step="1" placeholder="Optional, if measured"></label>
          <label>Roof covering <select data-sp="material"><option>Not sure</option><option>Concrete tile</option><option>Clay tile</option><option>Slate / natural slate</option><option>Metal sheet</option><option>Flat membrane / felt</option><option>Other</option></select></label>
        </div>
        <div class="sor-shell sor-embedded" data-solar-orientation data-orientation-embedded>
    <div class="sol-project-compass-top">
      <p class="sol-ey">INTERACTIVE ROOF COMPASS</p>
      <h3>Point your panels. See the output.</h3>
      <p>Tap or drag the dial, adjust the roof pitch and see generation change instantly. Your chosen direction, pitch and proposed array size update your installer brief automatically.</p>
      <div class="sol-project-face-tabs" data-sp-face-switch hidden role="group" aria-label="Choose roof face to configure">
        <button type="button" data-sp-face-button="1" aria-pressed="true">Roof face 1</button>
        <button type="button" data-sp-face-button="2" aria-pressed="false">Roof face 2</button>
      </div>
      <p class="sol-project-face-status" data-sp-face-status role="status">The compass starts with an example south-facing roof. Select a bearing to confirm your own roof.</p>
    </div>
    <section class="sor-board" aria-label="Interactive solar roof direction calculator">
    <div class="sor-left">
      <div class="sor-panel-heading">ROOF COMPASS <span>0° NORTH · 90° EAST · 180° SOUTH · 270° WEST</span></div>
      <button class="sor-dial" type="button" data-or="dial" aria-label="Roof direction compass. Tap or drag to set angle; arrow keys adjust by one degree." aria-describedby="sor-cue">
        <span class="sor-ring" aria-hidden="true"></span><span class="sor-disc" aria-hidden="true"></span>
        <span class="sor-cardinal sor-n" aria-hidden="true">N</span><span class="sor-cardinal sor-e" aria-hidden="true">E</span><span class="sor-cardinal sor-s" aria-hidden="true">S</span><span class="sor-cardinal sor-w" aria-hidden="true">W</span>
        <span class="sor-pointer" data-or="needle" style="transform:rotate(180deg)" aria-hidden="true"><span class="sor-roof"><i></i><i></i><i></i><i></i><i></i><i></i></span></span>
        <span class="sor-dial-center"><strong data-or="angle">180°</strong><span data-or="heading">South</span></span>
      </button>
      <p class="sor-cue" id="sor-cue">Tap, drag or use the slider to turn your panels.</p>
      <div class="sor-presets" role="group" aria-label="Quick roof directions">
        <button type="button" data-or-preset="0" aria-pressed="false">N</button>
        <button type="button" data-or-preset="45" aria-pressed="false">NE</button>
        <button type="button" data-or-preset="90" aria-pressed="false">E</button>
        <button type="button" data-or-preset="135" aria-pressed="false">SE</button>
        <button type="button" data-or-preset="180" aria-pressed="true">S</button>
        <button type="button" data-or-preset="225" aria-pressed="false">SW</button>
        <button type="button" data-or-preset="270" aria-pressed="false">W</button>
        <button type="button" data-or-preset="315" aria-pressed="false">NW</button>
      </div>
      <label class="sor-slider-line" for="sor-degree">Exact degree <input id="sor-degree" type="range" min="0" max="359" step="1" value="180" data-or="slider" aria-label="Solar panel compass azimuth angle, zero north clockwise"><output for="sor-degree" data-or="slider-value">180°</output></label>
    </div>
    <div class="sor-right">
      <span class="sor-status-chip" data-or="accuracy">Indicative estimate</span>
      <div data-or="results">
        <p class="sor-result-label">ESTIMATED ANNUAL ELECTRICITY GENERATION</p>
        <div class="sor-kwh"><strong data-or="total" aria-live="off">—</strong><span>kWh / year</span></div>
        <p class="sor-kwh-sub" data-or="source">Based on the settings and orientation shown.</p>
        <div class="sor-kpis">
          <div class="sor-kpi"><small>Vs due south, same pitch</small><strong data-or="percent">—</strong><em>100% = south-facing estimate</em></div>
          <div class="sor-kpi"><small>Annual yield per kWp</small><strong data-or="unit">—</strong><em>kWh per installed kWp</em></div>
        </div>
        <div class="sor-meter" aria-hidden="true"><span data-or="grade"></span></div><p class="sor-relative" data-or="relative"></p>
      </div>
      <p class="sor-error" data-or="error" hidden>Enter a system size above 0 and no more than 30 kWp, a roof pitch from 0° to 90°, and shading of 0–50%.</p>
      <div class="sor-settings" role="group" aria-label="Solar system assumptions">
        <label><span>Nearby Irish town</span><select data-or="place">
          <option value="dublin">Dublin</option><option value="navan" selected>Navan / Meath</option>
          <option value="wexford">Wexford</option><option value="cork">Cork</option>
          <option value="kilkenny">Kilkenny</option><option value="limerick">Limerick</option>
          <option value="galway">Galway</option><option value="sligo">Sligo</option>
          <option value="donegal">Letterkenny / Donegal</option>
        </select></label>
        <label><span>Panel array size (kWp)</span><input data-or="size" type="number" min="0.1" max="30" step="0.5" value="6" inputmode="decimal"></label>
        <label><span>Panel tilt / pitch (degrees)</span><input data-or="pitch" type="number" min="0" max="90" step="1" value="35" inputmode="numeric"></label>
        <label><span>Estimated shading loss (%)</span><input data-or="shade" type="number" min="0" max="50" step="1" value="0" inputmode="numeric"></label>
      </div>
      <p class="sor-field-note">Choose the nearest representative town, not your exact roof. The shading field is a simple illustrative annual deduction, not a shade survey.</p>
      <div class="sor-buttons">
        <button type="button" class="sor-action" data-or="request">Open PVGIS calculator ↗</button>
        <button type="button" class="sor-action sor-action-secondary" data-or="copy">Copy yield per kWp</button>
        
      </div>
      <p role="status" aria-live="polite" class="sor-message" data-or="status"></p>
    </div>
  </section>
    <section class="sor-chart-section" aria-label="Monthly solar generation estimate">
    <div class="sor-chart-header"><div><p class="sor-ey">THE SEASONS MATTER</p><h2>Generation across the year.</h2></div><p>Monthly output changes with daylight, seasonal sun angle, panel direction and your selected roof pitch.</p></div>
    <div class="sor-chart-visual">
      <canvas data-or="chart" class="sor-canvas" role="button" tabindex="0" aria-label="Monthly solar generation chart. Tap or use left and right arrow keys to select a month." width="800" height="258">Monthly solar generation by month, January to December.</canvas>
      <div class="sor-chart-readout"><strong data-or="chart-amount" role="status" aria-live="polite">Select a month</strong><span data-or="chart-peak">Peak production updates with the compass</span></div>
      <p class="sor-chart-hint">Tap a bar, or use the chart’s left and right arrow keys, to see the exact monthly kWh. Turn the compass above to compare roof directions.</p>
    </div>
    <p class="sor-disclosure">These instant estimates are illustrative, not a roof or electrical survey. Confirm usable area, shade and expected yield with your installer. <a href="/solar/roof-direction/">Learn how the estimate works ↗</a></p>
  </section>
  </div>
                <div class="sol-project-secondary-face" data-sp-second hidden aria-label="Secondary roof face">
          <h3>Second roof face</h3><div class="sol-fields">
            <input type="hidden" data-sp="azimuth2" value="">
            <input type="hidden" data-sp="pitch2" value="">
            <p class="sol-project-roof-readout">Second roof face: <strong data-sp-secondary-output>Not yet selected</strong></p>
            <label>Second face usable area (m²) <input data-sp="areaM22" type="number" min="0" max="1000" placeholder="Optional"></label>
          </div>
        </div>
        <div class="sol-fields">
          <label>Visible shading <select data-sp="shade"><option>Not sure</option><option>None / minimal</option><option>Some shade</option><option>Significant shade</option></select></label>
          <label>Possible obstructions <select data-sp="obstacles"><option>Not sure</option><option>No major obstructions</option><option>Chimney / vents</option><option>Dormer / skylights</option><option>Mixed obstructions</option></select></label>
          <label>Roof condition <select data-sp="roofCondition"><option>Not sure</option><option>Recently replaced / good</option><option>Appears sound</option><option>Repair / replacement planned</option></select></label>
          <label>Building height <select data-sp="storeys"><option>Not sure</option><option>One storey</option><option>Two storeys</option><option>Three or more</option></select></label>
          <label>Site access <select data-sp="access"><option>Not sure</option><option>Normal driveway / scaffold access</option><option>Restricted access</option><option>Long cable run / outbuilding</option></select></label>
        </div>
        <p class="sol-project-help" data-sp-compass>Your confirmed compass settings appear automatically in the installer brief below. Figures are indicative and should be verified by the installer.</p>
      </section>
      <section class="sol-project-step" id="sol-project-energy" aria-labelledby="sol-project-energy-heading">
        <div class="sol-project-step-head"><span>03 / ENERGY DEMAND AND ELECTRICAL</span><h2 id="sol-project-energy-heading">How does your home use electricity?</h2><p>Use a recent bill for annual kWh if available. The installer will confirm any electrical details you are unsure about.</p></div>
        <div class="sol-fields">
          <label>Annual home electricity use (kWh) <input data-sb="demand" data-sp="demand" type="number" min="0" max="100000" step="100" inputmode="numeric" placeholder="e.g. 5,000"></label>
          <label>Average electricity bill (€ per month) <input data-sp="bill" type="number" min="0" max="5000" step="5" placeholder="If annual kWh is unknown"></label>
          <label>Day/night usage pattern <select data-sp="daytime"><option>Not sure</option><option>Someone home most days</option><option>Mainly evenings</option><option>Shift work / variable schedule</option><option>High daytime business use</option></select></label>
          <label>Electricity meter <select data-sp="smartMeter"><option>Not sure</option><option>Smart meter installed</option><option>Standard meter</option></select></label>
          <label>Electricity supply <select data-sp="phase"><option>Not sure</option><option>Single-phase</option><option>Three-phase</option></select></label>
          <label>Electrical distribution board <select data-sp="board"><option>Not sure</option><option>Recently updated</option><option>Older unit / may need inspection</option><option>Space constraints</option></select></label>
          <label>EV charging <select data-sp="ev"><option>No EV planned</option><option>Already own an EV</option><option>Planning an EV</option><option>Multiple EVs</option></select></label>
          <label>Heat pump <select data-sp="heatPump"><option>No heat pump planned</option><option>Already installed</option><option>Planning a heat pump</option></select></label>
          <label>Hot-water immersion <select data-sp="immersion"><option>Not sure</option><option>Electric immersion present</option><option>No electric immersion</option></select></label>
          <label>Existing solar PV <select data-sp="existingPV"><option>No</option><option>Yes, extend existing system</option><option>Yes, battery-only upgrade</option><option>Not sure</option></select></label>
        </div>
        <p class="sol-project-help">Do not open electrical covers or climb onto the roof. Do not share meter serial numbers or MPRNs. The installer checks these safely during a survey.</p>
      </section>
      <section class="sol-project-step" id="sol-project-preferences" aria-labelledby="sol-project-preferences-heading">
        <div class="sol-project-step-head"><span>04 / WHAT YOU WANT QUOTED</span><h2 id="sol-project-preferences-heading">Tell installers how to price it.</h2><p>These preferences help them send comparable proposals, not just a headline installation price.</p></div>
        <div class="sol-fields">
          <label>Preferred array size (kWp) <input data-sp="kwp" type="number" min="0" max="100" step="0.5" placeholder="If known; installer to recommend"></label>
          <label>Battery preference <select data-sb="battery" data-sp="battery"><option value="quote-both">Quote both with and without battery</option><option value="solar-only">Solar PV only</option><option value="with-battery">Solar PV plus battery</option><option value="unsure">Not sure</option></select></label>
          <label>Battery size (kWh) <input data-sp="batteryKwh" type="number" min="0" max="200" step="0.5" placeholder="Leave blank to let installer advise"></label>
          <label>EV charger included? <select data-sp="evCharger"><option>Quote separately</option><option>Yes</option><option>No</option></select></label>
          <label>Hot water diverter? <select data-sp="diverter"><option>Quote separately</option><option>Yes</option><option>No</option></select></label>
          <label>Backup power during outages? <select data-sp="backup"><option>Not essential / unsure</option><option>Yes, explore backup</option><option>No</option></select></label>
          <label>Solar grant status <select data-sp="grant"><option>Not sure</option><option>Likely eligible but not applied</option><option>Application underway</option><option>Already approved</option><option>Previously received solar grant</option></select></label>
          <label>Funding <select data-sp="finance"><option>Not sure</option><option>Pay outright</option><option>Interested in finance</option></select></label>
          <label>Existing solar quotes? <select data-sp="quotes"><option>No</option><option>Yes, one</option><option>Yes, two or more</option></select></label>
          <label>Install/inverter cable route <select data-sp="cable"><option>Not sure</option><option>Near consumer unit / meter</option><option>Attic / garage / utility space</option><option>Outbuilding / long distance</option></select></label>
        </div>
        <label class="sol-project-wide-label">Anything else the installer should know? <textarea data-sp="notes" rows="3" maxlength="900" placeholder="Roof access, high electricity bills, upcoming renovation, specific equipment or accessibility needs…"></textarea></label>

      </section>
      <section class="sol-project-step" id="sol-project-contact" aria-labelledby="sol-project-contact-heading">
        <div class="sol-project-step-head"><span>05 / HOMEOWNER CONTACT PREFERENCES</span><h2 id="sol-project-contact-heading">Decide how you'd like quotations.</h2><p>These fields are for your own copy-ready message. Nothing is submitted to Compound and no company is automatically contacted.</p></div>
        <div class="sol-fields">
          <label>Preferred number of installers <select data-sp="installerCount"><option value="" selected>Select the number of quotes</option><option value="1">One installer only</option><option value="2">Up to 2 separate installers</option><option value="3">Up to 3 separate installers</option></select></label>
          <label>Preferred contact method <select data-sp="contactMethod"><option>Email</option><option>Phone</option><option>Either</option></select></label>
          <label>Your name (optional; stays in this browser tab) <input data-sp="name" type="text" maxlength="100" autocomplete="name" placeholder="Included only if you copy the brief"></label>
          <label>Your email (optional) <input data-sp="email" type="email" maxlength="180" autocomplete="email" placeholder="you@example.ie"></label>
          <label>Your phone (optional) <input data-sp="phone" type="tel" maxlength="35" autocomplete="tel" placeholder="+353…"></label>
          <label>Full Eircode (optional, private) <input data-sp="eircode" type="text" maxlength="12" autocomplete="postal-code" placeholder="Only disclose directly to your chosen installer"></label>
        </div>
        <section data-sp-live-request hidden class="sol-project-disclosure" aria-labelledby="solar-quote-request-heading">
          <h3 id="solar-quote-request-heading">Request your solar installation quotes</h3>
          <p>Your name and private project details will only be made available to up to the number of installers you select. Approved installers first see a limited, non-identifying county-level project preview.</p>
          <form data-sp-quote-form>
            <label class="sol-project-wide-label"><input type="checkbox" data-sp-quote-consent required> I request up to <strong data-sp-sharing-count>the number you choose</strong> solar installation quotations. I understand that a limited project preview may be shown to approved installers, and that my name, contact details and completed project brief may be shared with up to that number of approved installers so they can contact me about my quotes. Installers may pay Compound.ie for an introduction. I can stop future introductions by emailing david@compound.ie. I have read the <a href="/privacy/">privacy notice</a>.</label>
            <div data-sp-turnstile aria-label="Spam verification"></div>
            <button class="sol-btn" data-sp-quote-submit type="submit" disabled>Submit secure quote request</button>
            <p data-sp-quote-status role="status" aria-live="polite"></p>
          </form>
          <p>Contact details are never shown in the anonymous listing. This is only for the requested quotes, not newsletter subscriptions or unrelated marketing.</p>
        </section>
        <p class="sol-project-help"><strong>How future quote requests will work:</strong> You will actively choose 1, 2 or 3 quotes and agree to a clear sharing notice before submitting. A limited preview (such as county, rough area and broad solar requirements) may then be visible to approved installers. Your name and contact details will only be shared with up to your chosen number of participating installers for the quotes you request. We will tell you which companies receive your details, and you can stop further sharing. <strong>This tool does not currently submit or share your details.</strong></p>
      </section>
    </div>
    <aside class="sol-project-side" aria-label="Your project summary">
      <div class="sol-project-summary"><p class="sol-ey">YOUR SOLAR PLAN</p><h2>From research to a quote.</h2><div data-sp-tags class="sol-project-tags"><span>Start with your property</span></div>
      <p>This summary will update as you fill out the form. The resulting message will clearly separate known facts, estimates and questions for the installer.</p>
      <div class="sol-project-side-links"><a href="#sol-project-roof">360° roof compass ↑</a><a href="/solar-payback-calculator/">Solar payback calculator ↗</a><a href="/solar/compare-quotes/">Compare actual quotes ↗</a></div></div>
    </aside>
  </section>
  <section class="sol-project-output" aria-labelledby="sol-project-output-heading">
    <div class="sol-project-step-head"><span>YOUR REUSABLE QUOTE BRIEF</span><h2 id="sol-project-output-heading">Send the same project to every installer.</h2><p>Review the draft below, copy it and send it yourself to SEAI-registered companies. No form submission or automatic lead sharing takes place. This page does not load third-party advertising.</p></div>
    <textarea data-sb-output readonly rows="26" aria-label="Copy-ready solar installation project summary"></textarea>
    <div class="sol-project-output-actions"><button type="button" class="sol-btn" data-sb-copy>Copy my project brief</button><span role="status" aria-live="polite" data-sb-copy-status></span></div>
    <p class="sol-method">Some information might require a site survey or an electrician. Ask for itemised installed prices, panel and inverter models, realistic yield assumptions, battery capacity, scaffolding, grant handling, warranties, payment terms, exclusions and post-installation certification.</p>
  </section>
  <section class="sol-article-grid"><article><h2>What the installer still needs to confirm</h2><p>Usable roof dimensions and structure, fixings, access/scaffolding, shading, wiring distance, grid connection conditions and final system design cannot reliably be guaranteed from a homeowner's form. A quote based only on photos or your estimate should be clearly identified as provisional.</p></article><article><h2>Compare before accepting</h2><p>Ask for comparable written proposals, check the provider on <a href="/solar/installers/">SEAI's current installer register</a>, and use the <a href="/solar/compare-quotes/">solar quote comparator</a> to compare scope and total cost.</p></article></section>
  <nav class="sol-return"><a href="/solar/">← Solar hub</a><a href="/solar/compare-quotes/">Compare installer quotations ↗</a></nav>
</div>