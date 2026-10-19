from __future__ import annotations

import argparse

from claude_kit import theme, ui
from claude_kit.commands import Command
from claude_kit.paths import Paths
from claude_kit.preview import swatches


def run(_: argparse.Namespace, paths: Paths) -> int:
    active = theme.current(paths)
    for found in theme.discover(paths):
        mark = ui.bold("●") if active and active.id == found.id else " "
        origin = "yours" if paths.user_themes.resolve() in found.directory.parents else "bundled"
        print(f"{mark} {ui.bold(found.name.ljust(14))} {swatches(found)}  {ui.dim(origin)}")
        print(f"  {ui.dim(found.description)}")
    return 0


COMMAND = Command("themes", "List the themes and their colors.", run)
