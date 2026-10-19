from __future__ import annotations

import argparse
import getpass
import re
from pathlib import Path

from claude_kit import generate, theme, ui
from claude_kit.commands import Command
from claude_kit.errors import KitError
from claude_kit.install import write_cards
from claude_kit.paths import Paths
from claude_kit.preview import here

ID_PATTERN = re.compile(r"[a-z][a-z0-9-]{1,30}")


def configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("id", help="lowercase name for the theme folder, such as forest")
    parser.add_argument(
        "--image", type=Path, required=True, help="the picture for the welcome card and the colors"
    )
    parser.add_argument("--icon", type=Path, help="a simpler picture for the font glyph; defaults to --image")
    parser.add_argument("--name", help="display name; defaults to the id")
    parser.add_argument(
        "--tagline", default="One careful step at a time.", help="the line beside the card art"
    )
    parser.add_argument(
        "--emoji", default="⭐", help="the character the glyph replaces, shown where the font is missing"
    )
    parser.add_argument("--light", action="store_true", help="a light terminal background")
    parser.add_argument(
        "--author", default=getpass.getuser(), help="who made the art; defaults to your account name"
    )
    parser.add_argument(
        "--sampling",
        choices=("majority", "average"),
        default="majority",
        help="majority keeps flat drawings crisp; average suits photos and shading",
    )


def _request(args: argparse.Namespace) -> generate.Request:
    if not ID_PATTERN.fullmatch(args.id):
        raise KitError(
            f"{args.id!r} cannot be a theme id.",
            "Use lowercase letters, digits and dashes, starting with a letter.",
        )
    return generate.Request(
        theme_id=args.id,
        name=args.name or args.id.replace("-", " ").title(),
        tagline=args.tagline,
        emoji=args.emoji,
        author=args.author,
        appearance="light" if args.light else "dark",
        card=args.image,
        icon=args.icon or args.image,
        sampling=args.sampling,
    )


def run(args: argparse.Namespace, paths: Paths) -> int:
    request = _request(args)
    directory = paths.user_themes / request.theme_id
    if directory.exists():
        raise KitError(
            f"{paths.display(directory)} already exists.", "Pick another id, or delete that folder first."
        )
    generate.create(request, directory, paths.schema)
    created = theme.load(directory)
    write_cards(paths)
    here(paths, created)
    ui.step(f"Created {created.name} in {paths.display(directory)}")
    ui.note(f"Edit theme.json to taste, then run `kit check {created.id}` and `kit preview {created.id}`.")
    return 0


COMMAND = Command("new-theme", "Make a theme from an image.", run, configure)
