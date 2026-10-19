# AGENTS.md

This file is for AI coding agents working in this repository or setting it up for someone. Humans should start with [README.md](README.md).

claude-kit themes Claude Code on macOS. A theme is a folder of data (palette, terminal colors, card art, mascot glyph), and the kit turns it into a status line, a welcome card above the prompt, a Claude Code color theme, a patched copy of Monaco and an iTerm2 profile. Everything it changes is recorded, so `kit uninstall` restores the previous state.

## Set it up for someone

Never run `kit setup` for a person; it is interactive. Use the non-interactive commands and show them the result.

```bash
./install.sh --help                  # checks macOS, jq and Claude Code, then shows every command
bin/kit themes                       # the themes that exist
bin/kit preview <theme> --here       # draw a theme in the current terminal, changes nothing
bin/kit apply <theme> --dry-run      # list every change apply would make
bin/kit apply <theme>                # apply it; add --iterm-default to make the profile the default
bin/kit doctor                       # verify; exits 1 when something is broken, with a fix per line
bin/kit uninstall --yes              # undo everything
```

Before `apply`, tell the person what `--dry-run` printed. It edits `~/.claude/settings.json` (a backup goes to `~/.config/claude-kit/backups/`) and installs a font into `~/Library/Fonts`. New Claude Code sessions pick up the theme, and the running one does not.

To make a theme from a picture they give you, follow [.claude/skills/new-theme/SKILL.md](.claude/skills/new-theme/SKILL.md).

## Repository map

| Path | What it holds |
| --- | --- |
| `install.sh` | Checks prerequisites, then runs `bin/kit setup` (or passes its arguments to `bin/kit`) |
| `bin/kit` | Makes `.venv` from `requirements.txt` on first use, then runs `python -m claude_kit` |
| `claude_kit/` | The CLI. `commands/` has one module per command; `install.py` holds the apply and uninstall steps |
| `statusline/` | `statusline.sh` (entry point and caches), `render.jq`, `grid.jq` (layout engine), `palette.jq`, `meters.jq`, `subagents.jq` |
| `widgets/` | One jq file per status line widget, plus `registry.jq` |
| `mods/` | Claude Code mods (mini apps). Every folder with `.claude-plugin/plugin.json` is loaded |
| `themes/` | Bundled themes. Personal themes live in `~/.config/claude-kit/themes/` and win on an id clash |
| `schema/theme.schema.json` | The contract every `theme.json` is validated against |
| `docs/` | Tutorials, how-to guides, reference and explanation |
| `tests/` | pytest suite; `mods/*/tests/` hold the mod tests |

## Verify a change

```bash
make check     # ruff, pyright strict, pytest, shellcheck, claude plugin validate and test
make format    # fix formatting and the lint rules that can be fixed automatically
```

`make check` must pass before you say a change is done. It needs `uv`, `shellcheck`, `jq` and `claude` on the PATH.

## Rules

- Python must run on 3.9, the version macOS ships. Use `from __future__ import annotations`; never `match`, and never `X | Y` outside annotations.
- Tests use the `paths` fixture in `tests/conftest.py`, which points HOME at a temporary folder and hides iTerm2. Never write a test that touches the real `~/.claude`, `~/Library` or iTerm2 preferences.
- Never commit a `.ttf`. The font is built on each Mac from Apple's Monaco, which may not be redistributed.
- Never commit art you do not have the rights to. Bundled themes use original art under CC0; personal themes stay in `~/.config/claude-kit/themes/`.
- Text roles in a palette need 4.5:1 contrast against `terminal.background`, and the icon 3:1. `kit check` enforces it, and the bundled themes must pass with no warnings.
- In jq, a parameter named `$x` also defines a filter `x` inside the function body. Never name a parameter after a palette role or another function you call there.
- Keep functions short and names plain. Write a comment only for a reason the code cannot show.
- Every bug fix comes with a test that fails without the fix.

## Common tasks

| Task | Where to start |
| --- | --- |
| Add a status line widget | [docs/how-to/add-a-widget.md](docs/how-to/add-a-widget.md), [.claude/skills/new-widget/SKILL.md](.claude/skills/new-widget/SKILL.md) |
| Add a mini app | [docs/how-to/write-a-mod.md](docs/how-to/write-a-mod.md), [.claude/skills/new-mod/SKILL.md](.claude/skills/new-mod/SKILL.md) |
| Add or change a theme | [docs/reference/theme-format.md](docs/reference/theme-format.md), [docs/how-to/tune-a-palette.md](docs/how-to/tune-a-palette.md) |
| Change what apply writes | `claude_kit/install.py`, then update [docs/reference/files.md](docs/reference/files.md) |
| Add a command | A module in `claude_kit/commands/` exporting `COMMAND`, listed in `claude_kit/cli.py` and [docs/reference/cli.md](docs/reference/cli.md) |
