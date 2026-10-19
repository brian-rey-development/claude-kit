from __future__ import annotations

import argparse

from claude_kit import ui, widgets
from claude_kit.commands import Command
from claude_kit.paths import Paths


def run(_: argparse.Namespace, paths: Paths) -> int:
    in_use = {name for row in widgets.rows(paths) for name in row}
    for widget in widgets.available(paths):
        mark = ui.bold("●") if widget.name in in_use else " "
        print(f"{mark} {ui.bold(widget.name.ljust(12))} {ui.dim(widget.description)}")
    ui.note("● in your layout. Change it with `kit layout`.")
    return 0


COMMAND = Command("widgets", "List the status line widgets.", run)
