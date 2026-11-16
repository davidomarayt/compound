"""Claude logo cover regression: only self-hosted artwork; no image API needed."""
from pathlib import Path

from PIL import Image

from scripts.render_editorial_heroes import render_claude_logo_cover

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "content/wealth/anthropic-ipo-2026-prospectus-numbers-valuation.md"
BRAND = ROOT / "compound/site/static/images/brand"


def test_claude_ipo_pins_authentic_logo_without_runtime_wikimedia_download():
    text = ARTICLE.read_text(encoding="utf-8")
    assert "File:Claude_AI_logo.svg" in text
    assert "hero_image_url:" not in text
    assert "require_pinned_hero: true" in text
    assert "no endorsement implied" in text
    assert "TechCrunch_Disrupt_2023_02.jpg" not in text
    assert "social_image: /static/images/evergreen/anthropic-ipo-2026-prospectus-numbers-valuation.jpg" in text
    for asset in ("claude-mark.png", "claude-wordmark.png"):
        with Image.open(BRAND / asset) as image:
            assert image.format == "PNG"
            assert min(image.size) >= 500


def test_hero_is_a_valid_jpeg_with_unwarped_logo_assets(tmp_path):
    mark = tmp_path / "mark.png"
    wordmark = tmp_path / "wordmark.png"
    output = tmp_path / "cover.jpg"
    Image.new("RGBA", (512, 512), (217, 119, 87, 255)).save(mark)
    Image.new("RGBA", (1280, 300), (20, 20, 20, 255)).save(wordmark)
    render_claude_logo_cover(output, mark, wordmark)
    with Image.open(output) as image:
        assert image.format == "JPEG" and image.size == (1600, 900)
        # Neutral canvas is untouched, while both original colours stay legible.
        assert image.getpixel((0, 0)) == (250, 249, 245)
        assert image.getpixel((200, 450))[0] > 185
        assert image.getpixel((800, 450))[0] < 80
