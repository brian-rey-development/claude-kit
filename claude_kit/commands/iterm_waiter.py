from __future__ import annotations

import argparse

from claude_kit import iterm
from claude_kit.commands import Command
from claude_kit.paths import Paths


def configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("guid")


def run(args: argparse.Namespace, paths: Paths) -> int:
    iterm.await_quit_then_set_default(paths, None if args.guid == "none" else args.guid)
    return 0


COMMAND = Command(
    iterm.WAITER_COMMAND,
    "Wait for iTerm2 to quit, then set its default profile.",
    run,
    configure,
    hidden=True,
)
