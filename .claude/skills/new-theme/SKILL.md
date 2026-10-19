---
name: new-theme
description: Make a claude-kit theme from an image the person provides, check its contrast, preview it and apply it. Use when someone asks for a theme, a look, colors or a mascot based on a picture, a character, a brand or a mood.
---

# Make a theme from an image

You turn one picture into a theme with `bin/kit new-theme`, refine it with the person, and apply it only after they have seen it.

## 1. Gather the inputs

Ask only for what is missing.

- **The picture.** A drawing with few flat colors and a transparent background gives the best card. For a photo, plan on `--sampling average`.
- **A simpler mascot for the glyph**, when the picture is detailed. The glyph is drawn at about 16 pixels, so a bold silhouette reads best. Pass it as `--icon`.
- **The id and name**, such as `forest` and `Forest`.
- **A tagline** in the person's own words. Never quote copyrighted lines; write an original one if they ask you to.
- **An emoji** close to the mascot, shown wherever the patched font is missing.
- **Dark or light.** Default to dark unless they ask.

If the picture is someone else's artwork, tell the person the theme must stay private, in `~/.config/claude-kit/themes/`, and must not be committed or shared.

## 2. Generate and look

```bash
bin/kit new-theme <id> --image <file> [--icon <file>] --name "<Name>" --tagline "<text>" --emoji <emoji> [--light] [--sampling average]
bin/kit check <id>
bin/kit preview <id> --here
```

Describe what you see in the preview output. When the card lost the subject, try `bin/kit art <id> <file> --sampling average --colors 12`, or crop the image to the subject first.

## 3. Refine the palette

Edit `~/.config/claude-kit/themes/<id>/theme.json`. The roles are listed in `docs/reference/theme-format.md`. After each color change, run `bin/kit check <id>`. When a color falls short, keep its hue and fix its lightness with `claude_kit.generate.readable`, as `docs/how-to/tune-a-palette.md` shows. If you change the palette a lot, regenerate `claude.json` with `claude_kit.claude_theme.derive`.

## 4. Preview live, then apply

```bash
bin/kit preview <id>                 # new iTerm2 window, nothing installed
bin/kit apply <id> --dry-run         # show the person this list
bin/kit apply <id>                   # only after they agree
bin/kit doctor
```

Tell them to open a new tab and start `claude` to see it.
