# CLI reference

Run commands as `bin/kit <command>` from the repository, or as `kit <command>` once setup has linked it into `~/.local/bin`. Every command prints plain text without color when its output is not a terminal, and honors `NO_COLOR`. A command exits with 0 on success and 1 when something needs fixing, with the fix printed under the problem.

## Applying themes

| Command | What it does |
| --- | --- |
| `kit setup` | Guided setup. Checks the Mac, lets you pick and preview a theme, lists every change and asks before making it. Needs a terminal. |
| `kit apply <theme> [--dry-run] [--iterm-default]` | Applies a theme without questions. `--dry-run` lists the changes and makes none. `--iterm-default` also makes the theme's profile the iTerm2 default, at once when iTerm2 is closed or when it next quits. |
| `kit preview <theme> [--here]` | Opens a new iTerm2 window with a Claude Code session that uses the theme, leaving your settings alone. `--here` draws the card and the status line in the current terminal instead. |
| `kit uninstall [--yes]` | Restores what the kit changed and removes what it added. Your own themes and the settings backups stay. |
| `kit doctor` | Checks the tools, the active theme, the font, the settings, a status line render and the iTerm2 profile. |

`<theme>` is a theme id, such as `moonlit`, or the path to a theme folder.

## Making themes

| Command | What it does |
| --- | --- |
| `kit themes` | Lists every theme, bundled and yours, with its colors. The active one is marked. |
| `kit new-theme <id> --image <file>` | Makes a theme in `~/.config/claude-kit/themes/<id>/` from an image. |
| `kit art <theme> <image> [--sampling majority\|average] [--colors N]` | Rebuilds a theme's welcome card art from an image, in three sizes. |
| `kit check [<theme>...]` | Validates themes against the schema and the contrast rules. Checks every theme when none is named. |

Options of `kit new-theme`.

| Option | Default | Meaning |
| --- | --- | --- |
| `--image <file>` | required | The picture for the card art and the colors |
| `--icon <file>` | the image | A simpler picture for the font glyph |
| `--name <text>` | the id, capitalized | Display name, also the font family and the iTerm2 profile name |
| `--tagline <text>` | "One careful step at a time." | The line beside the card art |
| `--emoji <char>` | ⭐ | The character the glyph replaces; terminals without the font show it |
| `--light` | off | Generate a light background instead of a dark one |
| `--sampling` | `majority` | `majority` keeps flat drawings crisp, `average` suits photos |

## Status line

| Command | What it does |
| --- | --- |
| `kit widgets` | Lists the widgets with their descriptions. The ones in your layout are marked. |
| `kit layout [<row>...]` | Without arguments, prints the layout. With arguments, sets it, one argument per row of up to three comma-separated widgets. |

```bash
kit layout "location,context" "git,limit_5h" "model,limit_week"
```
