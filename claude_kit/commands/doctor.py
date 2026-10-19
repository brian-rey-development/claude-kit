from __future__ import annotations

import argparse

from claude_kit import doctor, ui
from claude_kit.commands import Command
from claude_kit.paths import Paths

SYMBOLS = {"ok": ui.step, "warn": ui.warn, "fail": ui.fail}


def run(_: argparse.Namespace, paths: Paths) -> int:
    findings = doctor.run(paths)
    for finding in findings:
        SYMBOLS[finding.level](finding.message)
        if finding.fix:
            ui.note(f"Fix: {finding.fix}")
    return 1 if any(finding.level == "fail" for finding in findings) else 0


COMMAND = Command("doctor", "Check that the setup is in place and working.", run)
