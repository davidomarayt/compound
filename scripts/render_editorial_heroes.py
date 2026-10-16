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


def make_roadster():
    """Bespoke Roadster investment illustration. No unlicensed reveal photography."""
    target = ROOT / "compound/site/static/images/news/tesla-roadster-reveal-investment-case-2026.jpg"
    im = Image.new("RGB", (W, H), "#0c1726")
    d = ImageDraw.Draw(im)
    # Night-time editorial backdrop, smoke and launch-trail atmosphere.
    for y in range(H):
        t = y / H
        d.line((0, y, W, y), fill=(int(11+13*t), int(22+7*t), int(40+12*t)))
    for x in range(0, W, 27):
        d.line((x, 480, max(0, x - 230), 892), fill="#243143", width=2)
    d.ellipse((910, 310, 1850, 1300), fill="#203446")
    d.ellipse((1260, 420, 1970, 1080), fill="#2c3c4d")
    d.rounded_rectangle((72, 62, 1528, 833), 33, outline="#405167", width=3)
    d.rounded_rectangle((115, 103, 425, 148), 12, fill="#e8e5de")
    text(d, (140, 113), "COMPOUND / STOCKS", 22, "#243147", True)
    text(d, (1485, 118), "16 OCT 2026", 23, "#a8bdcf", True, anchor="ra")
    text(d, (114, 177), "THE TESLA ROADSTER", 60, "#ffffff", True)
    text(d, (116, 252), "A spectacular demo.", 54, "#fa796d", True)
    text(d, (116, 330), "But what is it worth?", 54, "#f2f2f0", True)
    d.line((116, 425, 860, 425), fill="#71859c", width=3)
    text(d, (117, 445), "PROTOTYPE  /  2028 PRODUCTION TARGET", 22, "#bcd0db", True)
    # Artist's stylised EV silhouette and thruster beams, distinct from news footage.
    d.polygon([(905, 665), (964, 599), (1050, 568), (1185, 559),
               (1247, 519), (1360, 528), (1433, 585), (1494, 610),
               (1529, 648), (1514, 703), (882, 703)], fill="#b52c37")
    d.polygon([(1034, 573), (1169, 570), (1239, 529),
               (1353, 538), (1408, 584)], fill="#1a2a3b")
    d.line((900, 662, 1526, 662), fill="#f57973", width=10)
    d.polygon([(904, 669), (955, 639), (949, 680)], fill="#e8c8ba")
    for cx in (1035, 1410):
        d.ellipse((cx-53, 650, cx+53, 758), fill="#0d131c", outline="#718292", width=6)
        d.ellipse((cx-22, 681, cx+22, 724), fill="#738090", outline="#bdc6cd", width=3)
    for cx, cy in ((1266, 713), (1324, 714), (1375, 708)):
        d.polygon([(cx-13, cy), (cx+10, cy), (cx+65, cy+143),
                   (cx-33, cy+151)], fill="#4e9bb6")
        d.polygon([(cx-7, cy), (cx+6, cy), (cx+21, cy+112),
                   (cx-16, cy+117)], fill="#d4e8df")
    d.line((784, 774, 1524, 774), fill="#668097", width=4)
    text(d, (114, 747), "2025 TESLA REVENUE", 22, "#a6c0ce", True)
    text(d, (115, 778), "$94.83bn", 46, "#ffffff", True)
    text(d, (515, 803), "Roadster revenue scenarios inside", 23, "#e7c7c5")
    text(d, (1484, 806), "ORIGINAL ILLUSTRATION — NOT EVENT FOOTAGE", 15, "#b4c0c9", True, anchor="ra")
    target.parent.mkdir(parents=True, exist_ok=True)
    im.save(target, "JPEG", quality=93, optimize=True, progressive=True, subsampling=0)
    with Image.open(target) as check:
        assert check.format == "JPEG" and check.size == (W, H)
    print(f"Original Roadster investment cover: {target}")


if __name__ == "__main__":
    make()
    make_roadster()
