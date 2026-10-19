from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from claude_kit import iterm, theme
from claude_kit.paths import Paths
from claude_kit.theme import Theme


def _no_waiter(_: Paths) -> None:
    pass


@pytest.fixture
def paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Paths]:
    """A Mac with no kit, no Claude Code settings and no iTerm2, in a temporary home folder."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("CLAUDE_KIT_HOME", raising=False)
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    monkeypatch.setattr(iterm, "is_installed", lambda: False)
    monkeypatch.setattr(iterm, "default_guid", lambda: None)
    monkeypatch.setattr(iterm, "cancel_pending_default", _no_waiter)
    yield Paths.for_home(tmp_path)


@pytest.fixture
def moonlit(paths: Paths) -> Theme:
    return theme.find(paths, "moonlit")
