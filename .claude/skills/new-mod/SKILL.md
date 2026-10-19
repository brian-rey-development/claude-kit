---
name: new-mod
description: Build a mini app for claude-kit as a Claude Code mod in mods/, following the kit's conventions. Use when someone wants something new inside the Claude Code session, such as a band above the prompt, a pane or a slash command.
---

# Build a mod

1. **Load Claude Code's `plugin-authoring` skill.** It has the current mod API, the types and the test runner. Use it to write the mod, and place the mod in `mods/<name>/` with `name` in `plugin.json` matching the folder.
2. **Study `mods/welcome/`.** It is the reference for the kit's conventions, which `docs/how-to/write-a-mod.md` lists.
3. **Take colors from the theme.** A mod cannot read files. When it needs theme data, generate it into the mod from `claude_kit/card.py` and pass the active theme through `pluginConfigs.<name>.options` in `claude_kit/settings.kit_values`, as the welcome card does.
4. **Never block the person.** Give every hook on a gating event, such as `prompt.submit`, a `.catch(($, e, next) => next(e))`.
5. **Test on two surfaces.** Write `mods/<name>/tests/*.test.tsx` that loop over `['terminal', 'desktop']`, and run `make check`, which validates and tests every mod.
6. **Load it.** `bin/kit apply <theme>` adds every folder in `mods/` to `CLAUDE_CODE_PLUGIN_DIRS`. The person starts a new session to use it.
