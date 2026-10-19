"""Draws the sunflower that the README turns into a theme with `kit new-theme`. Released under CC0."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

SIZE = 600
CENTER = (300, 230)
PETAL, PETAL_SHADE = "#F6C33B", "#E0952B"
SEED, SEED_SHADE = "#6B4226", "#4A2C18"
STEM, LEAF = "#4F8A3E", "#76B35A"
PETALS = 16

Point = tuple[float, float]


def toward(origin: Point, angle: float, distance: float) -> Point:
    return origin[0] + distance * math.cos(angle), origin[1] + distance * math.sin(angle)


def petals(draw: ImageDraw.ImageDraw, turn: float, length: float, fill: str) -> None:
    for index in range(PETALS):
        angle = 2 * math.pi * (index + turn) / PETALS
        base = [toward(CENTER, angle + side, 70) for side in (-0.2, 0.2)]
        draw.polygon([base[0], toward(CENTER, angle, length), base[1]], fill=fill)


def head(draw: ImageDraw.ImageDraw) -> None:
    petals(draw, 0.5, 190, PETAL_SHADE)
    petals(draw, 0, 175, PETAL)
    for radius, fill in ((82, SEED_SHADE), (66, SEED)):
        x, y = CENTER
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill)


def leaf(image: Image.Image, center: Point, tilt: float) -> None:
    shape = Image.new("RGBA", (200, 80))
    ImageDraw.Draw(shape).ellipse((0, 0, 199, 79), fill=LEAF)
    turned = shape.rotate(tilt, expand=True)
    image.alpha_composite(turned, (round(center[0] - turned.width / 2), round(center[1] - turned.height / 2)))


def card() -> Image.Image:
    image = Image.new("RGBA", (SIZE, SIZE + 120))
    draw = ImageDraw.Draw(image)
    draw.rectangle((290, 300, 310, SIZE + 110), fill=STEM)
    leaf(image, (215, 520), 30)
    leaf(image, (385, 450), -30)
    head(draw)
    return image.crop(image.getbbox())


def icon() -> Image.Image:
    image = Image.new("RGBA", (SIZE, SIZE))
    head(ImageDraw.Draw(image))
    return image.crop(image.getbbox())


def draw_into(out: Path) -> tuple[Path, Path]:
    card_path, icon_path = out / "sunflower.png", out / "sunflower-icon.png"
    card().save(card_path)
    icon().save(icon_path)
    return card_path, icon_path
