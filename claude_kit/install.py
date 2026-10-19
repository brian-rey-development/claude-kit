"""Applying a theme and undoing it.

Each step converges, so running apply or uninstall twice changes nothing more, and each step saves the
install record as soon as it has changed something, so a step that fails halfway can still be undone.
"""

from __future__ import annotations

import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from claude_kit import card, font, iterm, jsonfile, settings, state, theme, ui, widgets
from claude_kit.paths import Paths
from claude_kit.state import State, remember
from claude_kit.theme import Theme


@dataclass(frozen=True)
class Step:
    title: str
    run: Callable[[], None]


def execute(steps: list[Step]) -> None:
    for step in steps:
        step.run()
        ui.step(step.title)


def mod_dirs(paths: Paths) -> list[str]:
    """Every folder in mods/ with a plugin manifest, so a new mini app loads with no code change."""
    manifests = sorted(paths.mods.glob("*/.claude-plugin/plugin.json"))
    return [str(manifest.parent.parent) for manifest in manifests]


def link(target: Path, link_path: Path) -> None:
    link_path.parent.mkdir(parents=True, exist_ok=True)
    if link_path.is_symlink() or link_path.exists():
        link_path.unlink()
    link_path.symlink_to(target)


def ensure_font(paths: Paths, chosen: Theme, record: State) -> None:
    remember(record.fonts, str(font.path_for(chosen, paths.fonts)))
    state.save(paths, record)
    if not font.is_current(chosen, paths.fonts):
        font.build(chosen, paths.fonts)


def write_cards(paths: Paths) -> None:
    card.write(theme.discover(paths), paths.cards)


def _link_claude_theme(paths: Paths, chosen: Theme, record: State) -> None:
    target = paths.claude_themes / f"{chosen.id}.json"
    remember(record.claude_themes, str(target))
    state.save(paths, record)
    link(chosen.directory / "claude.json", target)


def _activate(paths: Paths, chosen: Theme) -> None:
    link(chosen.directory, paths.current)
    jsonfile.write(paths.config, {**widgets.config(paths), "theme": chosen.id})


def _back_up_settings(paths: Paths) -> None:
    if paths.claude_settings.exists():
        backup = paths.backups / f"settings.{time.strftime('%Y%m%d-%H%M%S')}.json"
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(paths.claude_settings, backup)


def _write_settings(paths: Paths, chosen: Theme, record: State) -> None:
    current = jsonfile.read(paths.claude_settings, {})
    _back_up_settings(paths)
    if not record.has_settings_snapshot:
        record.settings_before = settings.snapshot(current)
    record.theme, record.mods = chosen.id, mod_dirs(paths)
    state.save(paths, record)
    values = settings.kit_values(paths, chosen.id)
    jsonfile.write(paths.claude_settings, settings.apply(current, values, record.mods))


def _write_iterm_profile(paths: Paths, chosen: Theme, record: State, make_default: bool) -> None:
    base = iterm.base_profile(record.iterm_default_before)
    iterm.write_profile(paths, chosen, base)
    if make_default and iterm.default_guid() != iterm.PROFILE_GUID:
        record.iterm_default_before = base.guid
        state.save(paths, record)
        iterm.change_default(paths, iterm.PROFILE_GUID)


def _iterm_step(paths: Paths, chosen: Theme, record: State, make_default: bool) -> Step:
    title = f"Add the iTerm2 profile {chosen.name}" + (" and make it the default" if make_default else "")
    return Step(title, lambda: _write_iterm_profile(paths, chosen, record, make_default))


def apply_steps(paths: Paths, chosen: Theme, *, iterm_default: bool) -> list[Step]:
    record = state.load(paths)
    show = paths.display
    steps = [
        Step(
            f"Build the font {chosen.font_family} in {show(paths.fonts)}",
            lambda: ensure_font(paths, chosen, record),
        ),
        Step(
            f"Add the Claude Code theme custom:{chosen.id}", lambda: _link_claude_theme(paths, chosen, record)
        ),
        Step("Write the welcome card", lambda: write_cards(paths)),
        Step(f"Make {chosen.name} the active theme in {show(paths.user)}", lambda: _activate(paths, chosen)),
        Step(
            f"Point the status line, theme and welcome card in {show(paths.claude_settings)} at the kit, "
            f"after a backup to {show(paths.backups)}",
            lambda: _write_settings(paths, chosen, record),
        ),
    ]
    return steps + ([_iterm_step(paths, chosen, record, iterm_default)] if iterm.is_installed() else [])


def _remove(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()


def _restore_settings(paths: Paths, record: State) -> None:
    if not record.has_settings_snapshot:
        return
    current = jsonfile.read(paths.claude_settings, {})
    values = settings.kit_values(paths, record.theme)
    jsonfile.write(
        paths.claude_settings, settings.restore(current, values, record.settings_before, record.mods)
    )


def _remove_iterm(paths: Paths, record: State) -> None:
    for name in (iterm.PROFILE_FILE, iterm.PREVIEW_FILE):
        _remove(paths.iterm_profiles / name)
    iterm.cancel_pending_default(paths)
    if iterm.default_guid() == iterm.PROFILE_GUID:
        iterm.change_default(paths, record.iterm_default_before)


def _remove_files(paths: Paths, record: State) -> None:
    recorded = [Path(file) for file in [*record.fonts, *record.claude_themes, record.kit_link] if file]
    generated = [paths.current, paths.cards, paths.preview_settings, paths.config]
    for path in recorded + generated:
        _remove(path)


def uninstall_steps(paths: Paths) -> list[Step]:
    record = state.load(paths)
    settings_file = paths.display(paths.claude_settings)
    return [
        Step(f"Restore what {settings_file} held before", lambda: _restore_settings(paths, record)),
        Step("Remove the iTerm2 profiles", lambda: _remove_iterm(paths, record)),
        Step(
            "Remove the fonts, the theme links and the generated files", lambda: _remove_files(paths, record)
        ),
        Step("Forget the install record", lambda: _remove(paths.state)),
    ]
