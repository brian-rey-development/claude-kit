"""Draws Moonlit's art from shapes: a crescent moon, a cloud and three sparkles. Released under CC0.

Usage: python draw.py <out_dir>    writes card.png (the welcome card) and icon.png (the font glyph)
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

SIZE = 600
MOON, MOON_SHADE = "#F3E3B5", "#D8C28A"
CLOUD, CLOUD_SHADE = "#DDE2F7", "#AEB6E6"
SPARKLE = "#E8C170"

Point = tuple[float, float]


def disc(draw: ImageDraw.ImageDraw, center: Point, radius: float, fill: str | int) -> None:
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill)


def crescent() -> Image.Image:
    moon = Image.new("RGBA", (SIZE, SIZE))
    draw = ImageDraw.Draw(moon)
    disc(draw, (290, 310), 230, MOON_SHADE)
    disc(draw, (302, 298), 218, MOON)
    cut = Image.new("L", (SIZE, SIZE), 255)
    disc(ImageDraw.Draw(cut), (420, 205), 180, 0)
    moon.putalpha(Image.composite(moon.getchannel("A"), cut, cut))
    return moon


def sparkle(draw: ImageDraw.ImageDraw, center: Point, radius: float) -> None:
    x, y = center
    waist = radius * 0.28
    points = [
        (x, y - radius),
        (x + waist, y - waist),
        (x + radius, y),
        (x + waist, y + waist),
        (x, y + radius),
        (x - waist, y + waist),
        (x - radius, y),
        (x - waist, y - waist),
    ]
    draw.polygon(points, fill=SPARKLE)


def puffs(draw: ImageDraw.ImageDraw, drop: float, fill: str) -> None:
    for (x, y), radius in (((175, 500), 58), ((250, 470), 72), ((325, 505), 52)):
        disc(draw, (x, y + drop), radius, fill)
    draw.rounded_rectangle((100, 500 + drop, 400, 580 + drop), radius=40, fill=fill)


def cloud(draw: ImageDraw.ImageDraw) -> None:
    puffs(draw, 14, CLOUD_SHADE)
    puffs(draw, 0, CLOUD)


def card() -> Image.Image:
    image = crescent()
    draw = ImageDraw.Draw(image)
    cloud(draw)
    for center, radius in (((450, 250), 66), ((560, 95), 40)):
        sparkle(draw, center, radius)
    return image.crop(image.getbbox())


def icon() -> Image.Image:
    image = crescent()
    return image.crop(image.getbbox())


if __name__ == "__main__":
    out = Path(sys.argv[1])
    card().save(out / "card.png")
    icon().save(out / "icon.png")
