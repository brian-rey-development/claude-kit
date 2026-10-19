from __future__ import annotations

from PIL import Image

from claude_kit import art

RED, BLUE = "#FF0000", "#0000FF"


def test_runs_merge_neighbours_and_pack_two_pixel_rows() -> None:
    grid: art.Grid = [[RED, RED, None], [RED, BLUE, None]]
    assert art.to_runs(grid) == [
        [
            {"text": "█", "fg": RED, "bg": None},
            {"text": "▀", "fg": RED, "bg": BLUE},
            {"text": " ", "fg": None, "bg": None},
        ]
    ]


def test_despeckle_removes_a_lone_pixel() -> None:
    grid: art.Grid = [[RED] * 3, [RED, BLUE, RED], [RED] * 3]
    assert art.despeckle(grid)[1][1] == RED


def test_render_keeps_the_requested_width() -> None:
    image = Image.new("RGBA", (40, 20), RED)
    rendered = art.render(image, 12, [RED, BLUE])
    assert art.width(rendered) == 12
    assert len(rendered) == 3
