"""A copy of Apple's Monaco whose icon character draws the theme's mascot.

The glyph holds color bitmaps (sbix), which Core Text draws in color, and an outline traced from the
bitmap's opaque pixels for renderers that draw every glyph in the text color, such as iTerm2.
The font is built on each Mac from its own Monaco, so no copy of Apple's font is ever distributed.
"""

from __future__ import annotations

import hashlib
import io
import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

from fontTools.misc.timeTools import timestampNow
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, TTLibError
from fontTools.ttLib.tables import _s_b_i_x
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from fontTools.ttLib.tables._g_l_y_f import Glyph
from fontTools.ttLib.tables.sbixGlyph import Glyph as SbixGlyph
from fontTools.ttLib.tables.sbixStrike import Strike
from PIL import Image

from claude_kit.theme import Theme

BASE_FONT = Path("/System/Library/Fonts/Monaco.ttf")
GLYPH = "mascot"
STRIKES = (12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 64, 96, 128)
SMALL_IMAGE_BELOW_PPEM = 64
OUTLINE_RESOLUTION = 48
OPAQUE = 128
WIDTH_FILL, HEIGHT_FILL = 0.94, 0.9
VERSION_TAG = "claude-kit"
# Tables that describe Monaco's own bitmaps or metrics per glyph and would not cover the new one.
STALE_TABLES = ("hdmx", "bdat", "bloc", "fond", "Zapf")

Box = tuple[int, int, int, int]


def table(font: TTFont, tag: str) -> Any:  # fontTools tables carry no type information
    return cast(Any, font[tag])


def path_for(theme: Theme, fonts: Path) -> Path:
    return fonts / f"{theme.font_postscript}.ttf"


def fingerprint(theme: Theme) -> str:
    digest = hashlib.sha256(Path(__file__).read_bytes())
    digest.update(f"{theme.name}|{theme.icon}|{theme.icon_cells}".encode())
    for image in sorted((theme.directory / "glyph").glob("*.png")):
        digest.update(image.read_bytes())
    return digest.hexdigest()[:16]


def is_current(theme: Theme, fonts: Path) -> bool:
    path = path_for(theme, fonts)
    if not path.exists():
        return False
    try:
        version = table(TTFont(path, lazy=True), "name").getDebugName(5) or ""
    except TTLibError:
        return False
    return version.endswith(f"{VERSION_TAG} {fingerprint(theme)}")


def build(theme: Theme, fonts: Path, base: Path = BASE_FONT) -> Path:
    logging.getLogger("fontTools").setLevel(logging.ERROR)
    font = TTFont(base)
    large, small = _images(theme)
    box = _placement(font, large, theme.icon_cells)
    advance = table(font, "hmtx")["a"][0] * theme.icon_cells
    _add_glyph(font, _outline(large, box), advance, box[0])
    _map_codepoints(font, [ord(char) for char in theme.icon])
    _add_bitmaps(font, large, small, box)
    _rename(font, theme)
    table(font, "head").created = table(font, "head").modified = timestampNow()
    out = path_for(theme, fonts)
    out.parent.mkdir(parents=True, exist_ok=True)
    partial = out.with_name(f".{out.name}.partial")
    font.save(partial)
    partial.replace(out)
    return out


def _images(theme: Theme) -> tuple[Image.Image, Image.Image]:
    glyph = theme.directory / "glyph"
    large = Image.open(glyph / "icon.png").convert("RGBA")
    small_file = glyph / "icon-small.png"
    small = Image.open(small_file).convert("RGBA") if small_file.exists() else large
    return large.crop(large.getbbox()), small.crop(small.getbbox())


