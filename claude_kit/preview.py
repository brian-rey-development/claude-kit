"""Two ways to see a theme before applying it, drawn in this terminal or live in a new iTerm2 window."""

from __future__ import annotations

import shlex
import shutil
import subprocess
import time
from pathlib import Path

from claude_kit import art, iterm, jsonfile, sample, settings, state, ui
from claude_kit.errors import KitError
from claude_kit.install import ensure_font, mod_dirs, write_cards
from claude_kit.paths import Paths
from claude_kit.theme import Theme

GAP = "   "
# The welcome mod keeps the same room for its tagline, so both pick the same art size.
MIN_TEXT_COLUMNS = 20
PROFILE_ATTEMPTS, PROFILE_RETRY_SECONDS = 20, 0.25
OPEN_WINDOW = """
on run argv
  tell application "iTerm"
    set previewWindow to (create window with profile (item 1 of argv))
    tell current session of previewWindow to write text (item 2 of argv)
  end tell
end run
"""


def card_lines(theme: Theme, columns: int) -> list[str]:
    tagline = ui.rgb(theme.palette["caption"], theme.tagline)
    fitting = [size for size in theme.art_sizes if art.width(size) + len(GAP) + MIN_TEXT_COLUMNS <= columns]
    if not fitting:
        return [tagline]
    rows = [ui.runs(row) for row in fitting[0]]
    middle = len(rows) // 2
    return [row + (GAP + tagline if index == middle else "") for index, row in enumerate(rows)]


def swatches(theme: Theme) -> str:
    return "".join(ui.swatch(color) for color in theme.palette.values())


def here(paths: Paths, theme: Theme) -> None:
    columns = shutil.get_terminal_size().columns - 2
    status = sample.statusline(paths, theme, columns, paths.kit).stdout.splitlines()
    lines = [
        "",
        *card_lines(theme, columns),
        "",
        *status,
        "",
        f"{swatches(theme)}  {ui.dim(theme.description)}",
    ]
    for line in lines:
        print(f"  {line}" if line else "")


def _session_command(paths: Paths, start_dir: Path) -> str:
    return " ".join(
        [
            f"cd {shlex.quote(str(start_dir))} &&",
            f"CLAUDE_CODE_PLUGIN_DIRS={shlex.quote(':'.join(mod_dirs(paths)))}",
            f"claude --settings {shlex.quote(str(paths.preview_settings))}",
        ]
    )


def _open_window(profile_name: str, command: str) -> None:
    """iTerm2 loads a new dynamic profile within about a second, so the first attempts may not find it."""
    error = ""
    for _ in range(PROFILE_ATTEMPTS):
        arguments = ["osascript", "-", profile_name, command]
        opened = subprocess.run(arguments, input=OPEN_WINDOW, text=True, capture_output=True, check=False)
        if opened.returncode == 0:
            return
        error = opened.stderr.strip()
        time.sleep(PROFILE_RETRY_SECONDS)
    raise KitError("iTerm2 did not open the preview window.", error)


def live(paths: Paths, theme: Theme, start_dir: Path) -> None:
    if not iterm.is_installed():
        raise KitError(
            "The live preview needs iTerm2.", "Run `kit preview --here` to see the theme in this terminal."
        )
    record = state.load(paths)
    ensure_font(paths, theme, record)
    write_cards(paths)
    iterm.write_profile(paths, theme, iterm.base_profile(record.iterm_default_before), preview=True)
    preview_settings = settings.preview(paths, theme.id, str(theme.directory), mod_dirs(paths))
    jsonfile.write(paths.preview_settings, preview_settings)
    _open_window(f"{theme.name} (preview)", _session_command(paths, start_dir))
