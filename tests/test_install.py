from __future__ import annotations

import json

import pytest

from claude_kit import font, install, iterm, state
from claude_kit.paths import Paths
from claude_kit.theme import Theme

BEFORE = {"model": "opus", "env": {"FOO": "1"}}


@pytest.fixture
def installed(paths: Paths, moonlit: Theme) -> Paths:
    paths.claude_settings.parent.mkdir(parents=True)
    paths.claude_settings.write_text(json.dumps(BEFORE))
    install.execute(install.apply_steps(paths, moonlit, iterm_default=False))
    return paths


def test_apply_sets_up_every_piece(installed: Paths, moonlit: Theme) -> None:
    assert font.is_current(moonlit, installed.fonts)
    assert (installed.claude_themes / "moonlit.json").exists()
    assert installed.current.resolve() == moonlit.directory
    assert state.load(installed).theme == "moonlit"


def test_uninstall_leaves_no_trace(installed: Paths) -> None:
    install.execute(install.uninstall_steps(installed))
    assert json.loads(installed.claude_settings.read_text()) == BEFORE
    leftovers = [p for p in installed.home.rglob("*") if p.is_file() and installed.backups not in p.parents]
    assert leftovers == [installed.claude_settings]


def test_uninstall_removes_what_a_preview_left(paths: Paths, moonlit: Theme) -> None:
    record = state.load(paths)
    install.ensure_font(paths, moonlit, record)
    state.save(paths, record)
    install.execute(install.uninstall_steps(paths))
    assert not font.path_for(moonlit, paths.fonts).exists()
    assert not paths.claude_settings.exists()


def test_a_failure_after_the_settings_step_can_still_be_undone(
    paths: Paths, moonlit: Theme, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths.claude_settings.parent.mkdir(parents=True)
    paths.claude_settings.write_text(json.dumps(BEFORE))

    def broken_profile(*_: object, **__: object) -> None:
        raise OSError("disk full")

    def plain_profile(_: str | None) -> iterm.BaseProfile:
        return iterm.BaseProfile(None, 14)

    monkeypatch.setattr(iterm, "is_installed", lambda: True)
    monkeypatch.setattr(iterm, "base_profile", plain_profile)
    monkeypatch.setattr(iterm, "write_profile", broken_profile)
    with pytest.raises(OSError, match="disk full"):
        install.execute(install.apply_steps(paths, moonlit, iterm_default=False))
    install.execute(install.uninstall_steps(paths))
    assert json.loads(paths.claude_settings.read_text()) == BEFORE
    assert not font.path_for(moonlit, paths.fonts).exists()


def test_a_symlinked_settings_file_stays_a_symlink(paths: Paths, moonlit: Theme) -> None:
    dotfiles = paths.home / "dotfiles" / "settings.json"
    dotfiles.parent.mkdir()
    dotfiles.write_text(json.dumps(BEFORE))
    paths.claude_settings.parent.mkdir(parents=True)
    paths.claude_settings.symlink_to(dotfiles)
    install.execute(install.apply_steps(paths, moonlit, iterm_default=False))
    assert paths.claude_settings.is_symlink()
    assert json.loads(dotfiles.read_text())["theme"] == "custom:moonlit"
