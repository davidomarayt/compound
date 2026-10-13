---
title: "Solar Panel Direction Calculator Ireland: 360° Compass & kWh"
canonical_path: /solar/roof-direction/
meta_description: "Turn an interactive 360-degree solar compass to estimate Irish solar panel generation by roof direction, pitch, kWp and location. Compare with south-facing output."
---
<div class="sor-shell" data-solar-orientation>
  <nav aria-label="Breadcrumb"><a class="sor-back" href="/solar/">← Solar Hub</a></nav>
  <header class="sor-intro">
    <div><p class="sor-ey">COMPOUND / FREE SOLAR DESIGN TOOL</p><h1>Which way should your solar panels <em>face?</em></h1><p class="sor-lead">Turn the roof through a full 360°. See how direction, tilt and system size change estimated solar generation in Ireland. No sign-up required.</p></div>
    <p class="sor-sidelead">A south-facing roof isn't your only option. Explore any angle, then refine your numbers using the European Commission's PVGIS model before requesting installation quotes.</p>
  </header>
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
    <p class="sor-disclosure">The instant dial uses a simplified sun-path and diffuse-light model calibrated to broad indicative Irish annual yields. It is not a site-specific forecast. Choose <strong>Open PVGIS calculator</strong> to check the estimate using the <a href="https://photovoltaic-geographic-information-system.ec.europa.eu/" rel="noopener" target="_blank">European Commission's official PVGIS website ↗</a>. PVGIS opens separately: enter your exact location, roof pitch, system size and orientation, checking its azimuth convention. Compound does not send your settings to PVGIS. The simplified model on this page does not measure trees, chimneys, roof obstructions or future weather.</p>
  </section>
  <section class="sor-next"><div><h2>Now, does it pay back?</h2><p>Take the estimated <strong>kWh per kWp</strong> into our solar payback calculator, then compare installer quotes on the same generation assumptions. Confirm final yield predictions with your installer.</p></div><div class="sor-buttons"><a href="/solar-payback-calculator/" class="sor-action">Calculate solar payback ↗</a><a href="/solar/compare-quotes/" class="sor-action sor-action-secondary">Compare solar quotes ↗</a></div></section>
  <section aria-label="How to read solar panel compass bearings"><h2>How solar panel direction works</h2><p class="sor-disclosure">The compass uses degrees clockwise from north: 0° is north, 90° east, 180° south and 270° west. PVGIS uses a different angle convention internally; Compound converts your compass bearing automatically. For two roof faces, calculate each separately with its own kWp and add the generation estimates. An east-west layout can spread electricity production across the morning and afternoon even where total annual yield is below due south. Read our <a href="/wealth/east-west-facing-solar-panels-ireland/">east-versus-west Irish solar guide</a> for a deeper explanation.</p></section>
</div>