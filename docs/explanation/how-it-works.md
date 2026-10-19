# How it works

claude-kit is a thin layer over four extension points that Claude Code, macOS and iTerm2 already offer. A theme is pure data, and every part of the kit reads that data instead of naming colors itself, so one palette restyles the status line, the welcome card, Claude Code and the terminal at once.

## The status line

Claude Code runs the command in `statusLine` after each message and every `refreshInterval` seconds, and pipes the session to it as JSON. The kit's command is `statusline/statusline.sh`, and a render takes under 50 ms.

The script reads git state and the session's pull request from caches in `$TMPDIR/claude-kit/` and starts a background refresh for the next render. This stale-while-revalidate pattern, the same one HTTP caches use, means a render never waits on git or the network, so a slow repository or a GitHub outage cannot freeze the prompt. The PR cache exists because Claude Code reports only the current branch's pull request, while a session that ships work from another worktree has opened a PR on a different branch. The script finds the last PR link in the session's transcript and asks `gh` for its state, at most once a minute.

Then one `jq` process does all the rendering. `render.jq` looks up each widget the layout names in `widgets/registry.jq`, and `grid.jq` fits the cells to the terminal. The fitting step is a greedy algorithm. Every cell is a ladder of variants from widest to narrowest, each with a keep value. While the grid is wider than `$COLUMNS`, the algorithm finds the cells that set the overflowing width and steps down the one with the lowest keep, then measures again. Each step strictly shrinks a cell and every ladder is finite, so it always ends. It also degrades in a predictable order, with decoration first, then detail, and the identifying text last. The second column steps as one, so the three meters always read as a table.

A limit meter also projects when the limit runs out. It assumes the usage so far in the window continues at the same pace, and when that pace would reach 100% before the reset, the meter turns to the danger color and prints the time. It stays quiet during the first 5% of a window and below 5% usage, where the pace says too little to project from.

## The welcome card

The card is a mod, `mods/welcome/`, which Claude Code loads through `CLAUDE_CODE_PLUGIN_DIRS`. It draws in the band above the prompt until the first message of the session. The art is half-block pixel art. Each terminal cell shows "▀" with a foreground and a background color, which packs two square pixels into one cell, so a 30 by 30 pixel picture fits in 30 columns and 15 rows. `kit art` samples the image down with a small palette taken from the image itself, and merges neighbouring cells of the same colors into runs, which keeps the element tree small.

The band shares half the terminal's height with the prompt and the status line, so the art comes in three heights and the mod draws the largest that fits. The mod cannot read files, so the kit generates `cards.ts` with every theme's card and passes the active theme's id as the mod's `theme` option. A preview session passes another id, which is how a preview shows a different card without touching the installed one.

## The mascot glyph

Terminals draw text from a font, so the cheapest way to put a picture in the status line is to make it a character. The kit copies Apple's Monaco and maps the theme's icon character, such as 🌙, to a new glyph. The glyph carries two forms. An `sbix` table holds PNG bitmaps at fourteen sizes, which Core Text draws in full color. A TrueType outline traced from the bitmap's opaque pixels serves renderers that draw every glyph in one color, as iTerm2 does. That is why the palette has an `icon` role, since iTerm2 paints the outline in the text color around it.

The icon is an emoji on purpose. Terminals give emoji two cells, which gives the mascot room, and a terminal without the patched font still shows something that means the same thing. The font's version string stores a fingerprint of the theme's glyph files, so `kit apply` rebuilds the font only when they change.

## The iTerm2 profile

The kit installs a dynamic profile, a JSON file in iTerm2's `DynamicProfiles` folder, which a running iTerm2 loads at once. The profile names your current default as its parent, so it inherits your keys, scrollback and every other setting, and overrides only the font, the colors and the working directory of new splits and tabs.

Making it the default profile is the one change that cannot happen while iTerm2 runs, since iTerm2 writes its preferences back when it quits and would undo the change. When iTerm2 is open, the kit starts a small detached process that waits for iTerm2 to quit and then sets the default. Before it does, it records the previous default, and uninstall uses the same mechanism to restore it.

## Undo

Every apply records what it changed in `~/.config/claude-kit/state.json`. For settings it records each owned key's value before the first apply. Uninstall puts a key back only while it still holds the kit's value, so a setting you changed by hand after installing stays yours. The test suite checks that apply followed by uninstall returns `settings.json` to exactly what it was, for several starting points.
