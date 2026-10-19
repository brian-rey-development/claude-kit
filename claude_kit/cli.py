from __future__ import annotations

import argparse
import subprocess

from claude_kit import ui
from claude_kit.commands import (
    apply,
    art,
    cards,
    check,
    doctor,
    iterm_waiter,
    layout,
    new_theme,
    preview,
    setup,
    themes,
    uninstall,
    widgets,
)
from claude_kit.errors import KitError
from claude_kit.paths import Paths

COMMANDS = tuple(
    module.COMMAND
    for module in (
        setup,
        themes,
        preview,
        apply,
        doctor,
        uninstall,
        new_theme,
        check,
        art,
        widgets,
        layout,
        cards,
        iterm_waiter,
    )
)
ISSUES = "https://github.com/brian-rey-development/claude-kit/issues"
EPILOG = "New here? Run `kit setup`, which shows each change and asks before making it."


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="kit", description="Themes, status line widgets and mini apps for Claude Code.", epilog=EPILOG
    )
    commands = root.add_subparsers(title="commands", metavar="<command>")
    for command in COMMANDS:
        listed = {} if command.hidden else {"help": command.summary}
        sub = commands.add_parser(command.name, description=command.summary, **listed)
        command.configure(sub)
        sub.set_defaults(handler=command.run)
    return root


def _fail(message: str, hint: str) -> int:
    ui.fail(message)
    if hint:
        ui.note(hint)
    return 1


def main(argv: list[str] | None = None) -> int:
    root = parser()
    args = root.parse_args(argv)
    if not hasattr(args, "handler"):
        root.print_help()
        return 0
    try:
        return int(args.handler(args, Paths.from_env()))
    except KitError as error:
        return _fail(str(error), error.hint)
    except (KeyboardInterrupt, EOFError):
        print()
        ui.note("Stopped. Steps already shown with a check mark are done, and `kit uninstall` undoes them.")
        return 130
    except (OSError, subprocess.SubprocessError) as error:
        return _fail(
            f"{type(error).__name__}, {error}",
            f"Run `kit doctor`. If it persists, open an issue at {ISSUES}.",
        )
