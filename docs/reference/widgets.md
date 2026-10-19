# Widget contract

A widget is a jq module in `widgets/` that defines `widget`. The status line calls it once per render with the session as input, and lays out the cell it returns.

## Input

The input is the JSON that Claude Code sends to status line commands, plus two fields the kit adds.

| Field | Meaning |
| --- | --- |
| `.workspace.current_dir`, `.workspace.project_dir`, `.cwd` | Where the session runs |
| `.model.display_name`, `.effort.level`, `.fast_mode` | The model and how it runs |
| `.context_window.used_percentage`, `.total_input_tokens`, `.context_window_size` | Context use |
| `.rate_limits.five_hour`, `.rate_limits.seven_day` | Each with `used_percentage` and `resets_at` in Unix seconds |
| `.cost.total_cost_usd`, `.cost.total_lines_added`, `.cost.total_lines_removed` | Session totals |
| `.pr` | The pull request of the current branch, when Claude Code knows it |
| `.git_status` | Added by the kit. The output of `git status --porcelain=v2 --branch` for the session's folder, from a cache refreshed in the background |
| `.session_pr` | Added by the kit. The last pull request linked in the session's transcript, with `number`, `url` and `review_state` |

Claude Code adds fields over time. Read them with `//` defaults, so a missing field never breaks the render.

## Output

`widget` returns a cell, or `empty` when there is nothing to show.

```jq
cell(
  (wide_text | variant(40)),
  (narrow_text | variant(0)))
```

A cell holds its variants from widest to narrowest. `variant($keep)` takes the text as input. `variant($label; $keep)` adds a label that lines up with the other labels in the column, as the meters do. While the grid is wider than the terminal, the cell with the lowest keep among those that set the width moves to its next variant. The last variant should have keep 0 and be as short as the widget can usefully be.

## Helpers

Include `palette` for colors and formatting, `grid` for `cell` and `variant`, and `meters` for bars and limits.

| Helper | Module | What it does |
| --- | --- | --- |
| `brand`, `accent`, `accent_soft`, `ok`, `warn`, `danger`, `merged`, `bright`, `track`, `divider_color` | palette | The theme's color for a role, as an SGR code |
| `paint($color; $text)`, `bold($color)` | palette | Colors text |
| `caption($text)`, `detail($text)` | palette | Text in the quiet roles |
| `icon` | palette | The theme's mascot character in its color |
| `link($url; $text)` | palette | A clickable OSC 8 link |
| `when(cond; s)`, `maybe(cond; s)` | palette | `s` when the condition holds, else nothing or an empty string |
| `clip($n)`, `lpad($n)`, `rpad($n)`, `compact` | palette | Shorten, pad, and format counts such as `76k` |
| `bar($p; $width; $color)`, `percent($p; $color)` | palette | A meter bar and its percentage |
| `severity($p; $warn_at; $critical_at)` | palette | `ok`, `warn` or `danger` for a percentage |
| `meter($label; $short; $p; $color; $detail; $alert; $boost)` | meters | A full meter cell with the shared four-step ladder |
| `limit_meter($label; $short; $window; $seconds)` | meters | A usage limit meter that predicts when the limit runs out |

## Rules

- The first line of the file is a comment that describes the widget in one sentence. `kit widgets` prints it.
- Register the widget in `widgets/registry.jq`. A test fails when a file is missing there.
- A widget runs on every render, about every 15 seconds and after each message, so it must not call programs or read files. The status line already caches git and the PR for you.
- Do not name a jq parameter after a helper you call in the same function. `def f($warn)` also defines a filter `warn` inside `f`, which hides the palette's `warn`.
