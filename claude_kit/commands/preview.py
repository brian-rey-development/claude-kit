from __future__ import annotations

import argparse
from pathlib import Path

from claude_kit import preview, theme, ui
from claude_kit.commands import Command
from claude_kit.paths import Paths


def configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("theme", help="theme id or path to a theme folder")
    parser.add_argument(
        "--here", action="store_true", help="draw it in this terminal instead of a new iTerm2 window"
    )


def run(args: argparse.Namespace, paths: Paths) -> int:
    chosen = theme.find(paths, args.theme)
    if args.here:
        preview.here(paths, chosen)
        return 0
    preview.live(paths, chosen, Path.cwd())
    ui.step(f"Opened {chosen.name} in a new iTerm2 window. Your own settings are unchanged.")
    return 0


COMMAND = Command(
    "preview", "See a theme in a new iTerm2 window, or in this terminal with --here.", run, configure
)
