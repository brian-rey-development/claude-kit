"""Hex colors and the arithmetic every part of the kit shares."""

from __future__ import annotations

from collections.abc import Sequence

Rgb = tuple[int, int, int]


def to_rgb(hex_color: str) -> Rgb:
    value = hex_color.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def to_hex(rgb: Sequence[int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb[:3])


def mix(color: str, base: str, amount: float) -> str:
    """`amount` of `color` over `base`, so 0 gives `base` and 1 gives `color`."""
    return to_hex([round(c * amount + b * (1 - amount)) for c, b in zip(to_rgb(color), to_rgb(base))])


def lighten(color: str, amount: float = 0.25) -> str:
    return mix("#FFFFFF", color, amount)


def chroma(color: str) -> float:
    """How colorful a color is, from 0 for any gray to 1 for a pure hue, at any lightness."""
    channels = to_rgb(color)
    return (max(channels) - min(channels)) / 255


def sgr(foreground: str | None, background: str | None = None) -> str:
    """The SGR parameters that paint text in these colors, for an escape sequence."""
    codes = [f"38;2;{';'.join(map(str, to_rgb(foreground)))}"] if foreground else []
    codes += [f"48;2;{';'.join(map(str, to_rgb(background)))}"] if background else []
    return ";".join(codes)
