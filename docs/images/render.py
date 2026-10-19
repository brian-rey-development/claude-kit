"""Renders the README screenshots from real kit output, in a throwaway home so nothing on this Mac changes.

Usage: make screenshots

Run it on a clean checkout, because the setup screenshots show this repository's own git status.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pty_session
import sunflower
from terminal import screenshot

from claude_kit import sample, theme
from claude_kit.color import sgr
from claude_kit.paths import KIT_ROOT, Paths
from claude_kit.theme import Theme

IMAGES = Path(__file__).parent
COLUMNS = 100
SESSION_COLUMNS = 96
WIDTHS = (80, 66, 52, 38)
PROMPT = "> add a dark mode toggle to the settings page"
SETUP_ANSWERS = (
    ("first? [y/N]", "n"),
    ("Use Moonlit? [Y/n]", "y"),
    ("profile? [Y/n]", "n"),
    ("Apply them? [Y/n]", "n"),
)


def painted(text: str, foreground: str | None, background: str | None = None) -> str:
    code = sgr(foreground, background)
    return f"\x1b[{code}m{text}\x1b[0m" if code else text


def typed(command: str) -> str:
    return f"\x1b[2m$\x1b[0m {command}\n"


@dataclass(frozen=True)
class Studio:
    home: Path
    repo: Path
    out: Path

    @property
    def paths(self) -> Paths:
        return Paths.for_home(self.home)

    @property
    def moonlit(self) -> Theme:
        return theme.find(self.paths, "moonlit")

    def kit(self, args: Sequence[str], answers: Sequence[tuple[str, str]] = ()) -> str:
        argv = [str(KIT_ROOT / "bin" / "kit"), *args]
        return pty_session.run(argv, columns=COLUMNS, answers=answers, env=os.environ, cwd=self.repo)

    def status(self, chosen: Theme, columns: int) -> list[str]:
        return sample.statusline(self.paths, chosen, columns, self.repo).stdout.splitlines()


def session(studio: Studio) -> None:
    chosen = studio.moonlit
    rows = ["".join(painted(run["text"], run["fg"], run["bg"]) for run in row) for row in chosen.art_sizes[0]]
    rows[len(rows) // 2] += "   " + painted(chosen.tagline, chosen.palette["caption"])
    rule = painted("─" * SESSION_COLUMNS, chosen.palette["divider"])
    lines = ["", *rows, "", rule, PROMPT, rule, *studio.status(chosen, SESSION_COLUMNS)]
    out = studio.out / "moonlit.png"
    screenshot(chosen, "\n".join(lines), out, columns=SESSION_COLUMNS, title="claude")


def widths(studio: Studio) -> None:
    chosen = studio.moonlit
    lines: list[str] = []
    for columns in WIDTHS:
        label = painted(f"{columns} columns", chosen.palette["detail"])
        lines += [label, *studio.status(chosen, columns), ""]
    screenshot(chosen, "\n".join(lines), studio.out / "widths.png", columns=WIDTHS[0], title="status line")


def setup(studio: Studio) -> None:
    text = typed("kit setup") + studio.kit(["setup"], SETUP_ANSWERS)
    screenshot(studio.moonlit, text, studio.out / "setup.png", columns=COLUMNS, title="kit setup")


def new_theme(studio: Studio) -> None:
    card, icon = sunflower.draw_into(studio.home)
    shutil.copy2(card, studio.out / "sunflower.png")
    options = ["--light", "--emoji", "🌻", "--tagline", "Turn toward the light.", "--author", "claude-kit"]
    output = studio.kit(["new-theme", "sunflower", "--image", str(card), "--icon", str(icon), *options])
    text = typed("kit new-theme sunflower --image sunflower.png --light") + output
    created = theme.load(studio.paths.user_themes / "sunflower")
    screenshot(created, text, studio.out / "new-theme.png", columns=COLUMNS, title="kit new-theme")


def sample_repo(root: Path) -> Path:
    repo = root / "storefront"
    repo.mkdir()
    git = ["git", "-C", str(repo), "-c", "user.name=kit", "-c", "user.email=kit@example.com"]
    subprocess.run([*git, "init", "--quiet", "--initial-branch", "feat/dark-mode"], check=True)
    (repo / "settings.tsx").write_text("export const Settings = () => null\n")
    subprocess.run([*git, "add", "."], check=True)
    subprocess.run([*git, "commit", "--quiet", "--message", "Start the settings page"], check=True)
    (repo / "settings.tsx").write_text("export const Settings = () => <Toggle />\n")
    (repo / "toggle.tsx").write_text("export const Toggle = () => null\n")
    return repo


def main() -> None:
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch).resolve()
        os.environ["HOME"] = str(root)
        for override in ("CLAUDE_KIT_HOME", "CLAUDE_CONFIG_DIR"):
            os.environ.pop(override, None)
        studio = Studio(home=root, repo=sample_repo(root), out=root / "out")
        studio.out.mkdir()
        for scene in (setup, new_theme, session, widths):
            scene(studio)
        for image in studio.out.iterdir():
            shutil.copy2(image, IMAGES / image.name)


if __name__ == "__main__":
    main()
