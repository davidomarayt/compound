"""Regression checks for production-only failure detection."""
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('live_finance', Path(__file__).parents[1] / 'scripts/verify_finance_discovery.py')
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)

@pytest.mark.parametrize('directive', ['noindex', 'googlebot: noindex', 'NONE', 'nofollow'])
def test_reject_blocking_directives(directive):
    with pytest.raises(AssertionError):
        live.check_directives([directive])


def test_parse_html_and_nested_schema():
    page = live.Page('''<link href="https://compound.ie/finance/" rel="canonical">
    <META name="Googlebot" content="noindex"><meta http-equiv="refresh" content="0;url=/">
    <a href="/stocks/aapl/">Apple</a>
    <script type="application/ld+json">{"@graph":[{"@type":["WebPage","CollectionPage"]}]}</script>''')
    assert page.canonicals == ['https://compound.ie/finance/']
    assert page.refresh and page.directives == ['noindex']
    assert page.links == ['/stocks/aapl/']
    assert set(live.schema_types(page.schemas)) == {'WebPage', 'CollectionPage'}


@pytest.mark.parametrize('status,url,mime,headers', [
    (404, 'https://compound.ie/finance/', 'text/html', []),
    (200, 'https://compound.ie/', 'text/html', []),
    (200, 'https://compound.ie/finance/', 'text/plain', []),
    (200, 'https://compound.ie/finance/', 'text/html', ['googlebot: noindex']),
])
def test_fetch_rejects_delivery_regressions(monkeypatch, status, url, mime, headers):
    class Headers:
        def get_content_type(self): return mime
        def get_all(self, key, default): return headers
        def get(self, key): return mime
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self): return b'<html>not a real page</html>'
    response = Response()
    response.status, response.url, response.headers = status, url, Headers()
    monkeypatch.setattr(live, 'urlopen', lambda *args, **kwargs: response)
    monkeypatch.setattr(live.time, 'sleep', lambda _: None)
    with pytest.raises(AssertionError):
        live.fetch('https://compound.ie/finance/', 'text/html')
