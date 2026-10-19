from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Callable

from claude_kit.paths import Paths


def _no_arguments(_: argparse.ArgumentParser) -> None:
    pass


@dataclass(frozen=True)
class Command:
    name: str
    summary: str
    run: Callable[[argparse.Namespace, Paths], int]
    configure: Callable[[argparse.ArgumentParser], None] = _no_arguments
    hidden: bool = False
