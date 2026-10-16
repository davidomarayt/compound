#!/usr/bin/env python3
"""Render approved, article-specific Compound editorial graphics, never generic covers.

The output is deliberately generated during every build so no remote image API,
shared stock photo, or static-media commit is required for these pinned covers.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "compound/site/static/images/news/one-income-vs-two-incomes-ireland-2027.jpg"
W, H = 1600, 900

def font(size: int, bold: bool = False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    options = [
        f"/usr/share/fonts/truetype/dejavu/{name}",
        f"/usr/local/share/fonts/{name}",
        name,
    ]
    for option in options:
        try:
            return ImageFont.truetype(option, size)
        except OSError:
            continue
    return ImageFont.load_default()

def text(draw, xy, label, size, colour, bold=False, anchor=None):
    draw.text(xy, label, font=font(size, bold), fill=colour, anchor=anchor,
              stroke_width=0)

def person(draw, cx, cy, colour):
    draw.ellipse((cx-18, cy-24, cx+18, cy+12), fill=colour)
    draw.rounded_rectangle((cx-30, cy+17, cx+30, cy+68), radius=15, fill=colour)

def make():
    im = Image.new("RGB", (W, H), "#0c2133")
    d = ImageDraw.Draw(im)
    # restrained geometric editorial background, never photo/stock filler
    d.ellipse((-340, -430, 630, 390), fill="#14394b")
    d.ellipse((1220, -330, 2050, 530), fill="#122e40")
    d.rounded_rectangle((60, 48, 1540, 850), radius=38, fill="#102b3c",
                        outline="#416070", width=2)

    d.rounded_rectangle((105, 86, 288, 134), radius=12, fill="#cfe9df")
    text(d, (126, 100), "IRELAND 2027", 23, "#174a40", bold=True)
    text(d, (1484, 102), "COMPOUND.IE", 29, "#e2eceb", bold=True, anchor="ra")

    text(d, (105, 163), "SAME HOUSEHOLD INCOME", 35, "#dbe7ed", bold=True)
    text(d, (105, 217), "€100,000", 83, "#ffffff", bold=True)
    text(d, (655, 236), "gross per year", 30, "#b3cdd3")

    left, right = (100, 340, 758, 731), (842, 340, 1500, 731)
    d.rounded_rectangle(left, radius=30, fill="#e5f4ed")
    d.rounded_rectangle(right, radius=30, fill="#e8edf3")

    # Simple human silhouettes make the two-earning-household contrast immediate.
    person(d, 174, 404, "#0d6954")
    person(d, 259, 404, "#0d6954")
    person(d, 915, 404, "#253c57")
    person(d, 996, 404, "#8d9dae")

    text(d, (310, 368), "TWO EARNERS", 27, "#0c6554", True)
    text(d, (1063, 368), "ONE EARNER", 27, "#264562", True)
    text(d, (135, 493), "€50k + €50k", 40, "#1c3b34", True)
    text(d, (875, 493), "€100k + €0", 40, "#203d57", True)

    d.line((140, 574, 718, 574), fill="#b9d6ca", width=3)
    d.line((881, 574, 1460, 574), fill="#c0ccd9", width=3)
    text(d, (140, 595), "ANNUAL TAKE-HOME PAY", 22, "#4c6960", True)
    text(d, (880, 595), "ANNUAL TAKE-HOME PAY", 22, "#516579", True)
    text(d, (138, 630), "€80,679", 66, "#075d46", True)
    text(d, (878, 630), "€71,123", 66, "#193650", True)

    # Difference claim sits in the safe middle for common Open Graph crops.
    d.rounded_rectangle((530, 282, 1070, 346), radius=17, fill="#f5c85f")
    text(d, (800, 314), "€9,556 MORE TAKE-HOME", 28, "#1d2b2d", True, anchor="mm")

    text(d, (106, 771),
         "Illustrative jointly assessed PAYE households with a qualifying child.",
         22, "#b9ced4")
    text(d, (106, 807),
         "Includes Home Carer Tax Credit where eligible. 2027 announced tax rules.",
         20, "#9bb8bf")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUTPUT, "JPEG", quality=91, optimize=True, progressive=True,
            subsampling=0)
    with Image.open(OUTPUT) as check:
        assert check.size == (W, H) and check.format == "JPEG"
    print(f"Approved editorial hero generated: {OUTPUT}")

if __name__ == "__main__":
    make()
