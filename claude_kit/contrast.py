"""WCAG 2.2 contrast between theme colors and the terminal background."""

from __future__ import annotations

from dataclasses import dataclass

from claude_kit.color import to_rgb

TEXT_MINIMUM = 4.5
GRAPHIC_MINIMUM = 3.0
# Roles drawn as text must be readable; the icon is a graphic. Divider and track are decorative.
TEXT_ROLES = (
    "brand",
    "accent",
    "accent_soft",
    "ok",
    "warn",
    "danger",
    "merged",
    "bright",
    "caption",
    "detail",
)
GRAPHIC_ROLES = ("icon",)


def luminance(hex_color: str) -> float:
    def linear(channel: float) -> float:
        return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4

    r, g, b = (linear(channel / 255) for channel in to_rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


@dataclass(frozen=True)
class Shortfall:
    role: str
    color: str
    ratio: float
    minimum: float

    def __str__(self) -> str:
        return (
            f"{self.role} {self.color} has {self.ratio:.2f}:1 against the background, needs {self.minimum}:1"
        )


def shortfalls(palette: dict[str, str], background: str) -> list[Shortfall]:
    checks = [(role, TEXT_MINIMUM) for role in TEXT_ROLES] + [
        (role, GRAPHIC_MINIMUM) for role in GRAPHIC_ROLES
    ]
    found = [
        Shortfall(role, palette[role], ratio(palette[role], background), minimum) for role, minimum in checks
    ]
    return [s for s in found if s.ratio < s.minimum]
