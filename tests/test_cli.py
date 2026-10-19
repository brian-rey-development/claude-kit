from __future__ import annotations

import pytest

from claude_kit.cli import main
from claude_kit.paths import Paths


def test_help_lists_the_commands(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--help"])
    assert exit_info.value.code == 0
    assert "setup" in capsys.readouterr().out


def test_an_unknown_theme_explains_what_exists(paths: Paths, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["apply", "nope"]) == 1
    output = capsys.readouterr().out
    assert "There is no theme called 'nope'" in output
    assert "moonlit" in output