def _placement(font: TTFont, image: Image.Image, cells: int) -> Box:
    """The mascot's box in font units, centered in its cells and as large as the line allows."""
    advance = table(font, "hmtx")["a"][0] * cells
    ascent, descent = table(font, "hhea").ascent, table(font, "hhea").descent
    scale = min(advance * WIDTH_FILL / image.width, (ascent - descent) * HEIGHT_FILL / image.height)
    width, height = round(image.width * scale), round(image.height * scale)
    return ((advance - width) // 2, round((ascent + descent - height) / 2), width, height)


def _opaque_runs(mask: Image.Image) -> Iterator[tuple[int, int, int]]:
    """Each horizontal run of opaque pixels as (row, first column, column after the last)."""
    alpha = mask.tobytes()
    for y in range(mask.height):
        opaque = [value >= OPAQUE for value in alpha[y * mask.width : (y + 1) * mask.width]] + [False]
        start = None
        for x, is_opaque in enumerate(opaque):
            if is_opaque and start is None:
                start = x
            elif not is_opaque and start is not None:
                yield (y, start, x)
                start = None


def _outline(image: Image.Image, box: Box) -> Glyph:
    x0, y0, width, height = box
    scale = OUTLINE_RESOLUTION / max(image.size)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    mask = image.getchannel("A").resize(size, Image.Resampling.BOX)
    unit_x, unit_y = width / mask.width, height / mask.height
    pen = TTGlyphPen(None)
    for row, start, end in _opaque_runs(mask):
        left, right = x0 + round(start * unit_x), x0 + round(end * unit_x)
        top, bottom = y0 + height - round(row * unit_y), y0 + height - round((row + 1) * unit_y)
        pen.moveTo((left, bottom))
        pen.lineTo((left, top))
        pen.lineTo((right, top))
        pen.lineTo((right, bottom))
        pen.closePath()
    return pen.glyph()


def _add_glyph(font: TTFont, outline: Glyph, advance: int, left_bearing: int) -> None:
    order: list[str] = [*font.getGlyphOrder(), GLYPH]
    font.setGlyphOrder(order)
    table(font, "glyf").glyphOrder = order
    table(font, "glyf")[GLYPH] = outline
    table(font, "hmtx")[GLYPH] = (advance, left_bearing)
    table(font, "maxp").numGlyphs = len(order)
    for tag in STALE_TABLES:
        if tag in font:
            del font[tag]


def _map_codepoints(font: TTFont, codepoints: list[int]) -> None:
    """Emoji live above U+FFFF, which only a format 12 cmap subtable can address."""
    subtables = table(font, "cmap").tables
    if not any(subtable.format == 12 for subtable in subtables):
        bmp = next(subtable for subtable in subtables if subtable.format == 4 and subtable.isUnicode())
        full: Any = CmapSubtable.newSubtable(12)  # fontTools tables carry no type information
        full.platformID, full.platEncID, full.language, full.cmap = 0, 4, 0, dict(bmp.cmap)
        subtables.append(full)
    for subtable in subtables:
        if subtable.isUnicode() and subtable.format in (4, 12):
            subtable.cmap.update({cp: GLYPH for cp in codepoints if cp <= 0xFFFF or subtable.format == 12})


def _bitmap(image: Image.Image, ppem: int, upm: int, box: Box) -> SbixGlyph:
    x0, y0, width, height = box
    scale = ppem / upm
    png = io.BytesIO()
    image.resize(
        (max(1, round(width * scale)), max(1, round(height * scale))), Image.Resampling.LANCZOS
    ).save(png, "PNG")
    return SbixGlyph(
        glyphName=GLYPH,
        graphicType="png ",
        imageData=png.getvalue(),
        originOffsetX=round(x0 * scale),
        originOffsetY=round(y0 * scale),
    )


def _add_bitmaps(font: TTFont, large: Image.Image, small: Image.Image, box: Box) -> None:
    upm = table(font, "head").unitsPerEm
    sbix = _s_b_i_x.table__s_b_i_x("sbix")
    sbix.version, sbix.flags = 1, 1
    for ppem in STRIKES:
        strike: Any = Strike(ppem=ppem, resolution=72)  # fontTools tables carry no type information
        strike.glyphs[GLYPH] = _bitmap(small if ppem < SMALL_IMAGE_BELOW_PPEM else large, ppem, upm, box)
        sbix.strikes[ppem] = strike
    font["sbix"] = sbix


def _rename(font: TTFont, theme: Theme) -> None:
    names = {
        1: theme.font_family,
        3: f"{theme.font_postscript}-Regular",
        4: theme.font_family,
        5: f"Version 1.0; {VERSION_TAG} {fingerprint(theme)}",
        6: theme.font_postscript,
        16: theme.font_family,
    }
    for record in table(font, "name").names:
        if record.nameID in names:
            record.string = names[record.nameID]
