from __future__ import annotations

import re

from claude_kit import widgets
from claude_kit.paths import Paths


def test_every_widget_file_is_registered(paths: Paths) -> None:
    registry = (paths.widgets / widgets.REGISTRY).read_text()
    registered = re.findall(r'^import "(\w+)" as \1;$', registry, re.MULTILINE)
    assert sorted(registered) == sorted(widget.name for widget in widgets.available(paths))


def test_every_widget_describes_itself(paths: Paths) -> None:
    assert all(widget.description for widget in widgets.available(paths))


def test_the_default_layout_uses_known_widgets(paths: Paths) -> None:
    names = {widget.name for widget in widgets.available(paths)}
    assert {name for row in widgets.rows(paths) for name in row} <= names
