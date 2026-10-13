---
title: "Installer Portal | Compound Solar"
canonical_path: /solar/installer-portal/
meta_description: "Secure Compound Solar portal for verified installation businesses to access private solar opportunities and purchased introductions."
---
<div class="sip" data-installer-portal data-supabase-url="https://guifxtijipkpvjjyhatq.supabase.co" data-supabase-publishable-key="sb_publishable_ve357dvU1yKXIkMkEz5FTA_bg1BBvjk" data-checkout-api-url="">
  <div class="sip-head">
    <div>
      <a class="sip-back" href="/solar/">← Compound Solar</a>
      <div class="sip-brand"><span class="sip-brand-mark">C<span>.</span></span><span>COMPOUND <b>SOLAR</b> <small>INSTALLER PORTAL</small></span></div>
    </div>
    <span class="sip-head-status"><i></i> Private installer access</span>
  </div>

  <section class="sip-signin" data-ip-screen="signin" aria-labelledby="sip-signin-title">
    <div class="sip-auth-copy">
      <p class="sip-eyebrow">FOR VERIFIED SOLAR INSTALLERS</p>
      <h1 id="sip-signin-title">Better projects.<br><em>Less chasing.</em></h1>
      <p>Browse homeowner-approved solar projects, review the scope before committing, and keep every purchased introduction in one place.</p>
      <div class="sip-auth-benefits">
        <div><span>01</span><strong>Qualified project briefs</strong><small>Solar requirements, roof settings and customer intent in one overview.</small></div>
        <div><span>02</span><strong>Pay per introduction</strong><small>See the price and remaining availability before you buy.</small></div>
        <div><span>03</span><strong>Private purchased leads</strong><small>Homeowner details only unlock for your business after approved payment.</small></div>
      </div>
    </div>
    <div class="sip-login-panel">
      <span class="sip-pill">VERIFIED BUSINESSES ONLY</span>
      <h2>Installer sign in</h2>
      <p>Use the email address registered to your company. We’ll email a one-time verification code — no password needed.</p>
      <div class="sip-pilot-notice" data-ip-prelaunch>This installer portal is being prepared for its pilot. Real login and purchases are not active yet.</div>
      <form data-ip-email-form novalidate>
        <label for="sip-email">Business email address</label>
        <input id="sip-email" name="email" type="email" autocomplete="email" inputmode="email" required placeholder="you@solarcompany.ie">
        <button class="sip-button sip-button-primary" data-ip-send type="submit">Email me a login code <span>→</span></button>
      </form>
      <form data-ip-code-form hidden novalidate>
        <label for="sip-code">Six-digit email code</label>
        <input id="sip-code" data-ip-code name="code" type="text" inputmode="numeric" autocomplete="one-time-code" maxlength="6" pattern="[0-9]{6}" placeholder="000000" required>
        <button class="sip-button sip-button-primary" type="submit">Enter installer dashboard <span>→</span></button>
        <button class="sip-link-button" data-ip-code-back type="button">Use a different email</button>
      </form>
      <p class="sip-message" data-ip-message role="status" aria-live="polite"></p>
      <div class="sip-login-divider"><span>NEW INSTALLER?</span></div>
      <p class="sip-apply-copy">Access is granted only after a business verification check.</p>
      <a class="sip-button sip-button-outline" href="#installer-application">Apply for installer access ↗</a>
      <p class="sip-form-foot">Sign-in does not subscribe you to marketing emails. <a href="/privacy/">Privacy policy</a>.</p>
    </div>
  </section>

  <section class="sip-application" id="installer-application" data-ip-application aria-labelledby="sip-application-title">
    <div><p class="sip-eyebrow">INSTALLER ONBOARDING</p><h2 id="sip-application-title">Apply for the pilot.</h2><p>Tell us your company, SEAI registration and service counties. We verify businesses before granting portal access.</p></div>
    <form data-ip-application-form>
      <label>Company name<input name="company" maxlength="120" autocomplete="organization" required placeholder="Your registered business"></label>
      <label>Business email<input name="email" type="email" autocomplete="email" required placeholder="office@example.ie"></label>
      <label>SEAI registration / business verification details<input name="registration" maxlength="120" required placeholder="Registration number or register listing"></label>
      <label>Counties served<input name="counties" maxlength="240" required placeholder="e.g. Meath, Dublin, Kildare"></label>
      <button class="sip-button sip-button-primary" type="submit">Prepare application email <span>↗</span></button>
      <p class="sip-form-foot">Applications currently open your email app; no application information is stored by this page. Approval and login are separate.</p>
      <p class="sip-message" data-ip-application-status role="status"></p>
    </form>
  </section>

  <section class="sip-dashboard" data-ip-screen="dashboard" aria-label="Private installer dashboard" hidden>
    <div class="sip-dashboard-head">
      <div><p class="sip-eyebrow">INSTALLER WORKSPACE</p><h1>Solar opportunities.</h1><p data-ip-company>Verified partner</p></div>
      <div class="sip-dashboard-actions"><span class="sip-pill" data-ip-mode>APPROVED ACCOUNT</span><button type="button" class="sip-signout" data-ip-signout>Sign out ↗</button></div>
    </div>
    <div class="sip-preview-warning" data-ip-demo-warning hidden><strong>Design preview only.</strong> All projects below are invented examples. There is no live lead inventory, payment or homeowner information in this preview.</div>
    <div class="sip-metrics">
      <div><span>AVAILABLE TO YOUR COMPANY</span><strong data-ip-total>0</strong><small>Verified projects in your service area</small></div>
      <div><span>YOUR PURCHASED LEADS</span><strong data-ip-purchased-total>0</strong><small>Accessible only to your business</small></div>
      <div><span>INTRODUCTION PRICE</span><strong>€65</strong><small>Pilot price per qualified introduction</small></div>
    </div>
    <nav class="sip-tabs" aria-label="Installer workspace sections">
      <button type="button" data-ip-tab="available" aria-pressed="true">Available Projects <span data-ip-tab-available>0</span></button>
      <button type="button" data-ip-tab="purchased" aria-pressed="false">Purchased Leads <span data-ip-tab-purchased>0</span></button>
      <button type="button" data-ip-tab="account" aria-pressed="false">My Account</button>
    </nav>
    <div data-ip-tab-panel="available">
      <div class="sip-section-heading"><div><h2>Available solar projects</h2><p>Anonymous project previews. Contact details are never shown before an authorised purchase.</p></div><label class="sip-select-wrap">County <select data-ip-county-filter><option value="">All service counties</option></select></label></div>
      <div class="sip-project-grid" data-ip-available-list></div>
      <div class="sip-empty" data-ip-available-empty hidden><span>◇</span><h3>No available projects</h3><p>New qualified requests in your service area will appear here once the marketplace launches.</p></div>
    </div>
    <div data-ip-tab-panel="purchased" hidden>
      <div class="sip-section-heading"><div><h2>Purchased introductions</h2><p>Only homeowner briefs purchased and authorised for your company are accessible here.</p></div></div>
      <div class="sip-project-grid" data-ip-purchased-list></div>
      <div class="sip-empty" data-ip-purchased-empty hidden><span>◇</span><h3>No purchased leads</h3><p>Your secure project briefs and contact details will be shown here after completed purchases.</p></div>
    </div>
    <div data-ip-tab-panel="account" hidden>
      <div class="sip-account-card">
        <p class="sip-eyebrow">VERIFIED INSTALLER</p><h2 data-ip-account-name>Company account</h2>
        <dl><div><dt>Business email</dt><dd data-ip-account-email>—</dd></div><div><dt>SEAI registration</dt><dd data-ip-account-registration>—</dd></div><div><dt>Service counties</dt><dd data-ip-account-counties>—</dd></div><div><dt>Verification</dt><dd data-ip-account-verification>—</dd></div></dl>
        <p>For account changes, contact <a href="mailto:david@compound.ie?subject=Compound%20Solar%20Installer%20Account">david@compound.ie</a>. Accounts are individually approved; there is no public self-registration.</p>
      </div>
    </div>
    <p class="sip-message" data-ip-dashboard-status role="status" aria-live="polite"></p>
  </section>
  <p class="sip-footer-note">Compound Solar is an introduction service, not a guarantee of an installation contract. Quotes and technical specifications require installer verification and a site assessment.</p>
</div>
