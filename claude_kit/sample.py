"""A realistic Claude Code session, for previews and for checking that the status line renders."""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

from claude_kit.jsonfile import JsonObject
from claude_kit.paths import Paths
from claude_kit.theme import Theme

HOUR = 3600


def session(directory: Path) -> JsonObject:
    now = time.time()
    return {
        "session_id": "preview",
        "cwd": str(directory),
        "workspace": {"current_dir": str(directory), "project_dir": str(directory)},
        "model": {"id": "claude-opus-5-5", "display_name": "Opus 5.5"},
        "effort": {"level": "high"},
        "context_window": {"used_percentage": 38, "total_input_tokens": 76000, "context_window_size": 200000},
        "rate_limits": {
            "five_hour": {"used_percentage": 61, "resets_at": now + HOUR},
            "seven_day": {"used_percentage": 23, "resets_at": now + 90 * HOUR},
        },
    }


def statusline(paths: Paths, theme: Theme, columns: int, directory: Path) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "CLAUDE_KIT_THEME_DIR": str(theme.directory), "COLUMNS": str(columns)}
    return subprocess.run(
        [str(paths.statusline / "statusline.sh")],
        input=json.dumps(session(directory)),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
