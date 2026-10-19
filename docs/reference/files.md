# Files the kit writes

The kit changes nothing outside this list. `kit apply --dry-run` prints the same list for a given theme, and `kit uninstall` undoes each entry.

| Path | Written by | What it holds | Undone by uninstall |
| --- | --- | --- | --- |
| `~/.claude/settings.json` | apply | Sets `statusLine`, `subagentStatusLine`, `theme` and `pluginConfigs.welcome`, and adds the kit's mods to `env.CLAUDE_CODE_PLUGIN_DIRS` beside any folders already there | Each key gets back the value it had before the first apply, unless you changed it since |
| `~/.config/claude-kit/backups/settings.<time>.json` | apply | A copy of `settings.json` before each apply | Kept |
| `~/.claude/themes/<id>.json` | apply | A link to the theme's `claude.json` | Removed |
| `~/Library/Fonts/Monaco<Name>.ttf` | apply, preview | Monaco with the theme's mascot glyph | Removed |
| `~/Library/Application Support/iTerm2/DynamicProfiles/claude-kit.json` | apply | The theme's iTerm2 profile, built on your default profile | Removed |
| `~/Library/Application Support/iTerm2/DynamicProfiles/claude-kit-preview.json` | preview | The profile for preview windows | Removed |
| iTerm2's `Default Bookmark Guid` preference | apply with `--iterm-default` | Makes the theme's profile the default, written when iTerm2 is closed | Set back to your previous default |
| `~/.config/claude-kit/current` | apply | A link to the active theme's folder | Removed |
| `~/.config/claude-kit/config.json` | apply, layout | The active theme and the status line layout | Removed |
| `~/.config/claude-kit/state.json` | apply, preview | What the kit changed, so uninstall can undo exactly that | Removed |
| `~/.config/claude-kit/preview-settings.json` | preview | Settings for preview sessions | Removed |
| `~/.config/claude-kit/iterm-default.pid` | apply with `--iterm-default` while iTerm2 runs | The process that sets the default profile once iTerm2 quits | Process stopped, file removed |
| `~/.config/claude-kit/themes/` | new-theme | Your own themes | Kept |
| `~/.local/bin/kit` | setup, when you accept | A link to `bin/kit` | Removed |
| `mods/welcome/hooks/cards.ts` in the repository | apply, preview, art, new-theme | Every theme's welcome card, generated | Removed |
| `$TMPDIR/claude-kit/` | the status line | Caches of git status and the session's PR | Cleared by macOS |

Set `CLAUDE_KIT_HOME` to keep the kit's own files somewhere other than `~/.config/claude-kit`, and `CLAUDE_CONFIG_DIR` if your Claude Code settings live outside `~/.claude`.
