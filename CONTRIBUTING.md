# Contributing

Thank you for helping. This page covers the setup, the checks a change must pass, and the conventions the code follows.

## Set up

You need macOS, [uv](https://docs.astral.sh/uv/), `jq`, `shellcheck` and [Claude Code](https://docs.claude.com/en/docs/claude-code/setup).

```bash
brew install uv shellcheck jq
git clone https://github.com/brian-rey-development/claude-kit && cd claude-kit
make check
```

`make check` runs ruff, pyright in strict mode, the pytest suite on Python 3.9, shellcheck, and `claude plugin validate` and `claude plugin test` for every mod. CI runs the same target on macOS, so a change that passes locally passes there.

## Make a change

1. Open an issue first for anything larger than a fix, so we can agree on the shape before you write it.
2. Write the test first. A bug fix needs a test that fails without the fix.
3. Run `make format`, then `make check`.
4. Update the docs the change touches. [AGENTS.md](AGENTS.md) maps what lives where, and [docs/reference/files.md](docs/reference/files.md) must list every file the kit writes.
5. If the change alters what a README screenshot shows, commit it, run `make screenshots` on the clean tree, and commit the new images.
6. Use [Conventional Commits](https://www.conventionalcommits.org), such as `feat(widgets): add a lines widget`.

## Conventions

- Python runs on 3.9, the version macOS ships, and uses only `fonttools`, `pillow` and `jsonschema` at runtime.
- Small functions with plain names, data over configuration, and pure functions wherever the work allows. `settings.py` is the model, since every function there is pure and the tests check round trips.
- Comments explain a reason the code cannot show, never what the code does.
- Tests never touch the real home folder. Use the `paths` fixture.
- New themes in this repository need original art under CC0 and must pass `kit check` with no warnings.

## Share a theme without a pull request

A theme is a folder. Zip it or put it in its own repository, and others copy it into `~/.config/claude-kit/themes/`. Bundled themes are kept few on purpose, so each one can be maintained.
