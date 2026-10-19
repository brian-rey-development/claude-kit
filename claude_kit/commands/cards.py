from __future__ import annotations

import argparse

from claude_kit import ui
from claude_kit.commands import Command
from claude_kit.install import write_cards
from claude_kit.paths import Paths


def run(_: argparse.Namespace, paths: Paths) -> int:
    write_cards(paths)
    ui.step("Wrote the welcome cards for every theme.")
    return 0


COMMAND = Command("cards", "Regenerate the welcome cards from every theme.", run, hidden=True)
