"""The theme's iTerm2 profile, as a dynamic profile that inherits everything else from your default.

A running iTerm2 loads dynamic profiles at once, so nothing needs a restart. Only making the profile
the default does: iTerm2 writes its preferences back when it quits, so that change waits for the quit.
"""

from __future__ import annotations

import os
import plistlib
import re
import select
import signal
import subprocess
from pathlib import Path
from typing import NamedTuple

from claude_kit import color, jsonfile
from claude_kit.jsonfile import JsonObject
from claude_kit.paths import Paths
from claude_kit.theme import Theme

APP = Path("/Applications/iTerm.app")
DOMAIN = "com.googlecode.iterm2"
PROFILE_GUID = "C1A0DE00-0000-4000-8000-00000000C17A"
PREVIEW_GUID = "C1A0DE00-0000-4000-8000-0000000F1E57"
PROFILE_FILE = "claude-kit.json"
PREVIEW_FILE = "claude-kit-preview.json"
DEFAULT_FONT_SIZE = 14
WAITER_COMMAND = "_iterm-default"
COLOR_KEYS = {
    "background": "Background Color",
    "foreground": "Foreground Color",
    "bold": "Bold Color",
    "cursor": "Cursor Color",
    "cursor_text": "Cursor Text Color",
    "selection": "Selection Color",
    "selected_text": "Selected Text Color",
    "link": "Link Color",
    "tab": "Tab Color",
}


class BaseProfile(NamedTuple):
    guid: str | None
    font_size: int


def is_installed() -> bool:
    return APP.exists()


def is_running() -> bool:
    return subprocess.run(["pgrep", "-xq", "iTerm2"], check=False).returncode == 0


def _preferences() -> JsonObject:
    exported = subprocess.run(["defaults", "export", DOMAIN, "-"], capture_output=True, check=False)
    return plistlib.loads(exported.stdout) if exported.returncode == 0 else {}


def default_guid() -> str | None:
    guid = _preferences().get("Default Bookmark Guid")
    return str(guid) if guid else None


def base_profile(remembered_default: str | None) -> BaseProfile:
    """Today's default profile, or the one that was default before the kit's own took its place."""
    prefs = _preferences()
    guid = prefs.get("Default Bookmark Guid")
    if guid == PROFILE_GUID:
        guid = remembered_default
    profiles: list[JsonObject] = prefs.get("New Bookmarks", [])
    fonts = [str(profile.get("Normal Font", "")) for profile in profiles if profile.get("Guid") == guid]
    size = re.search(r"(\d+(?:\.\d+)?)$", fonts[0] if fonts else "")
    return BaseProfile(guid, round(float(size.group(1))) if size else DEFAULT_FONT_SIZE)


def _color(hex_color: str) -> JsonObject:
    r, g, b = (channel / 255 for channel in color.to_rgb(hex_color))
    return {
        "Color Space": "sRGB",
        "Red Component": r,
        "Green Component": g,
        "Blue Component": b,
        "Alpha Component": 1,
    }


def _colors(terminal: JsonObject) -> JsonObject:
    named = {key: terminal[role] for role, key in COLOR_KEYS.items()}
    ansi = {f"Ansi {i} Color": color for i, color in enumerate(terminal["ansi"])}
    return {
        key + mode: _color(value)
        for key, value in {**named, **ansi}.items()
        for mode in ("", " (Dark)", " (Light)")
    }


def profile(theme: Theme, guid: str, base: BaseProfile) -> JsonObject:
    font = f"{theme.font_postscript} {base.font_size}"
    return {
        "Name": theme.name if guid == PROFILE_GUID else f"{theme.name} (preview)",
        "Guid": guid,
        **({"Dynamic Profile Parent GUID": base.guid} if base.guid else {}),
        "Normal Font": font,
        "Non Ascii Font": font,
        "Use Non-ASCII Font": False,
        "Use Separate Colors for Light and Dark Mode": False,
        "Use Tab Color": True,
        "Use Bright Bold": True,
        "Minimum Contrast": 0,
        "Custom Directory": "Advanced",
        "AWDS Pane Option": "Recycle",
        "AWDS Tab Option": "Recycle",
        "AWDS Window Option": "No",
        **_colors(theme.terminal),
    }


def write_profile(paths: Paths, theme: Theme, base: BaseProfile, *, preview: bool = False) -> Path:
    guid, name = (PREVIEW_GUID, PREVIEW_FILE) if preview else (PROFILE_GUID, PROFILE_FILE)
    out = paths.iterm_profiles / name
    jsonfile.write(out, {"Profiles": [profile(theme, guid, base)]})
    return out


def change_default(paths: Paths, guid: str | None) -> None:
    """Sets the default profile now when iTerm2 is closed, or right after it next quits."""
    cancel_pending_default(paths)
    if not is_running():
        set_default(guid)
        return
    waiter = subprocess.Popen(
        [str(paths.kit / "bin" / "kit"), WAITER_COMMAND, guid or "none"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    paths.iterm_waiter.write_text(str(waiter.pid))


def _pending_waiter(paths: Paths) -> int | None:
    """The waiter's pid, once it is confirmed to be our waiter and not a process that reused the pid."""
    if not paths.iterm_waiter.exists():
        return None
    pid = paths.iterm_waiter.read_text().strip()
    command = subprocess.run(["ps", "-p", pid, "-o", "command="], capture_output=True, text=True, check=False)
    return int(pid) if WAITER_COMMAND in command.stdout else None


def is_waiting_to_set_default(paths: Paths) -> bool:
    return _pending_waiter(paths) is not None


def cancel_pending_default(paths: Paths) -> None:
    pid = _pending_waiter(paths)
    if pid is not None:
        os.kill(pid, signal.SIGTERM)
    paths.iterm_waiter.unlink(missing_ok=True)


def _wait_for_exit(pid: int) -> None:
    queue = select.kqueue()
    exit_event = select.kevent(pid, filter=select.KQ_FILTER_PROC, fflags=select.KQ_NOTE_EXIT)
    try:
        queue.control([exit_event], 1, None)
    except ProcessLookupError:
        return


def await_quit_then_set_default(paths: Paths, guid: str | None) -> None:
    running = subprocess.run(["pgrep", "-x", "iTerm2"], capture_output=True, text=True, check=False)
    for pid in running.stdout.split():
        _wait_for_exit(int(pid))
    set_default(guid)
    paths.iterm_waiter.unlink(missing_ok=True)


def set_default(guid: str | None) -> None:
    """Writes the default profile directly, which is only safe while iTerm2 is closed."""
    if guid is None:
        subprocess.run(
            ["defaults", "delete", DOMAIN, "Default Bookmark Guid"], check=False, capture_output=True
        )
    else:
        subprocess.run(["defaults", "write", DOMAIN, "Default Bookmark Guid", "-string", guid], check=True)
