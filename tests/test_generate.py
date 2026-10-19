from __future__ import annotations

from pathlib import Path

import pytest

from claude_kit import art, contrast, generate
from claude_kit.cli import main
from claude_kit.paths import KIT_ROOT, Paths

CARD = KIT_ROOT / "themes" / "moonlit" / "source" / "card.png"


def request(appearance: generate.Appearance, card: Path = CARD) -> generate.Request:
    return generate.Request(
        theme_id="fresh",
        name="Fresh",
        tagline="Hello",
        emoji="⭐",
        author="test",
        appearance=appearance,
        card=card,
        icon=card,
        sampling="majority",
    )


@pytest.mark.parametrize("appearance", ["dark", "light"])
def test_generated_palettes_are_readable(paths: Paths, appearance: generate.Appearance) -> None:
    data = generate.theme_data(request(appearance), art.open_image(CARD), paths.schema)
    assert contrast.shortfalls(data["palette"], data["terminal"]["background"]) == []
    assert len(data["terminal"]["ansi"]) == 16


def test_readable_reaches_the_minimum() -> None:
    assert contrast.ratio(generate.readable("#333333", "#111111"), "#111111") >= contrast.TEXT_MINIMUM


@pytest.mark.parametrize("flags", [[], ["--light"], ["--sampling", "average"]])
def test_new_theme_passes_its_own_check(paths: Paths, flags: list[str]) -> None:
    assert main(["new-theme", "fresh", "--image", str(CARD), *flags]) == 0
    assert main(["check", "fresh"]) == 0


def test_a_bad_image_leaves_no_half_made_theme(paths: Paths, tmp_path: Path) -> None:
    broken = tmp_path / "broken.png"
    broken.write_text("not an image")
    assert main(["new-theme", "fresh", "--image", str(broken)]) == 1
    assert list(paths.user_themes.glob("*")) == []
