from __future__ import annotations

import argparse
from pathlib import Path

from claude_kit import art, jsonfile, theme, ui
from claude_kit.commands import Command
from claude_kit.install import write_cards
from claude_kit.paths import Paths


def configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("theme", help="theme id or path to a theme folder")
    parser.add_argument(
        "image", type=Path, help="the picture for the welcome card, ideally with a transparent background"
    )
    parser.add_argument(
        "--sampling",
        choices=("majority", "average"),
        default="majority",
        help="majority keeps flat drawings crisp; average suits photos and shading",
    )
    parser.add_argument("--colors", type=int, default=art.CARD_COLORS, help="how many colors the art may use")


def run(args: argparse.Namespace, paths: Paths) -> int:
    chosen = theme.find(paths, args.theme)
    sizes = art.card_sizes(art.open_image(args.image), sampling=args.sampling, colors=args.colors)
    jsonfile.write(chosen.directory / "art.json", sizes)
    write_cards(paths)
    for row in sizes[1]:
        print(f"  {ui.runs(row)}")
    ui.step(f"Wrote {len(sizes)} card sizes to {paths.display(chosen.directory / 'art.json')}")
    return 0


COMMAND = Command("art", "Turn an image into a theme's welcome card art.", run, configure)
