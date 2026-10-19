"""Builds a complete theme from one image, with a readable palette, terminal colors, card art and a glyph.

Hues come from the image. Lightness is then pushed away from the background until every text role
reaches WCAG AA, so a generated theme always passes `kit check`.
"""

from __future__ import annotations

import colorsys
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from PIL import Image

from claude_kit import art, claude_theme, contrast, jsonfile
from claude_kit.color import chroma, mix, to_hex, to_rgb
from claude_kit.errors import KitError
from claude_kit.jsonfile import JsonObject

Appearance = Literal["dark", "light"]
ICON_SIZE = 256
LIGHTNESS_STEP = 0.02
STATUS_HUES = {"ok": 150, "warn": 32, "danger": 4, "merged": 270}
ANSI_HUES = (4, 140, 45, 220, 290, 185)


@dataclass(frozen=True)
class Request:
    theme_id: str
    name: str
    tagline: str
    emoji: str
    author: str
    appearance: Appearance
    card: Path
    icon: Path
    sampling: art.Sampling


@dataclass(frozen=True)
class Colors:
    roles: dict[str, str]
    background: str
    foreground: str


def hls(hue: float, lightness: float, saturation: float) -> str:
    r, g, b = colorsys.hls_to_rgb(hue / 360, lightness, saturation)
    return to_hex([round(r * 255), round(g * 255), round(b * 255)])


def components(color: str) -> tuple[float, float, float]:
    r, g, b = (channel / 255 for channel in to_rgb(color))
    hue, lightness, saturation = colorsys.rgb_to_hls(r, g, b)
    return hue * 360, lightness, saturation


def readable(color: str, background: str, minimum: float = contrast.TEXT_MINIMUM) -> str:
    """The color, moved away from the background's lightness until it reaches the minimum contrast."""
    hue, lightness, saturation = components(color)
    direction = 1 if contrast.luminance(background) < 0.5 else -1
    while contrast.ratio(color, background) < minimum and 0 < lightness < 1:
        lightness = min(1.0, max(0.0, lightness + direction * LIGHTNESS_STEP))
        color = hls(hue, lightness, saturation)
    return color


def _hue_distance(a: str, b: str) -> float:
    gap = abs(components(a)[0] - components(b)[0]) % 360
    return min(gap, 360 - gap)


def _roles(found: list[str], background: str, foreground: str, dark: bool) -> dict[str, str]:
    brand = max(found, key=chroma)
    accent = max(found, key=lambda color: _hue_distance(color, brand) * chroma(color))
    status_lightness = 0.65 if dark else 0.4
    return {
        "brand": readable(brand, background),
        "accent": readable(accent, background),
        "accent_soft": readable(mix(foreground, accent, 0.35), background),
        **{role: readable(hls(hue, status_lightness, 0.6), background) for role, hue in STATUS_HUES.items()},
        "bright": foreground,
        "caption": readable(mix(foreground, background, 0.55), background),
        "detail": readable(mix(foreground, background, 0.68), background),
        "divider": mix(brand, background, 0.3),
        "track": mix(foreground, background, 0.12),
        "icon": readable(found[0], background, contrast.GRAPHIC_MINIMUM),
    }


def colors_from(image: Image.Image, appearance: Appearance) -> Colors:
    found = art.dominant_colors(image, 8)
    if not found:
        raise KitError("The image has no opaque pixels to take colors from.")
    hue, dark = components(max(found, key=chroma))[0], appearance == "dark"
    background = hls(hue, 0.08 if dark else 0.96, 0.25)
    foreground = hls(hue, 0.9 if dark else 0.15, 0.12)
    return Colors(_roles(found, background, foreground, dark), background, foreground)


def terminal(colors: Colors, appearance: Appearance) -> JsonObject:
    roles, background, foreground = colors.roles, colors.background, colors.foreground
    dark = appearance == "dark"
    normal = [readable(hls(hue, 0.62 if dark else 0.4, 0.55), background) for hue in ANSI_HUES]
    bright = [readable(hls(hue, 0.75 if dark else 0.3, 0.6), background) for hue in ANSI_HUES]
    black, white = mix(foreground, background, 0.1), mix(foreground, background, 0.8)
    return {
        "background": background,
        "foreground": foreground,
        "bold": "#FFFFFF" if dark else "#000000",
        "cursor": roles["brand"],
        "cursor_text": background,
        "selection": mix(roles["accent"], background, 0.3),
        "selected_text": foreground,
        "link": roles["accent"],
        "tab": mix(roles["brand"], background, 0.25),
        "ansi": [black, *normal, white, mix(foreground, background, 0.45), *bright, foreground],
    }


def theme_data(request: Request, image: Image.Image, schema: Path) -> JsonObject:
    colors = colors_from(image, request.appearance)
    return {
        "$schema": str(schema),
        "id": request.theme_id,
        "name": request.name,
        "description": f"{request.name}, with colors taken from its artwork.",
        "author": request.author,
        "license": "personal",
        "appearance": request.appearance,
        "icon": {"char": request.emoji, "cells": 2},
        "tagline": request.tagline,
        "palette": colors.roles,
        "terminal": terminal(colors, request.appearance),
    }


def _write(request: Request, directory: Path, schema: Path) -> None:
    card, icon = art.open_image(request.card), art.open_image(request.icon)
    data = theme_data(request, card, schema)
    (directory / "glyph").mkdir(parents=True)
    (directory / "source").mkdir()
    jsonfile.write(directory / "theme.json", data)
    jsonfile.write(directory / "claude.json", claude_theme.derive(data))
    jsonfile.write(directory / "art.json", art.card_sizes(card, sampling=request.sampling))
    icon = icon.crop(icon.getbbox())
    icon.thumbnail((ICON_SIZE, ICON_SIZE))
    icon.save(directory / "glyph" / "icon.png")
    shutil.copy2(request.card, directory / "source" / f"card{request.card.suffix}")


def create(request: Request, directory: Path, schema: Path) -> None:
    """Builds the theme in a hidden folder beside its final place, so a failure leaves nothing behind."""
    staging = directory.with_name(f".{directory.name}.partial")
    shutil.rmtree(staging, ignore_errors=True)
    try:
        _write(request, staging, schema)
        staging.rename(directory)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
