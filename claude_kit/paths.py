"""Every location the kit reads or writes, in one place, rooted at a home folder tests can replace."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Paths:
    home: Path
    user: Path
    claude: Path
    kit: Path = KIT_ROOT

    @classmethod
    def for_home(cls, home: Path) -> Paths:
        return cls(home=home, user=home / ".config" / "claude-kit", claude=home / ".claude")

    @classmethod
    def from_env(cls) -> Paths:
        """CLAUDE_KIT_HOME moves the kit's own files and CLAUDE_CONFIG_DIR follows Claude Code's setting."""
        defaults = cls.for_home(Path.home())
        return cls(
            home=defaults.home,
            user=Path(os.environ.get("CLAUDE_KIT_HOME", defaults.user)),
            claude=Path(os.environ.get("CLAUDE_CONFIG_DIR", defaults.claude)),
        )

    def display(self, path: Path) -> str:
        return f"~/{path.relative_to(self.home)}" if self.home in path.parents else str(path)

    @property
    def bundled_themes(self) -> Path:
        return self.kit / "themes"

    @property
    def user_themes(self) -> Path:
        return self.user / "themes"

    @property
    def current(self) -> Path:
        return self.user / "current"

    @property
    def config(self) -> Path:
        return self.user / "config.json"

    @property
    def state(self) -> Path:
        return self.user / "state.json"

    @property
    def backups(self) -> Path:
        return self.user / "backups"

    @property
    def preview_settings(self) -> Path:
        return self.user / "preview-settings.json"

    @property
    def iterm_waiter(self) -> Path:
        return self.user / "iterm-default.pid"

    @property
    def claude_settings(self) -> Path:
        return self.claude / "settings.json"

    @property
    def claude_themes(self) -> Path:
        return self.claude / "themes"

    @property
    def fonts(self) -> Path:
        return self.home / "Library" / "Fonts"

    @property
    def iterm_profiles(self) -> Path:
        return self.home / "Library" / "Application Support" / "iTerm2" / "DynamicProfiles"

    @property
    def local_bin(self) -> Path:
        return self.home / ".local" / "bin"

    @property
    def mods(self) -> Path:
        return self.kit / "mods"

    @property
    def cards(self) -> Path:
        return self.mods / "welcome" / "hooks" / "cards.ts"

    @property
    def statusline(self) -> Path:
        return self.kit / "statusline"

    @property
    def widgets(self) -> Path:
        return self.kit / "widgets"

    @property
    def schema(self) -> Path:
        return self.kit / "schema" / "theme.schema.json"
