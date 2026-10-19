from __future__ import annotations

from dataclasses import replace
from typing import Any

import pytest

from claude_kit import settings
from claude_kit.paths import Paths

MODS = ["/kit/mods/welcome"]
BEFORE: list[dict[str, Any]] = [
    {},
    {"model": "opus", "env": {"FOO": "1"}},
    {"statusLine": {"type": "command", "command": "mine.sh"}, "theme": "dark"},
    {"env": {settings.PLUGIN_DIRS: "/other/mod"}, "pluginConfigs": {"other": {"options": {}}}},
]


@pytest.mark.parametrize("before", BEFORE)
def test_uninstall_restores_the_settings_exactly(paths: Paths, before: dict[str, Any]) -> None:
    values = settings.kit_values(paths, "moonlit")
    installed = settings.apply(before, values, MODS)
    assert settings.restore(installed, values, settings.snapshot(before), MODS) == before


def test_apply_is_idempotent(paths: Paths) -> None:
    values = settings.kit_values(paths, "moonlit")
    once = settings.apply({"env": {settings.PLUGIN_DIRS: "/other"}}, values, MODS)
    assert settings.apply(once, values, MODS) == once
    assert settings.plugin_dirs(once) == ["/other", *MODS]


def test_uninstall_keeps_a_key_the_person_changed_since(paths: Paths) -> None:
    values = settings.kit_values(paths, "moonlit")
    installed = settings.apply({"theme": "dark"}, values, MODS)
    edited = {**installed, "theme": "light"}
    assert settings.restore(edited, values, settings.snapshot({"theme": "dark"}), MODS)["theme"] == "light"


def test_commands_survive_a_path_with_spaces(paths: Paths) -> None:
    spaced = replace(paths, kit=paths.home / "My Tools" / "claude-kit")
    command = settings.kit_values(spaced, "moonlit")[("statusLine",)]["command"]
    assert command == f"'{spaced.kit}/statusline/statusline.sh'"
