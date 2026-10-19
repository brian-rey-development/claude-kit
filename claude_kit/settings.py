"""The Claude Code settings the kit owns, as pure functions over the settings object.

The kit owns a few keys outright and shares CLAUDE_CODE_PLUGIN_DIRS, where it adds its mods beside any
folders already listed. What an owned key held before the first install is kept, so uninstall puts it back.
"""

from __future__ import annotations

import copy
import shlex
from typing import Any, cast

from claude_kit.jsonfile import JsonObject
from claude_kit.paths import Paths

PLUGIN_DIRS = "CLAUDE_CODE_PLUGIN_DIRS"
STATUS_REFRESH_SECONDS = 15
Key = tuple[str, ...]
OWNED_KEYS: tuple[Key, ...] = (
    ("statusLine",),
    ("subagentStatusLine",),
    ("theme",),
    ("pluginConfigs", "welcome"),
)


def kit_values(paths: Paths, theme_id: str, theme_dir: str | None = None) -> dict[Key, Any]:
    prefix = f"CLAUDE_KIT_THEME_DIR={shlex.quote(theme_dir)} " if theme_dir else ""
    return {
        ("statusLine",): {
            "type": "command",
            "command": prefix + shlex.quote(str(paths.statusline / "statusline.sh")),
            "refreshInterval": STATUS_REFRESH_SECONDS,
        },
        ("subagentStatusLine",): {
            "type": "command",
            "command": prefix + shlex.quote(str(paths.statusline / "subagents.sh")),
        },
        ("theme",): f"custom:{theme_id}",
        ("pluginConfigs", "welcome"): {"options": {"theme": theme_id}},
    }


def get(settings: JsonObject, key: Key) -> Any:
    head, *rest = key
    value = settings.get(head)
    if not rest:
        return value
    return get(cast(JsonObject, value), tuple(rest)) if isinstance(value, dict) else None


def _set(settings: JsonObject, key: Key, value: Any | None) -> None:
    *parents, last = key
    node = settings
    for part in parents:
        node = node.setdefault(part, {})
    if value is not None:
        node[last] = value
        return
    node.pop(last, None)
    if parents and not node:
        _set(settings, tuple(parents), None)


def snapshot(settings: JsonObject) -> dict[str, Any | None]:
    return {".".join(key): get(settings, key) for key in OWNED_KEYS}


def plugin_dirs(settings: JsonObject) -> list[str]:
    return [entry for entry in str(get(settings, ("env", PLUGIN_DIRS)) or "").split(":") if entry]


def apply(settings: JsonObject, values: dict[Key, Any], mods: list[str]) -> JsonObject:
    result = copy.deepcopy(settings)
    for key, value in values.items():
        _set(result, key, value)
    current = plugin_dirs(result)
    _set(result, ("env", PLUGIN_DIRS), ":".join(current + [mod for mod in mods if mod not in current]))
    return result


def restore(
    settings: JsonObject, values: dict[Key, Any], before: dict[str, Any | None], mods: list[str]
) -> JsonObject:
    """Puts back what each owned key held before, unless the person has changed it since."""
    result = copy.deepcopy(settings)
    for key in OWNED_KEYS:
        if get(result, key) == values[key]:
            _set(result, key, before.get(".".join(key)))
    remaining = [entry for entry in plugin_dirs(result) if entry not in mods]
    _set(result, ("env", PLUGIN_DIRS), ":".join(remaining) or None)
    return result


def preview(paths: Paths, theme_id: str, theme_dir: str, mods: list[str]) -> JsonObject:
    """Settings for one `claude --settings` session, which win over the person's own for that session only."""
    return apply({}, kit_values(paths, theme_id, theme_dir), mods)
