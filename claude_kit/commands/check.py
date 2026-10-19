from __future__ import annotations

import argparse
from pathlib import Path

from claude_kit import theme, ui
from claude_kit.commands import Command
from claude_kit.errors import KitError
from claude_kit.paths import Paths


def configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("themes", nargs="*", help="theme ids or folders; every theme folder when left out")


def problems(paths: Paths, directory: Path) -> tuple[list[str], list[str]]:
    try:
        report = theme.load(directory).check(paths.schema)
    except KitError as error:
        return [str(error)], []
    return report.errors, report.warnings


def report(paths: Paths, directory: Path) -> bool:
    errors, warnings = problems(paths, directory)
    label = paths.display(directory)
    if errors:
        ui.fail(label)
    elif warnings:
        ui.warn(label)
    else:
        ui.step(label)
    for problem in errors + warnings:
        ui.note(problem)
    return not errors


def run(args: argparse.Namespace, paths: Paths) -> int:
    directories = [theme.find(paths, name).directory for name in args.themes] or theme.folders(paths)
    results = [report(paths, directory) for directory in directories]
    return 0 if all(results) else 1


COMMAND = Command("check", "Validate themes against the schema and the contrast rules.", run, configure)
