from types import SimpleNamespace

from PIL import Image

from compound.site import build as builder


def test_discover_derivatives_reused_without_reencoding(monkeypatch, tmp_path):
    site = tmp_path / "site"
    image_path = site / "static" / "images" / "hero.jpg"
    image_path.parent.mkdir(parents=True)
    Image.new("RGB", (80, 50), (80, 100, 120)).save(image_path)
    monkeypatch.setattr(builder, "HERE", site)
    monkeypatch.setenv("COMPOUND_ARTICLE_CACHE_DIR", str(tmp_path / "render-cache"))

    article = SimpleNamespace(slug="test-discover", image="/static/images/hero.jpg")
    public = tmp_path / "public"
    builder.generate_discover_images(article, public)
    expected = [public / "static" / "discover" / f"test-discover-{ratio}.webp"
                for ratio in ("1x1", "4x3", "16x9")]
    assert all(file.is_file() and file.stat().st_size for file in expected)
    for file in expected:
        file.unlink()

    def should_not_decode(*args, **kwargs):
        raise AssertionError("cached derivatives should not open source image")

    monkeypatch.setattr(builder.Image, "open", should_not_decode)
    builder.generate_discover_images(article, public)
    assert all(file.is_file() and file.stat().st_size for file in expected)
