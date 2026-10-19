from __future__ import annotations

import re
from pathlib import Path

import pytest

from claude_kit import sample
from claude_kit.jsonfile import JsonObject
from claude_kit.paths import Paths
from claude_kit.theme import Theme

ESCAPES = re.compile(r"\x1b\[[0-9;]*m|\x1b\]8;;[^\x1b]*\x1b\\")
WIDE_ICON_EXTRA = 1


@pytest.mark.parametrize("columns", [200, 120, 80, 60, 40])
def test_rows_fit_the_terminal(paths: Paths, moonlit: Theme, columns: int) -> None:
    result = sample.statusline(paths, moonlit, columns, paths.kit)
    assert result.returncode == 0, result.stderr
    rows = result.stdout.splitlines()
    assert len(rows) == 3
    assert all(len(ESCAPES.sub("", row)) + WIDE_ICON_EXTRA <= columns for row in rows)


@pytest.mark.parametrize("used", [5, 55, 61, 80, 97])
def test_every_meter_level_renders(
    paths: Paths, moonlit: Theme, used: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    session = sample.session(paths.kit)
    session["context_window"]["used_percentage"] = used
    session["rate_limits"]["five_hour"]["used_percentage"] = used

    def fixed(_: Path) -> JsonObject:
        return session

    monkeypatch.setattr(sample, "session", fixed)
    result = sample.statusline(paths, moonlit, 120, paths.kit)
    assert result.returncode == 0, result.stderr
    assert f"{used}%" in ESCAPES.sub("", result.stdout)
