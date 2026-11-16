"""Claude logo image regression tests: preserve true trademark artwork and MIME."""
from pathlib import Path

from PIL import Image

from scripts.news_images import render_centered_logo_jpeg

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "content/wealth/anthropic-ipo-2026-prospectus-numbers-valuation.md"


def test_claude_ipo_uses_real_attributed_wordmark_not_ceo_photo():
    text = ARTICLE.read_text(encoding="utf-8")
    assert "File:Claude_AI_logo.svg" in text
    assert "1280px-Claude_AI_logo.svg.png" in text
    assert "hero_image_presentation: centered-logo" in text
    assert "no endorsement implied" in text
    assert "TechCrunch_Disrupt_2023_02.jpg" not in text
    assert "require_pinned_hero: true" in text
    assert "social_image: /static/images/evergreen/anthropic-ipo-2026-prospectus-numbers-valuation.jpg" in text


def test_logo_rasterises_to_true_landscape_jpeg_without_warping(tmp_path):
    source = tmp_path / "claude-cover.jpg"
    # Simulate the real Wikimedia PNG with transparency and wide proportions.
    Image.new("RGBA", (1280, 275), (214, 115, 84, 255)).save(source, format="PNG")
    render_centered_logo_jpeg(source)
    with Image.open(source) as result:
        assert result.format == "JPEG"
        assert result.size == (1600, 900)
        assert result.getpixel((0, 0)) == (250, 249, 245)
        assert result.getpixel((800, 450))[0] < 240
