from __future__ import annotations

import pytest

from claude_kit import contrast


@pytest.mark.parametrize(
    ("foreground", "background", "expected"),
    [("#000000", "#FFFFFF", 21.0), ("#FFFFFF", "#FFFFFF", 1.0), ("#777777", "#FFFFFF", 4.48)],
)
def test_ratio_matches_wcag(foreground: str, background: str, expected: float) -> None:
    assert contrast.ratio(foreground, background) == pytest.approx(expected, abs=0.01)


def test_shortfalls_name_each_unreadable_role() -> None:
    palette: dict[str, str] = dict.fromkeys((*contrast.TEXT_ROLES, *contrast.GRAPHIC_ROLES), "#FFFFFF")
    palette["caption"] = "#222222"
    found = contrast.shortfalls(palette, "#111111")
    assert [shortfall.role for shortfall in found] == ["caption"]
