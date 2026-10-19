"""Turns an image into half-block terminal art, as rows of colored runs for the welcome card.

Each text row packs two pixel rows, the upper pixel as the color of "▀" and the lower as its background.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from typing import Callable, Literal, Optional, TypedDict

from PIL import Image, UnidentifiedImageError

from claude_kit.color import to_hex, to_rgb
from claude_kit.errors import KitError

Color = Optional[str]
Grid = list[list[Color]]
Sampling = Literal["majority", "average"]


class Run(TypedDict):
    text: str
    fg: Color
    bg: Color


Art = list[list[Run]]

OPAQUE = 128
CHANNEL_WEIGHTS = (2, 4, 3)
CARD_ROWS = (15, 10, 7)
MAX_COLUMNS = 36
CARD_COLORS = 8


def open_image(path: object) -> Image.Image:
    try:
        return Image.open(str(path)).convert("RGBA")
    except (OSError, UnidentifiedImageError) as error:
        raise KitError(
            f"{path} is not an image this kit can read.", "Use a PNG, JPEG or WebP file."
        ) from error


def nearest(rgb: Sequence[int], palette: Sequence[str]) -> str:
    def distance(candidate: str) -> int:
        return sum(w * (a - b) ** 2 for w, a, b in zip(CHANNEL_WEIGHTS, rgb, to_rgb(candidate)))

    return min(palette, key=distance)


def dominant_colors(image: Image.Image, count: int) -> list[str]:
    flat = Image.new("RGB", image.size)
    flat.paste(image, mask=image.getchannel("A"))
    quantized = flat.quantize(colors=count + 1, method=Image.Quantize.MEDIANCUT)
    raw = quantized.getpalette() or []
    by_frequency = sorted(quantized.getcolors() or [], reverse=True)
    indices = [index for _, index in by_frequency if isinstance(index, int)]
    colors = [to_hex(raw[index * 3 : index * 3 + 3]) for index in indices]
    return [color for color in colors if color != "#000000"][:count]


def _pixel(image: Image.Image, x: int, y: int, palette: Sequence[str]) -> Color:
    value = image.getpixel((x, y))
    if not isinstance(value, tuple) or value[3] < OPAQUE:
        return None
    return nearest(value, palette)


def averaged(image: Image.Image, columns: int, rows: int, palette: Sequence[str]) -> Grid:
    small = image.resize((columns, rows), Image.Resampling.BOX)
    return [[_pixel(small, x, y, palette) for x in range(columns)] for y in range(rows)]


def majority(image: Image.Image, columns: int, rows: int, palette: Sequence[str]) -> Grid:
    width, height = image.size

    def span(index: int, cells: int, size: int) -> range:
        start = index * size // cells
        return range(start, max((index + 1) * size // cells, start + 1))

    def block(x: int, y: int) -> Color:
        votes = Counter(
            _pixel(image, sx, sy, palette) for sy in span(y, rows, height) for sx in span(x, columns, width)
        )
        return votes.most_common(1)[0][0]

    return [[block(x, y) for x in range(columns)] for y in range(rows)]


SAMPLERS: dict[Sampling, Callable[[Image.Image, int, int, Sequence[str]], Grid]] = {
    "majority": majority,
    "average": averaged,
}


def despeckle(grid: Grid) -> Grid:
    """Downscaled line art leaves stray pixels whose four neighbours all share one other color."""
    out = [row[:] for row in grid]
    for y in range(1, len(grid) - 1):
        for x in range(1, len(grid[0]) - 1):
            around = {grid[y - 1][x], grid[y + 1][x], grid[y][x - 1], grid[y][x + 1]}
            if len(around) == 1 and grid[y][x] not in around:
                out[y][x] = around.pop()
    return out


def _cell(top: Color, bottom: Color) -> Run:
    if top is None:
        return Run(text=" ", fg=None, bg=None) if bottom is None else Run(text="▄", fg=bottom, bg=None)
    if bottom is None or top == bottom:
        return Run(text="█" if bottom else "▀", fg=top, bg=None)
    return Run(text="▀", fg=top, bg=bottom)


def to_runs(grid: Grid) -> Art:
    rows: Art = []
    for y in range(0, len(grid), 2):
        lower = grid[y + 1] if y + 1 < len(grid) else [None] * len(grid[y])
        row: list[Run] = []
        for cell in (_cell(top, bottom) for top, bottom in zip(grid[y], lower)):
            if row and (row[-1]["fg"], row[-1]["bg"]) == (cell["fg"], cell["bg"]):
                row[-1]["text"] += cell["text"]
            else:
                row.append(cell)
        rows.append(row)
    return rows


def render(
    image: Image.Image, columns: int, palette: Sequence[str], *, sampling: Sampling = "majority"
) -> Art:
    cropped = image.crop(image.getbbox())
    pixel_rows = max(2, round(columns * cropped.height / cropped.width / 2) * 2)
    return to_runs(despeckle(SAMPLERS[sampling](cropped, columns, pixel_rows, palette)))


def card_sizes(
    image: Image.Image, *, sampling: Sampling = "majority", colors: int = CARD_COLORS
) -> list[Art]:
    """The welcome card in three heights, largest first, so a short terminal still fits one."""
    box = image.getbbox()
    if box is None:
        raise KitError("The image is fully transparent, so there is nothing to draw.")
    aspect = (box[2] - box[0]) / (box[3] - box[1])
    palette = dominant_colors(image, colors)
    columns = [min(MAX_COLUMNS, round(rows * 2 * aspect)) for rows in CARD_ROWS]
    return [render(image, count, palette, sampling=sampling) for count in columns]


def width(art: Art) -> int:
    return sum(len(run["text"]) for run in art[0]) if art else 0
