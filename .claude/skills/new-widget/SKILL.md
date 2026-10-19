---
name: new-widget
description: Add a status line widget to claude-kit, register it, put it in the layout and test it. Use when someone wants the status line to show something new.
---

# Add a status line widget

Read `docs/reference/widgets.md` first. It lists the input fields, the helpers and the rules.

1. **Check the data exists.** A widget may only read the session JSON and the two cached fields the kit adds. It must not run programs or read files, since it runs on every render. If the data needs a program, add a cached refresh to `statusline/statusline.sh` the way git and the PR are cached, and pass the result in as a new input field.
2. **Write `widgets/<name>.jq`.** Start with a one-sentence comment, include `palette` and `grid`, and define `widget` as a `cell` of variants from widest to narrowest, the last with keep 0. Return nothing when there is nothing to show. Read every field with a `//` default.
3. **Register it** in `widgets/registry.jq` with an import and an `elif` branch.
4. **Test it.** Add cases to `tests/test_statusline.py` for a wide and a narrow terminal and for missing fields. Run `make check`.
5. **Show it.** `bin/kit layout ...` with the new widget, then `bin/kit preview <theme> --here`. `kit widgets` lists it from its first comment line, so it needs no other documentation.

Never name a jq parameter after a helper you call in the same function, such as `$warn` next to `warn`. jq turns the parameter into a filter of the same name, which silently hides the helper.
