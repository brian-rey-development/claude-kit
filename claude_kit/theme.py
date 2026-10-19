from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

from claude_kit import contrast, jsonfile
from claude_kit.art import Art
from claude_kit.errors import KitError
from claude_kit.jsonfile import JsonObject
from claude_kit.paths import Paths

REQUIRED_FILES = ("theme.json", "claude.json", "art.json", "glyph/icon.png")


@dataclass(frozen=True)
class Theme:
    directory: Path
    data: JsonObject

    @property
    def id(self) -> str:
        return str(self.data["id"])

    @property
    def name(self) -> str:
        return str(self.data["name"])

    @property
    def description(self) -> str:
        return str(self.data["description"])

    @property
    def tagline(self) -> str:
        return str(self.data["tagline"])

    @property
    def palette(self) -> dict[str, str]:
        return dict(self.data["palette"])

    @property
    def terminal(self) -> JsonObject:
        return dict(self.data["terminal"])

    @property
    def icon(self) -> str:
        return str(self.data["icon"]["char"])

    @property
    def icon_cells(self) -> int:
        return int(self.data["icon"]["cells"])

    @property
    def font_family(self) -> str:
        return f"Monaco {self.name}"

    @property
    def font_postscript(self) -> str:
        return "Monaco" + "".join(part.capitalize() for part in self.id.split("-"))

    @property
    def has_art(self) -> bool:
        return (self.directory / "art.json").exists()

    @property
    def art_sizes(self) -> list[Art]:
        """The welcome card art, largest first."""
        return json.loads((self.directory / "art.json").read_text(encoding="utf-8"))

    def check(self, schema: Path) -> Report:
        missing = [f"missing file {name}" for name in REQUIRED_FILES if not (self.directory / name).exists()]
        validator = Draft202012Validator(json.loads(schema.read_text(encoding="utf-8")))
        errors: Iterable[ValidationError] = validator.iter_errors(self.data)
        invalid = [f"theme.json {_location(error)}: {error.message}" for error in errors]
        if missing or invalid:
            return Report(errors=missing + invalid, warnings=[])
        unreadable = contrast.shortfalls(self.palette, self.terminal["background"])
        return Report(errors=[], warnings=[str(shortfall) for shortfall in unreadable])


@dataclass(frozen=True)
class Report:
    """Errors keep a theme from working; warnings are colors that fall short of WCAG contrast."""

    errors: list[str]
    warnings: list[str]


def _location(error: ValidationError) -> str:
    return ".".join(map(str, error.absolute_path)) or "(root)"


def load(directory: Path) -> Theme:
    file = directory / "theme.json"
    if not file.exists():
        raise KitError(
            f"No theme at {directory}.", "A theme folder holds a theme.json. Run `kit themes` to list them."
        )
    return Theme(directory.resolve(), jsonfile.read(file))


def folders(paths: Paths) -> list[Path]:
    """Theme folders, bundled first; hidden ones are themes still being built."""
    roots = (paths.bundled_themes, paths.user_themes)
    return [
        file.parent
        for root in roots
        for file in sorted(root.glob("*/theme.json"))
        if not file.parent.name.startswith(".")
    ]


def _readable(directory: Path) -> Theme | None:
    try:
        found = load(directory)
    except KitError:
        return None
    return (
        found if isinstance(found.data.get("id"), str) and isinstance(found.data.get("name"), str) else None
    )


def discover(paths: Paths) -> list[Theme]:
    """Every theme that loads, where the person's own replace a bundled theme with the same id.

    A broken theme is left out instead of stopping every command; `kit check` reports it.
    """
    found = {theme.id: theme for theme in map(_readable, folders(paths)) if theme is not None}
    return sorted(found.values(), key=lambda theme: theme.name.lower())


def _looks_like_path(name: str) -> bool:
    return "/" in name or name.startswith(("~", "."))


def find(paths: Paths, name: str) -> Theme:
    """A theme by id, or by the path to its folder."""
    if _looks_like_path(name):
        return load(Path(name).expanduser())
    themes = discover(paths)
    match = next((theme for theme in themes if theme.id == name), None)
    if match is None:
        known = ", ".join(theme.id for theme in themes)
        raise KitError(
            f"There is no theme called {name!r}.",
            f"Known themes: {known}. A path to a theme folder works too.",
        )
    return match


def current(paths: Paths) -> Theme | None:
    return load(paths.current.resolve()) if paths.current.exists() else None
