/* Compound Solar sponsorship enquiries — posts directly to FormSubmit, without an email application. */
(function(){
  "use strict";
  var form=document.querySelector("[data-solar-sponsor-form]");
  if(!form)return;
  var boxes=Array.prototype.slice.call(form.querySelectorAll("[data-county]"));
  var countEl=form.querySelector("[data-sponsor-count]");
  var monthlyEl=form.querySelector("[data-sponsor-monthly]");
  var annualEl=form.querySelector("[data-sponsor-annual]");
  var statusEl=form.querySelector("[data-sponsor-status]");
  var countyField=form.querySelector("[data-sponsor-counties]");
  var totalField=form.querySelector("[data-sponsor-total]");
  var feeField=form.querySelector("[data-sponsor-fee]");
  var submitButton=form.querySelector("[data-sponsor-submit]");
  var euro=new Intl.NumberFormat("en-IE",{style:"currency",currency:"EUR",maximumFractionDigits:0});
  function selected(){return boxes.filter(function(box){return box.checked;}).map(function(box){return box.value;});}
  function update(){
    var counties=selected(),qty=counties.length;
    countEl.textContent=qty+" of 32";
    monthlyEl.textContent=euro.format(qty*750);
    annualEl.textContent=euro.format(qty*3000);
    countyField.value=counties.join(", ");
    totalField.value=String(qty);
    feeField.value=String(qty*750);
  }
  boxes.forEach(function(box){
    box.addEventListener("change",function(){
      update();statusEl.textContent="Selected counties are included automatically when you submit the form.";
    });
  });
  form.addEventListener("submit",function(event){
    update();
    if(!selected().length){
      event.preventDefault();
      statusEl.textContent="Please choose at least one county before submitting.";
      boxes[0].focus();
      return;
    }
    if(!form.reportValidity()){
      event.preventDefault();
      statusEl.textContent="Please fill in your company details and accept the acknowledgement.";
      return;
    }
    if(submitButton){
      submitButton.disabled=true;
      submitButton.textContent="Sending application…";
    }
    // Native HTTPS POST to FormSubmit. The provider may display its anti-spam challenge.
    // It redirects to this same page only after a successful submission.
  });
  update();
  var params=new URLSearchParams(window.location.search);
  if(params.get("submitted")==="1"){
    // A completed FormSubmit redirect indicates an installer enquiry, not a
    // homeowner lead, subscription payment, or qualified converted customer.
    // Consent-gated and deliberately excludes county, email and form fields.
    try {
      if(localStorage.getItem("compound_analytics_consent")==="granted" && typeof window.gtag==="function") {
        window.gtag("event","solar_installer_enquiry_submitted",{
          audience:"installer_business",source_path:"/solar/for-installers/"
        });
      }
    } catch (_) {}
    var banner=document.querySelector("[data-sponsor-confirmation-banner]");
    if(banner){
      banner.hidden=false;
      banner.scrollIntoView({block:"start"});
    }
    // Avoid redisplaying submitted state after ordinary refreshes/bookmarks.
    if(window.history&&window.history.replaceState){
      window.history.replaceState(null,"",window.location.pathname+window.location.hash);
    }
  }
})();