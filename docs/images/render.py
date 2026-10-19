"""Renders the README screenshot from a theme's real card art and real status line output.

Usage: bin/kit cards && PYTHONPATH=. .venv/bin/python docs/images/render.py <theme-id> <out.png>
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from claude_kit import art, sample, theme
from claude_kit.paths import Paths
from claude_kit.theme import Theme

FONT = "/System/Library/Fonts/Menlo.ttc"
FONT_SIZE, CELL_WIDTH, LINE_HEIGHT, PADDING = 26, 16, 34, 44
COLUMNS = 96
PROMPT = "> make me a theme from this photo"
ESCAPE = re.compile(r"\x1b\[([0-9;]*)m|\x1b\]8;;[^\x1b]*\x1b\\")


def halves(glyph: str, run: art.Run) -> tuple[art.Color, art.Color]:
    """The colors of a cell's upper and lower pixel."""
    if glyph == "█":
        return run["fg"], run["fg"]
    if glyph == "▀":
        return run["fg"], run["bg"]
    return (None, run["fg"]) if glyph == "▄" else (None, None)


def colored_spans(line: str, default: str) -> list[tuple[str, str]]:
    spans: list[tuple[str, str]] = []
    color, start = default, 0
    for match in ESCAPE.finditer(line):
        spans.append((line[start : match.start()], color))
        codes = (match.group(1) or "").split(";")
        if "38" in codes:
            red, green, blue = codes[codes.index("38") + 2 : codes.index("38") + 5]
            color = f"#{int(red):02X}{int(green):02X}{int(blue):02X}"
        elif match.group(1) == "0":
            color = default
        start = match.end()
    return [*spans, (line[start:], color)]


@dataclass
class Screen:
    chosen: Theme
    image: Image.Image

    def __post_init__(self) -> None:
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.truetype(FONT, FONT_SIZE)

    def text(self, x: int, y: int, line: str) -> None:
        for text, color in colored_spans(line, self.chosen.terminal["foreground"]):
            self.draw.text((x, y), text, font=self.font, fill=color)
            x += round(self.draw.textlength(text, font=self.font))

    def rule(self, y: int) -> None:
        self.draw.line(
            (PADDING, y, self.image.width - PADDING, y), fill=self.chosen.palette["divider"], width=2
        )

    def pixel(self, column: int, row: int, color: str) -> None:
        left, top = PADDING + column * CELL_WIDTH, PADDING + row * LINE_HEIGHT // 2
        self.image.paste(color, (left, top, left + CELL_WIDTH, top + LINE_HEIGHT // 2))

    def card(self, rows: art.Art) -> None:
        for row_index, row in enumerate(rows):
            glyphs = [(glyph, run) for run in row for glyph in run["text"]]
            for column, (glyph, run) in enumerate(glyphs):
                for half, color in enumerate(halves(glyph, run)):
                    if color:
                        self.pixel(column, row_index * 2 + half, color)


def render(theme_id: str, out: Path) -> None:
    paths = Paths.from_env()
    chosen = theme.find(paths, theme_id)
    rows = chosen.art_sizes[0]
    status = sample.statusline(paths, chosen, COLUMNS, paths.kit).stdout.splitlines()
    size = (PADDING * 2 + CELL_WIDTH * COLUMNS, PADDING * 2 + LINE_HEIGHT * (len(rows) + len(status) + 4))
    screen = Screen(chosen, Image.new("RGB", size, chosen.terminal["background"]))
    screen.card(rows)
    tagline_x = PADDING + CELL_WIDTH * (art.width(rows) + 3)
    screen.draw.text(
        (tagline_x, PADDING + LINE_HEIGHT * (len(rows) // 2)),
        chosen.tagline,
        font=screen.font,
        fill=chosen.palette["caption"],
    )
    prompt_y = PADDING + LINE_HEIGHT * (len(rows) + 1)
    screen.rule(prompt_y)
    screen.text(PADDING, prompt_y + 8, PROMPT)
    screen.rule(prompt_y + LINE_HEIGHT + 16)
    for index, line in enumerate(status):
        screen.text(PADDING, prompt_y + LINE_HEIGHT * (index + 2), line.replace(chosen.icon, "  ", 1))
    icon = Image.open(chosen.directory / "glyph" / "icon.png").convert("RGBA")
    icon.thumbnail((CELL_WIDTH * 2, LINE_HEIGHT - 6))
    screen.image.paste(icon, (PADDING, prompt_y + LINE_HEIGHT * 2 + 2), icon)
    screen.image.save(out)


if __name__ == "__main__":
    render(sys.argv[1], Path(sys.argv[2]))
