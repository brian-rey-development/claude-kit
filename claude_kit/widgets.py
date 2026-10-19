"""The status line widgets, one jq file each in widgets/, each described by its first comment line."""

from __future__ import annotations

from dataclasses import dataclass

from claude_kit import jsonfile
from claude_kit.errors import KitError
from claude_kit.jsonfile import JsonObject
from claude_kit.paths import Paths

REGISTRY = "registry.jq"
MAX_PER_ROW = 3


@dataclass(frozen=True)
class Widget:
    name: str
    description: str


def available(paths: Paths) -> list[Widget]:
    found: list[Widget] = []
    for file in sorted(paths.widgets.glob("*.jq")):
        if file.name != REGISTRY:
            first = file.read_text(encoding="utf-8").splitlines()[0]
            found.append(Widget(file.stem, first.lstrip("# ").strip()))
    return found


def config(paths: Paths) -> JsonObject:
    defaults = jsonfile.read(paths.statusline / "defaults.json")
    return {**defaults, **jsonfile.read(paths.config, {})}


def rows(paths: Paths) -> list[list[str]]:
    return [list(row) for row in config(paths)["statusline"]["rows"]]


def set_rows(paths: Paths, new_rows: list[list[str]]) -> None:
    names = {widget.name for widget in available(paths)}
    unknown = sorted({name for row in new_rows for name in row} - names)
    if unknown:
        raise KitError(f"Unknown widgets: {', '.join(unknown)}.", f"Widgets: {', '.join(sorted(names))}.")
    if any(len(row) > MAX_PER_ROW or not row for row in new_rows):
        raise KitError(f"Each row holds one to {MAX_PER_ROW} widgets.")
    jsonfile.write(paths.config, {**config(paths), "statusline": {"rows": new_rows}})
