# Theme format

A theme is a folder. The kit finds bundled themes in `themes/` and your own in `~/.config/claude-kit/themes/`. When both hold the same id, yours wins.

| File | Required | What it holds |
| --- | --- | --- |
| `theme.json` | yes | Everything below, validated against [`schema/theme.schema.json`](../../schema/theme.schema.json) |
| `claude.json` | yes | A Claude Code theme, linked into `~/.claude/themes/<id>.json` and selected as `custom:<id>` |
| `art.json` | yes | The welcome card art, three sizes from largest to smallest, made by `kit art` |
| `glyph/icon.png` | yes | The mascot for the font glyph, with a transparent background |
| `glyph/icon-small.png` | no | A simpler mascot for sizes below 64 pixels per em |
| `source/` | no | The pictures and scripts the art was made from |

Editors that read JSON Schema, and agents, can validate `theme.json` as you type when it starts with `"$schema": "../../schema/theme.schema.json"`.

## Fields

| Field | Meaning |
| --- | --- |
| `id` | Folder name and Claude Code theme id. Lowercase letters, digits and dashes, starting with a letter. |
| `name` | Display name. The font family becomes `Monaco <name>` and the iTerm2 profile takes this name. |
| `description` | One sentence for the theme picker. |
| `author`, `license` | Who made the art, and its SPDX license, such as `CC0-1.0`. Use `personal` for art you may not share. |
| `appearance` | `dark` or `light`, the base of the Claude Code theme. |
| `icon.char` | The character the patched font draws as the mascot. Pick an emoji close to the mascot, because fonts without the patch show the character itself. |
| `icon.cells` | Terminal cells the glyph spans. Use 2 for an emoji, which terminals draw double width, and 1 for a narrow character. |
| `tagline` | The line beside the welcome card art. |
| `palette` | Status line colors by role, below. |
| `terminal` | Terminal colors for the iTerm2 profile, which are `background`, `foreground`, `bold`, `cursor`, `cursor_text`, `selection`, `selected_text`, `link`, `tab` and the 16 `ansi` colors. |

Colors are `#RRGGBB`.

## Palette roles

| Role | Used for | Minimum contrast |
| --- | --- | --- |
| `brand` | Repository name | 4.5:1 |
| `accent` | Branch name, approved PR, running agents | 4.5:1 |
| `accent_soft` | Commits ahead, staged files, agent types | 4.5:1 |
| `ok` | Meters below the warning level | 4.5:1 |
| `warn` | Meters past the warning level, changed files, pending PR | 4.5:1 |
| `danger` | Meters past the critical level, conflicts, failed agents, a limit about to run out | 4.5:1 |
| `merged` | Merged PR | 4.5:1 |
| `bright` | Model name and cost | 4.5:1 |
| `caption` | Labels and the welcome card tagline | 4.5:1 |
| `detail` | Token counts, reset times and other secondary text | 4.5:1 |
| `icon` | The mascot where the terminal draws glyph outlines in one color, as iTerm2 does | 3:1 |
| `divider` | The rule between columns | none, decorative |
| `track` | The empty part of a meter bar | none, decorative |

Contrast is measured against `terminal.background` with the WCAG 2.2 formula. `kit check` reports each shortfall, and `kit apply` warns about them without stopping.
