import datetime as dt
import unittest
from pathlib import Path
from unittest.mock import patch

import feedparser

from scripts import news_radar as radar


class FreshnessTests(unittest.TestCase):
    def test_feed_to_shortlist(self):
        now = dt.datetime(2026, 11, 2, 5, 58, tzinfo=dt.timezone.utc)
        entries = [
            ("missing", "", ""),
            ("EIA missing year", "Fri, 09 Oct  09:00:00 EST", ""),
            ("invalid day", "2026-11-31T00:00:00Z", ""),
            ("no timezone", "2026-11-02T04:00:00", ""),
            ("update only", "", "2026-11-02T05:58:00Z"),
            ("revised", "2026-10-09T14:00:00Z", "2026-11-02T05:58:00Z"),
            ("stale", "2026-10-31T17:57:59Z", ""),
            ("future", "2026-11-02T05:58:01Z", ""),
            ("boundary", "2026-10-31T13:58:00-04:00", ""),
            ("current", "2026-11-02T05:58:00Z", ""),
        ]
        atom = '<feed xmlns="http://www.w3.org/2005/Atom">' + "".join(
            f'<entry><title>{title}</title><link href="https://example.com/{i}"/>'
            + (f"<published>{published}</published>" if published else "")
            + (f"<updated>{updated}</updated>" if updated else "") + "</entry>"
            for i, (title, published, updated) in enumerate(entries)
        ) + "</feed>"
        feed = feedparser.parse(atom)
        with patch.object(radar.feedparser, "parse", return_value=feed), patch.object(
            Path, "read_text", return_value="feeds: [{url: fixture, default_tags: [wealth]}]"
        ), patch.object(radar.dt, "datetime", wraps=dt.datetime) as clock:
            clock.now.return_value = now
            items = radar.fetch(Path("fixture"), 36, 25)
        self.assertEqual([item.title for item in items], ["current", "boundary"])
        self.assertEqual(items[0].published, now)

    def test_rss_pubdate(self):
        for raw, expected in [
            ("Fri, 09 Oct  09:00:00 EST", None),
            ("Fri, 09 Oct 2026 09:00:00 EST", dt.datetime(2026, 10, 9, 14, tzinfo=dt.timezone.utc)),
        ]:
            with self.subTest(raw=raw):
                rss = f"<rss><channel><item><pubDate>{raw}</pubDate></item></channel></rss>"
                self.assertEqual(radar.parse_date(feedparser.parse(rss).entries[0]), expected)
