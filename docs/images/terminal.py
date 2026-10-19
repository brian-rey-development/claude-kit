"""Draws ANSI terminal output as a PNG in a theme's colors, so the screenshots show real kit output."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from claude_kit.color import mix
from claude_kit.theme import Theme

FONT = "/System/Library/Fonts/Menlo.ttc"
REGULAR, BOLD = 0, 1
FONT_SIZE, LINE_HEIGHT, PADDING = 26, 34, 36
TITLE_BAR, CORNER, DOT_RADIUS = 52, 18, 8
DOT_COLORS = ("#FF5F57", "#FEBC2E", "#28C840")
SGR = re.compile(r"\x1b\[([0-9;]*)m")
OTHER_ESCAPES = re.compile(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b\[[0-9;?]*[A-Za-ln-z]")
BLOCKS = {"█": (True, True), "▀": (True, False), "▄": (False, True)}


@dataclass
class Pen:
    fg: str | None = None
    bg: str | None = None
    bold: bool = False
    dim: bool = False


@dataclass(frozen=True)
class Cell:
    char: str
    fg: str | None
    bg: str | None
    bold: bool
    dim: bool


def _truecolor(codes: list[int], index: int) -> str:
    return "#{:02X}{:02X}{:02X}".format(*codes[index + 2 : index + 5])


def _apply(pen: Pen, codes: list[int], ansi: list[str]) -> None:
    index = 0
    while index < len(codes):
        code = codes[index]
        if code == 0:
            pen.fg, pen.bg, pen.bold, pen.dim = None, None, False, False
        elif code == 1:
            pen.bold = True
        elif code == 2:
            pen.dim = True
        elif code == 22:
            pen.bold = pen.dim = False
        elif code == 38:
            pen.fg = _truecolor(codes, index)
            index += 4
        elif code == 48:
            pen.bg = _truecolor(codes, index)
            index += 4
        elif code == 39:
            pen.fg = None
        elif code == 49:
            pen.bg = None
        elif 30 <= code <= 37 or 90 <= code <= 97:
            pen.fg = ansi[code - 30 if code < 90 else code - 82]
        index += 1


def parse(text: str, ansi: list[str]) -> list[list[Cell]]:
    pen = Pen()
    rows: list[list[Cell]] = []
    for line in OTHER_ESCAPES.sub("", text).split("\n"):
        row: list[Cell] = []
        position = 0
        for match in [*SGR.finditer(line), None]:
            end = match.start() if match else len(line)
            row += [Cell(char, pen.fg, pen.bg, pen.bold, pen.dim) for char in line[position:end]]
            if match:
                _apply(pen, [int(code or 0) for code in match.group(1).split(";")], ansi)
                position = match.end()
        rows.append(row)
    return rows


def _wide(char: str) -> bool:
    return unicodedata.east_asian_width(char) in ("W", "F")


def span(cell: Cell, theme: Theme) -> int:
    return theme.icon_cells if cell.char == theme.icon else 1 + _wide(cell.char)


def wrapped(line: list[Cell], columns: int, theme: Theme) -> list[list[Cell]]:
    """The line broken where a terminal of this width would break it."""
    rows: list[list[Cell]] = [[]]
    used = 0
    for cell in line:
        if used + span(cell, theme) > columns:
            rows.append([])
            used = 0
        rows[-1].append(cell)
        used += span(cell, theme)
    return rows


@dataclass
class Window:
    theme: Theme
    columns: int
    rows: int
    title: str = ""
    image: Image.Image = field(init=False)

    def __post_init__(self) -> None:
        self.fonts = [ImageFont.truetype(FONT, FONT_SIZE, index=index) for index in (REGULAR, BOLD)]
        self.cell = self.fonts[REGULAR].getlength("M")
        background = self.theme.terminal["background"]
        width = round(PADDING * 2 + self.cell * self.columns)
        height = TITLE_BAR + PADDING * 2 + LINE_HEIGHT * self.rows
        self.image = Image.new("RGBA", (width, height))
        self.draw = ImageDraw.Draw(self.image)
        self.draw.rounded_rectangle(
            (0, 0, width - 1, height - 1),
            CORNER,
            fill=background,
            outline=mix(self.theme.terminal["foreground"], background, 0.14),
            width=2,
        )
        self._title_bar()

    def _title_bar(self) -> None:
        middle = TITLE_BAR // 2
        for index, color in enumerate(DOT_COLORS):
            x = CORNER + 8 + index * DOT_RADIUS * 3
            box = (x - DOT_RADIUS, middle - DOT_RADIUS, x + DOT_RADIUS, middle + DOT_RADIUS)
            self.draw.ellipse(box, color)
        font = self.fonts[REGULAR].font_variant(size=FONT_SIZE - 6)
        self.draw.text(
            (self.image.width / 2, TITLE_BAR / 2),
            self.title,
            font=font,
            fill=self.theme.palette["caption"],
            anchor="mm",
        )

    def _box(self, column: float, row: int, width: float, half: int | None = None) -> tuple[int, ...]:
        left = round(PADDING + column * self.cell)
        right = round(PADDING + (column + width) * self.cell)
        top = TITLE_BAR + PADDING + row * LINE_HEIGHT
        if half is None:
            return (left, top, right, top + LINE_HEIGHT)
        middle = top + LINE_HEIGHT // 2
        return (left, top, right, middle) if half == 0 else (left, middle, right, top + LINE_HEIGHT)

    def _colors(self, cell: Cell) -> tuple[str, str | None]:
        foreground = cell.fg or self.theme.terminal["foreground"]
        if cell.dim:
            foreground = mix(foreground, self.theme.terminal["background"], 0.55)
        return foreground, cell.bg

    def _icon(self, column: int, row: int) -> None:
        icon = Image.open(self.theme.directory / "glyph" / "icon.png").convert("RGBA")
        icon.thumbnail((round(self.cell * self.theme.icon_cells), LINE_HEIGHT - 4))
        left, top, _, _ = self._box(column, row, self.theme.icon_cells)
        self.image.alpha_composite(icon, (left, top + (LINE_HEIGHT - icon.height) // 2))

    def _cell(self, cell: Cell, column: int, row: int) -> None:
        foreground, background = self._colors(cell)
        if background:
            self.draw.rectangle(self._box(column, row, span(cell, self.theme)), background)
        if cell.char == self.theme.icon:
            self._icon(column, row)
        elif cell.char in BLOCKS:
            for half, painted in enumerate(BLOCKS[cell.char]):
                if painted:
                    self.draw.rectangle(self._box(column, row, 1, half), foreground)
        elif not cell.char.isspace():
            left, top, _, _ = self._box(column, row, 1)
            font = self.fonts[BOLD if cell.bold else REGULAR]
            self.draw.text((left, top + LINE_HEIGHT / 2), cell.char, font=font, fill=foreground, anchor="lm")

    def write(self, lines: list[list[Cell]]) -> None:
        for row, line in enumerate(lines):
            column = 0
            for cell in line:
                self._cell(cell, column, row)
                column += span(cell, self.theme)

    def save(self, out: Path) -> None:
        self.image.save(out)


def screenshot(theme: Theme, text: str, out: Path, *, columns: int, title: str) -> None:
    parsed = parse(text.rstrip("\n"), theme.terminal["ansi"])
    lines = [row for line in parsed for row in wrapped(line, columns, theme)]
    window = Window(theme, columns, len(lines), title)
    window.write(lines)
    window.save(out)
