"""What the kit has changed on this Mac, so `kit uninstall` can undo exactly that and nothing else."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from claude_kit import jsonfile
from claude_kit.paths import Paths

VERSION = 1


@dataclass
class State:
    theme: str = ""
    mods: list[str] = field(default_factory=list[str])
    settings_before: dict[str, Any | None] = field(default_factory=dict[str, Any])
    fonts: list[str] = field(default_factory=list[str])
    claude_themes: list[str] = field(default_factory=list[str])
    iterm_default_before: str | None = None
    kit_link: str | None = None

    @property
    def has_settings_snapshot(self) -> bool:
        return bool(self.settings_before)

    @property
    def has_changes(self) -> bool:
        return bool(self.theme or self.fonts or self.claude_themes or self.kit_link)


def load(paths: Paths) -> State:
    data = jsonfile.read(paths.state, {})
    data.pop("version", None)
    known = State.__dataclass_fields__
    return State(**{key: value for key, value in data.items() if key in known})


def save(paths: Paths, state: State) -> None:
    jsonfile.write(paths.state, {"version": VERSION, **asdict(state)})


def remember(items: list[str], item: str) -> None:
    if item not in items:
        items.append(item)
