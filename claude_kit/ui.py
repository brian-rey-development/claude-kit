"""Terminal output for the CLI.

Color follows the NO_COLOR convention and turns off when stdout is not a terminal, so logs and agents
read plain text.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Sequence

from claude_kit import color
from claude_kit.art import Run

COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _sgr(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if COLOR and code else text


def bold(text: str) -> str:
    return _sgr("1", text)


def dim(text: str) -> str:
    return _sgr("2", text)


def rgb(hex_color: str, text: str) -> str:
    return _sgr(color.sgr(hex_color), text)


def swatch(hex_color: str) -> str:
    return rgb(hex_color, "██") if COLOR else ""


def runs(row: Sequence[Run]) -> str:
    return "".join(_sgr(color.sgr(run["fg"], run["bg"]), run["text"]) for run in row)


def heading(text: str) -> None:
    print(f"\n{bold(text)}")


def step(text: str) -> None:
    print(f"  {_sgr('32', '✓')} {text}")


def warn(text: str) -> None:
    print(f"  {_sgr('33', '!')} {text}")


def fail(text: str) -> None:
    print(f"  {_sgr('31', '✗')} {text}")


def item(text: str) -> None:
    print(f"  {dim('•')} {text}")


def note(text: str) -> None:
    print(f"    {dim(text)}")


def interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def confirm(question: str, *, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    while True:
        answer = input(f"\n{bold('?')} {question} {dim(f'[{hint}]')} ").strip().lower()
        if not answer:
            return default
        if answer in ("y", "yes", "n", "no"):
            return answer.startswith("y")
        print(dim("  Type y or n."))


def choose(question: str, options: Sequence[str]) -> int:
    print(f"\n{bold('?')} {question}")
    for number, option in enumerate(options, start=1):
        print(f"  {bold(str(number))}  {option}")
    while True:
        answer = input(f"{dim(f'Choose 1-{len(options)}:')} ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return int(answer) - 1
        print(dim(f"  Type a number from 1 to {len(options)}."))
