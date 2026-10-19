# Write a mod

A mod is a Claude Code plugin that runs inside the session. It can draw in the band above the prompt or in a pane, add slash commands, react to prompts and tool calls, and keep state. The kit loads every folder in `mods/` that holds a `.claude-plugin/plugin.json`, through the `CLAUDE_CODE_PLUGIN_DIRS` setting, so a new mod needs no change to the kit's code.

The welcome card in `mods/welcome/` is the reference mod. Read it before you start, since it is short and shows each part.

## 1. Let Claude Code write the skeleton

Claude Code ships a `plugin-authoring` skill that knows the current mod API, its types and its test runner. In a Claude Code session opened in this repository, ask for what you want, for example "a mod that shows a focus timer in the band above the prompt". The skill writes the mod and type-checks it. Ask it to place the result in `mods/<name>/`.

The repository's own [new-mod skill](../../.claude/skills/new-mod/SKILL.md) adds the kit's conventions on top.

## 2. Follow the kit's conventions

| Convention | Why |
| --- | --- |
| One folder per mod in `mods/`, named like the plugin | The kit loads by folder, and `name` in `plugin.json` is the key for its options |
| Tests in `mods/<name>/tests/*.test.tsx`, looped over the `terminal` and `desktop` surfaces | `claude plugin test` runs them in CI |
| Colors from the theme, never hard-coded | Switching themes must restyle every mod |
| `.catch(($, e, next) => next(e))` on hooks for `prompt.submit` and other gating events | A failing mod must never block the person |
| No network calls and no file writes outside the mod's state | Mods run in every session |

For theme colors, follow the welcome mod. The kit writes generated data into the mod (`hooks/cards.ts`) and passes the active theme as an option (`pluginConfigs.welcome.options.theme`). To do the same for your mod, extend `claude_kit/card.py` and `settings.kit_values`.

## 3. Check and load it

```bash
claude plugin validate mods/<name>
claude plugin test mods/<name>
bin/kit apply <theme>          # adds the new folder to CLAUDE_CODE_PLUGIN_DIRS
```

`make check` validates and tests every mod in `mods/`. Start a new Claude Code session to load it. While you develop, `claude --plugin-dir mods/<name>` loads it for one session and reloads it whenever you save.
