/* Compound Solar sponsor interest form. Email-client workflow only; no personal data posted to a server. */
(function(){
  "use strict";
  var form=document.querySelector("[data-solar-sponsor-form]");
  if(!form)return;
  var boxes=Array.prototype.slice.call(form.querySelectorAll("[data-county]"));
  var countEl=form.querySelector("[data-sponsor-count]");
  var monthlyEl=form.querySelector("[data-sponsor-monthly]");
  var annualEl=form.querySelector("[data-sponsor-annual]");
  var statusEl=form.querySelector("[data-sponsor-status]");
  var euro=new Intl.NumberFormat("en-IE",{style:"currency",currency:"EUR",maximumFractionDigits:0});
  function selected(){return boxes.filter(function(box){return box.checked;}).map(function(box){return box.value;});}
  function update(){
    var qty=selected().length;
    countEl.textContent=qty+" of 32";
    monthlyEl.textContent=euro.format(qty*250);
    annualEl.textContent=euro.format(qty*3000);
  }
  function field(name){return (form.elements.namedItem(name)?.value||"").trim().replace(/[\r\n]+/g," ");}
  function draft(){
    var counties=selected();
    if(!counties.length){statusEl.textContent="Please select at least one county.";boxes[0].focus();return null;}
    if(!form.reportValidity()){statusEl.textContent="Please complete the required company fields and acknowledgement.";return null;}
    var lines=[
      "Compound Solar — county sponsorship expression of interest","",
      "Company: "+field("company"),
      "Contact: "+field("contact"),
      "Email: "+field("email"),
      "Phone: "+(field("phone")||"Not supplied"),
      "Website: "+(field("website")||"Not supplied"),
      "SEAI / UK registration: "+(field("accreditation")||"To confirm"),
      "Requested counties ("+counties.length+"): "+counties.join(", "),
      "Indicative monthly total: "+euro.format(counties.length*250)+" before applicable VAT",
      "Additional notes: "+(field("notes")||"None"),"",
      "I understand this application is non-binding and does not reserve counties or begin billing."
    ];
    return lines.join("\n");
  }
  boxes.forEach(function(box){box.addEventListener("change",function(){update();statusEl.textContent="Your county selection is ready. Complete your company details below.";});});
  form.addEventListener("submit",function(event){
    event.preventDefault();
    var body=draft();if(!body)return;
    var company=field("company").slice(0,75);
    var url="mailto:david@compound.ie?subject="+encodeURIComponent("Solar sponsor enquiry — "+company)+"&body="+encodeURIComponent(body);
    statusEl.textContent="An email draft has been prepared. Please send it from your email app to complete your application. If your email app does not open, use ‘Copy application instead’.";
    window.location.href=url;
  });
  var copy=form.querySelector("[data-sponsor-copy]");
  copy.addEventListener("click",function(){
    var body=draft();if(!body)return;
    var message="Copy this application and email it to david@compound.ie. Your application is not submitted until you send that email.";
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText("To: david@compound.ie\nSubject: Solar sponsor enquiry\n\n"+body).then(function(){statusEl.textContent="Application copied. "+message;},function(){statusEl.textContent="Copy failed. Please use the Prepare Email button or email david@compound.ie directly.";});
    }else{
      var area=document.createElement("textarea");area.value="To: david@compound.ie\n\n"+body;area.setAttribute("readonly","");area.style.position="fixed";area.style.left="-9999px";document.body.appendChild(area);area.select();
      var ok=false;try{ok=document.execCommand("copy");}catch(_){}
      area.remove();statusEl.textContent=ok?"Application copied. "+message:"Copy unavailable. Please use the Prepare Email button or email david@compound.ie directly.";
    }
  });
  update();
})();