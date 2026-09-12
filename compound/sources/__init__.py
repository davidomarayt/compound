"""Source registry. Add a source class here and it gets polled."""
from __future__ import annotations

from compound.config import Settings
from compound.sources.base import Source, SourceItem
from compound.sources.revenue import RevenueEbriefs

__all__ = ["Source", "SourceItem", "build_sources"]


def build_sources(settings: Settings) -> list[Source]:
    return [
        RevenueEbriefs(index_url=settings.revenue_ebrief_index_url, rss_url=settings.revenue_ebrief_rss_url),
    ]
