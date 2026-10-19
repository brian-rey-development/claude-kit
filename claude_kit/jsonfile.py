"""JSON files the kit owns or edits, written atomically so a crash never leaves half a file."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, cast

from claude_kit.errors import KitError

JsonObject = dict[str, Any]


def read(path: Path, default: JsonObject | None = None) -> JsonObject:
    if not path.exists():
        if default is None:
            raise KitError(f"{path} does not exist.")
        return dict(default)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise KitError(
            f"{path} is not valid JSON: {error}", "Fix the file by hand, then run again."
        ) from error
    if not isinstance(data, dict):
        raise KitError(f"{path} must hold a JSON object.")
    return cast(JsonObject, data)


def write(path: Path, data: object) -> None:
    """Writes through a symlink to its target and keeps the file's permissions, as dotfile managers expect."""
    target = path.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f".{target.name}.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if target.exists():
        shutil.copymode(target, tmp)
    tmp.replace(target)
