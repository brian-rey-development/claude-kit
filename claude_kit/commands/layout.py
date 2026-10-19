from __future__ import annotations

import argparse

from claude_kit import ui, widgets
from claude_kit.commands import Command
from claude_kit.paths import Paths


def configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "rows", nargs="*", metavar="ROW", help='comma-separated widgets per row, such as "location,context"'
    )


def run(args: argparse.Namespace, paths: Paths) -> int:
    if args.rows:
        widgets.set_rows(
            paths, [[name.strip() for name in row.split(",") if name.strip()] for row in args.rows]
        )
        ui.step("Layout saved. The status line picks it up on its next refresh.")
    for number, row in enumerate(widgets.rows(paths), start=1):
        print(f"  {ui.dim(str(number))}  {'  '.join(row)}")
    return 0


COMMAND = Command("layout", "Show or set the status line layout.", run, configure)
