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

  function refreshChartSize() {
    // TradingView uses an autosized iframe; give it the new viewport dimensions.
    window.requestAnimationFrame(function () {
      window.dispatchEvent(new Event("resize"));
    });
  }

  function closeExpanded() {
    var expanded = document.querySelector(".compound-tv-panel.tv-expanded");
    if (!expanded) return;
    expanded.classList.remove("tv-expanded");
    document.body.classList.remove("compound-tv-scroll-lock");
    var toggle = expanded.querySelector("[data-tv-expand]");
    if (toggle) {
      toggle.textContent = "Expand chart";
      toggle.setAttribute("aria-pressed", "false");
      toggle.setAttribute("aria-label", "Expand interactive stock chart");
      toggle.focus();
    }
    refreshChartSize();
  }

  panels.forEach(function (panel) {
    var toggle = panel.querySelector("[data-tv-expand]");
    if (!toggle) return;
    panel.classList.add("compound-tv-ready");
    toggle.addEventListener("click", function () {
      if (panel.classList.contains("tv-expanded")) {
        closeExpanded();
        return;
      }
      closeExpanded();
      panel.classList.add("tv-expanded");
      document.body.classList.add("compound-tv-scroll-lock");
      toggle.textContent = "Close chart";
      toggle.setAttribute("aria-pressed", "true");
      toggle.setAttribute("aria-label", "Close enlarged stock chart");
      // If the user taps expand before reaching the lazy-load threshold.
      loadChart(panel);
      refreshChartSize();
    });
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeExpanded();
  });

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
