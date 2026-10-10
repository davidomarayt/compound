(function () {
  "use strict";
  // No market-data script is requested until the user scrolls near a chart.
  // The permanent TradingView link remains available if the embed is blocked.
  var panels = document.querySelectorAll("[data-compound-tradingview]");
  if (!panels.length) return;

  function loadChart(panel) {
    if (panel.dataset.tvState) return;
    var symbol = panel.getAttribute("data-tv-symbol") || "";
    var variant = panel.getAttribute("data-tv-variant");
    if (!/^[A-Z][A-Z0-9.]{0,11}$/.test(symbol) || (variant !== "compact" && variant !== "advanced")) return;
    var wrapper = panel.querySelector(".tradingview-widget-container");
    var target = panel.querySelector(".tradingview-widget-container__widget");
    if (!wrapper || !target) return;
    panel.dataset.tvState = "loading";
    var config, endpoint;
    if (variant === "advanced") {
      endpoint = "embed-widget-advanced-chart.js";
      config = {
        autosize: true, symbol: symbol, interval: "D", timezone: "Etc/UTC",
        theme: "light", style: "1", locale: "en", hide_side_toolbar: true,
        hide_top_toolbar: false, hide_legend: false, hide_volume: false,
        allow_symbol_change: false, withdateranges: true, details: false,
        calendar: false, save_image: true, backgroundColor: "#ffffff",
        gridColor: "rgba(46,46,46,0.06)"
      };
    } else {
      endpoint = "embed-widget-symbol-overview.js";
      config = {
        symbols: [[symbol, symbol + "|1D"]], autosize: true, width: "100%", height: "100%",
        locale: "en", colorTheme: "light", isTransparent: false,
        backgroundColor: "#ffffff", chartType: "area", lineWidth: 2,
        chartOnly: false, hideDateRanges: false, hideMarketStatus: false,
        hideSymbolLogo: false, showVolume: false, scalePosition: "right",
        dateRanges: ["1m|1D", "6m|1D", "12m|1D", "60m|1W", "all|1M"]
      };
    }
    target.textContent = "";
    var script = document.createElement("script");
    script.type = "text/javascript";
    script.src = "https://s3.tradingview.com/external-embedding/" + endpoint;
    script.async = true;
    script.textContent = JSON.stringify(config);
    script.onerror = function () {
      panel.dataset.tvState = "unavailable";
      target.textContent = "Interactive chart unavailable. Open the TradingView link below.";
    };
    wrapper.appendChild(script);
  }

  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          loadChart(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: "320px 0px", threshold: 0 });
    panels.forEach(function (panel) { observer.observe(panel); });
  } else {
    panels.forEach(loadChart);
  }
}());
