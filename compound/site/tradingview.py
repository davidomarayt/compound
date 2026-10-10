"""Safe, accessible TradingView price-chart panels for SEC earnings pages.

The ticker comes from the monitored company register, not arbitrary page input.
TradingView price data is distinct from the site's source-verified SEC metrics.
"""
from __future__ import annotations

from html import escape
import re


def render_tradingview_panel(symbol: str, company_name: str = "", variant: str = "compact") -> str:
    """Return progressive-enhancement markup without blocking external scripts.

    Any unrecognised ticker or variant fails closed, rather than rendering an
    arbitrary external symbol or injecting untrusted content into the DOM.
    """
    ticker = str(symbol or "").strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9.-]{0,11}", ticker):
        return ""
    if variant not in {"compact", "advanced"}:
        return ""
    # The SEC constituent register uses e.g. BRK-B / BF-B; TradingView uses dots.
    ticker = ticker.replace("-", ".")
    name = escape(str(company_name or ticker).strip())
    safe_ticker = escape(ticker, quote=True)
    heading = "Interactive stock chart" if variant == "advanced" else "Share price context"
    description = (
        "Explore the historical share price. The chart below is supplied by TradingView, "
        "not the SEC, and is separate from the financial results on this page."
        if variant == "advanced" else
        "Historical market prices, separate from the SEC financial results above."
    )
    url = "https://www.tradingview.com/symbols/" + ticker + "/"
    return (
        f'<section class="compound-tv-panel compound-tv-{variant}" '
        f'data-compound-tradingview data-tv-symbol="{safe_ticker}" data-tv-variant="{variant}" '
        f'aria-labelledby="compound-tv-title">'
        f'<div class="compound-tv-heading"><div><p class="compound-tv-eyebrow">MARKET DATA / TRADINGVIEW</p>'
        f'<h2 id="compound-tv-title">{heading}</h2>'
        f'<p class="compound-tv-description">{description}</p></div>'
        f'<span class="compound-tv-ticker">{safe_ticker}</span></div>'
        '<div class="tradingview-widget-container">'
        '<div class="tradingview-widget-container__widget" aria-label="Interactive share price chart">'
        '<p class="compound-tv-loading">Interactive chart loads as you scroll to it.</p>'
        '</div></div>'
        f'<p class="compound-tv-footnote">Market data may be delayed or unavailable for some securities. '
        f'<a href="{url}" target="_blank" rel="noopener nofollow">'
        f'{name} ({safe_ticker}) chart</a> by TradingView. '
        'TradingView branding and market-data attribution remain visible.</p>'
        '</section>'
    )
