"""Health checks for an install. Each returns a finding with a fix the person can run."""

from __future__ import annotations

import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import Callable, Literal

from claude_kit import font, iterm, jsonfile, sample, settings, state, theme
from claude_kit.errors import KitError
from claude_kit.install import mod_dirs
from claude_kit.paths import Paths
from claude_kit.theme import Theme

FAST_RENDER_SECONDS = 0.3


Level = Literal["ok", "warn", "fail"]


@dataclass(frozen=True)
class Finding:
    level: Level
    message: str
    fix: str = ""


def ok(message: str) -> Finding:
    return Finding("ok", message)


def warn(message: str, fix: str = "") -> Finding:
    return Finding("warn", message, fix)


def fail(message: str, fix: str = "") -> Finding:
    return Finding("fail", message, fix)


def _version(command: list[str]) -> str | None:
    if shutil.which(command[0]) is None:
        return None
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return (result.stdout or result.stderr).strip().splitlines()[0] if result.returncode == 0 else None


def tools(_: Paths) -> list[Finding]:
    claude, jq = _version(["claude", "--version"]), _version(["jq", "--version"])
    return [
        ok(f"Claude Code {claude}")
        if claude
        else fail("Claude Code is not installed.", "https://docs.claude.com/en/docs/claude-code/setup"),
        ok(f"jq {jq}") if jq else fail("jq is not installed.", "brew install jq"),
        ok("Monaco is available") if font.BASE_FONT.exists() else fail(f"{font.BASE_FONT} is missing."),
    ]


def _installed_pieces(paths: Paths, chosen: Theme) -> list[Finding]:
    fix = f"kit apply {chosen.id}"
    link = paths.claude_themes / f"{chosen.id}.json"
    return [
        ok(f"Font {chosen.font_family}")
        if font.is_current(chosen, paths.fonts)
        else fail("The font is missing or out of date.", fix),
        ok(f"Claude Code theme custom:{chosen.id}")
        if link.exists()
        else fail(f"{paths.display(link)} is missing.", fix),
    ]


def active_theme(paths: Paths) -> list[Finding]:
    chosen = theme.current(paths)
    if chosen is None:
        return [fail("No theme is applied.", "kit setup")]
    report = chosen.check(paths.schema)
    findings = [ok(f"Theme {chosen.name} ({paths.display(chosen.directory)})")]
    findings += [fail(error, f"kit check {chosen.id}") for error in report.errors]
    findings += [warn(warning) for warning in report.warnings]
    return findings + _installed_pieces(paths, chosen)


def _drifted(paths: Paths, theme_id: str) -> list[str]:
    current = jsonfile.read(paths.claude_settings, {})
    expected = settings.kit_values(paths, theme_id)
    drifted = [".".join(key) for key, value in expected.items() if settings.get(current, key) != value]
    if any(mod not in settings.plugin_dirs(current) for mod in mod_dirs(paths)):
        drifted.append(f"env.{settings.PLUGIN_DIRS}")
    return drifted


def claude_settings(paths: Paths) -> list[Finding]:
    record = state.load(paths)
    if not record.has_settings_snapshot:
        return []
    drifted = _drifted(paths, record.theme)
    if drifted:
        return [
            warn(f"Settings changed since the install: {', '.join(drifted)}.", f"kit apply {record.theme}")
        ]
    cards = paths.mods / "welcome" / "hooks" / "cards.ts"
    card = (
        ok("Welcome card ready")
        if cards.exists()
        else fail("The welcome cards are missing.", f"kit apply {record.theme}")
    )
    return [ok("Claude Code settings point at the kit"), card]


def statusline(paths: Paths) -> list[Finding]:
    chosen = theme.current(paths)
    if chosen is None:
        return []
    started = time.monotonic()
    result = sample.statusline(paths, chosen, 120, paths.kit)
    seconds = time.monotonic() - started
    if result.returncode != 0 or not result.stdout.strip():
        return [fail("The status line does not render.", result.stderr.strip()[:300])]
    speed = f"renders in {seconds * 1000:.0f} ms"
    return [
        ok(f"Status line {speed}")
        if seconds < FAST_RENDER_SECONDS
        else warn(f"Status line is slow: {speed}.")
    ]


def terminal(paths: Paths) -> list[Finding]:
    if not iterm.is_installed():
        return [
            warn(
                "iTerm2 is not installed, so the theme's terminal colors and font are not set.",
                "https://iterm2.com",
            )
        ]
    if not (paths.iterm_profiles / iterm.PROFILE_FILE).exists():
        return [warn("The iTerm2 profile is not installed.", "kit setup")]
    if iterm.default_guid() == iterm.PROFILE_GUID:
        return [ok("iTerm2 profile installed and set as the default")]
    if iterm.is_waiting_to_set_default(paths):
        return [ok("iTerm2 profile installed; it becomes the default when you quit iTerm2 (Cmd+Q)")]
    fix = f"kit apply {state.load(paths).theme} --iterm-default"
    return [ok("iTerm2 profile installed"), warn("It is not the default profile.", fix)]


CHECKS: list[Callable[[Paths], list[Finding]]] = [tools, active_theme, claude_settings, statusline, terminal]


def _safely(check: Callable[[Paths], list[Finding]], paths: Paths) -> list[Finding]:
    try:
        return check(paths)
    except KitError as error:
        return [fail(str(error), error.hint)]


def run(paths: Paths) -> list[Finding]:
    return [finding for check in CHECKS for finding in _safely(check, paths)]
