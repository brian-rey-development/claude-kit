from __future__ import annotations

import argparse

from claude_kit import state, ui
from claude_kit.commands import Command
from claude_kit.errors import KitError
from claude_kit.install import execute, uninstall_steps
from claude_kit.paths import Paths


def configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--yes", action="store_true", help="skip the question")


def run(args: argparse.Namespace, paths: Paths) -> int:
    if not state.load(paths).has_changes:
        ui.step("Nothing to undo, since claude-kit has not changed anything on this Mac.")
        return 0
    steps = uninstall_steps(paths)
    ui.heading("This puts your Mac back as it was before claude-kit")
    for step in steps:
        ui.item(step.title)
    if not args.yes:
        if not ui.interactive():
            raise KitError("Uninstall needs confirmation.", "Run `kit uninstall --yes`.")
        if not ui.confirm("Go ahead?"):
            return 0
    execute(steps)
    ui.note(f"Your own themes in {paths.display(paths.user_themes)} and the settings backups are kept.")
    return 0


COMMAND = Command("uninstall", "Undo every change and restore what was there before.", run, configure)
