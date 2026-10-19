from __future__ import annotations

from pathlib import Path

import pytest

from claude_kit import art, claude_theme, theme
from claude_kit.cli import main
from claude_kit.paths import KIT_ROOT, Paths

BUNDLED = sorted(path.name for path in (KIT_ROOT / "themes").iterdir() if (path / "theme.json").exists())


@pytest.mark.parametrize("theme_id", BUNDLED)
def test_bundled_themes_pass_every_check(paths: Paths, theme_id: str) -> None:
    report = theme.find(paths, theme_id).check(paths.schema)
    assert report.errors == []
    assert report.warnings == []


@pytest.mark.parametrize("theme_id", BUNDLED)
def test_card_sizes_shrink_and_stay_rectangular(paths: Paths, theme_id: str) -> None:
    sizes = theme.find(paths, theme_id).art_sizes
    assert [len(size) for size in sizes] == sorted((len(size) for size in sizes), reverse=True)
    for size in sizes:
        assert {sum(len(run["text"] or "") for run in row) for row in size} == {art.width(size)}


def test_derived_claude_theme_uses_the_palette(paths: Paths) -> None:
    moonlit = theme.find(paths, "moonlit")
    derived = claude_theme.derive(moonlit.data)
    assert derived["base"] == "dark"
    assert derived["overrides"]["claude"] == moonlit.palette["brand"]


def test_a_user_theme_replaces_a_bundled_one(paths: Paths) -> None:
    mine = paths.user_themes / "moonlit"
    mine.mkdir(parents=True)
    (mine / "theme.json").write_text((KIT_ROOT / "themes/moonlit/theme.json").read_text())
    assert theme.find(paths, "moonlit").directory == mine.resolve()


def test_a_broken_theme_does_not_stop_other_commands(paths: Paths) -> None:
    broken = paths.user_themes / "broken"
    broken.mkdir(parents=True)
    (broken / "theme.json").write_text("{ not json")
    assert [found.id for found in theme.discover(paths)] == ["moonlit"]
    assert main(["check"]) == 1
    assert main(["apply", "moonlit", "--dry-run"]) == 0


def test_a_folder_named_like_a_theme_does_not_shadow_it(
    paths: Paths, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "moonlit").mkdir()
    monkeypatch.chdir(tmp_path)
    assert theme.find(paths, "moonlit").directory == KIT_ROOT / "themes" / "moonlit"
