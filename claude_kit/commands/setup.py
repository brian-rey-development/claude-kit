from __future__ import annotations

import argparse
import os
from pathlib import Path

from claude_kit import doctor, iterm, preview, state, theme, ui
from claude_kit.commands import Command
from claude_kit.commands.apply import checked
from claude_kit.errors import KitError
from claude_kit.install import Step, apply_steps, execute, link
from claude_kit.paths import Paths
from claude_kit.theme import Theme

INTRO = """claude-kit dresses Claude Code in a theme, with a status line, a welcome card, matching
colors and an iTerm2 profile whose font draws the theme's mascot. You will see each change before
it is made, and `kit uninstall` puts everything back."""


def preflight(paths: Paths) -> None:
    problems = [finding for finding in doctor.tools(paths) if finding.level == "fail"]
    for problem in problems:
        ui.fail(problem.message)
        ui.note(f"Fix: {problem.fix}")
    if problems:
        raise KitError("Fix the problems above, then run `kit setup` again.")
    if not iterm.is_installed():
        ui.warn("iTerm2 is not installed. The status line and welcome card work in any terminal;")
        ui.note("the colors and the mascot font need iTerm2 (https://iterm2.com).")


def choose_theme(themes: list[Theme]) -> Theme:
    if len(themes) == 1:
        ui.heading(f"{themes[0].name}, the bundled theme")
        return themes[0]
    options = [f"{t.name:<14} {preview.swatches(t)}  {ui.dim(t.description)}" for t in themes]
    return themes[ui.choose("Which theme would you like?", options)]


def pick(paths: Paths) -> Theme:
    themes = theme.discover(paths)
    while True:
        chosen = choose_theme(themes)
        preview.here(paths, chosen)
        if iterm.is_installed() and ui.confirm("Try it live in a new iTerm2 window first?", default=False):
            preview.live(paths, chosen, Path.cwd())
            ui.note("A preview window is open. Come back here when you have looked around.")
        if ui.confirm(f"Use {chosen.name}?"):
            return chosen
        if len(themes) == 1:
            raise KitError(
                "Nothing was changed.", "Make a theme of your own with `kit new-theme`, then run setup again."
            )


def offer_kit_command(paths: Paths) -> None:
    target = paths.local_bin / "kit"
    on_path = str(paths.local_bin) in os.environ.get("PATH", "").split(":")
    if target.exists() or not on_path:
        return
    if ui.confirm(f"Add the `kit` command to {paths.local_bin}, so it works from any folder?"):
        link(paths.kit / "bin" / "kit", target)
        record = state.load(paths)
        record.kit_link = str(target)
        state.save(paths, record)
        ui.step("`kit` is ready. Try `kit doctor`.")


def confirm_plan(steps: list[Step]) -> bool:
    ui.heading("These changes will be made")
    for step in steps:
        ui.item(step.title)
    return ui.confirm("Apply them?")


def finish(paths: Paths, chosen: Theme) -> None:
    ui.heading(f"{chosen.name} is ready")
    if iterm.is_waiting_to_set_default(paths):
        ui.item("Quit iTerm2 once (Cmd+Q) and open it again to start with the new profile.")
    ui.item("Start `claude` in a new tab to see the welcome card and the status line.")
    ui.item("`kit doctor` checks the setup, `kit themes` lists themes, `kit uninstall` undoes it all.")


def run(_: argparse.Namespace, paths: Paths) -> int:
    if not ui.interactive():
        raise KitError(
            "Setup asks questions, so it needs a terminal.",
            "Scripts and agents use `kit apply <theme>` instead.",
        )
    ui.heading("Welcome to claude-kit")
    print(INTRO)
    preflight(paths)
    chosen = checked(paths, pick(paths).id)
    make_default = iterm.is_installed() and ui.confirm(f"Make {chosen.name} your default iTerm2 profile?")
    steps = apply_steps(paths, chosen, iterm_default=make_default)
    if not confirm_plan(steps):
        ui.note("Nothing was changed.")
        return 0
    execute(steps)
    offer_kit_command(paths)
    finish(paths, chosen)
    return 0


COMMAND = Command("setup", "Pick, preview and apply a theme, one step at a time.", run)
