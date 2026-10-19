from __future__ import annotations

import argparse

from claude_kit import iterm, theme, ui
from claude_kit.commands import Command
from claude_kit.errors import KitError
from claude_kit.install import apply_steps, execute
from claude_kit.paths import Paths
from claude_kit.theme import Theme


def configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("theme", help="theme id or path to a theme folder")
    parser.add_argument(
        "--iterm-default", action="store_true", help="also make the theme's profile the iTerm2 default"
    )
    parser.add_argument("--dry-run", action="store_true", help="list the changes without making them")


def checked(paths: Paths, name: str) -> Theme:
    chosen = theme.find(paths, name)
    report = chosen.check(paths.schema)
    if report.errors:
        raise KitError(f"The theme {chosen.id} has problems:\n    " + "\n    ".join(report.errors))
    for warning in report.warnings:
        ui.warn(warning)
    return chosen


def run(args: argparse.Namespace, paths: Paths) -> int:
    chosen = checked(paths, args.theme)
    steps = apply_steps(paths, chosen, iterm_default=args.iterm_default)
    if args.dry_run:
        for step in steps:
            ui.item(step.title)
        return 0
    execute(steps)
    if args.iterm_default and iterm.is_waiting_to_set_default(paths):
        ui.note("iTerm2 is open, so the default profile changes when you next quit it (Cmd+Q).")
    ui.note("New Claude Code sessions use the theme. Run `kit doctor` to check everything.")
    return 0


COMMAND = Command("apply", "Apply a theme without questions, for scripts and agents.", run, configure)
