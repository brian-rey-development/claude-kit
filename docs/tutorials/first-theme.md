# Make your first theme

This tutorial turns one picture into a working theme, checks that its colors are readable, previews it, and applies it. It takes about ten minutes. You need claude-kit cloned and `install.sh` run once, so that `bin/kit` works.

## 1. Pick a picture

The same picture gives the theme its colors and its welcome card art, so a drawing with a few flat colors works best. A PNG with a transparent background gives the cleanest card, because transparent pixels stay empty in the terminal instead of becoming a colored box. Photos work too, with `--sampling average` in step 2.

The mascot glyph in the status line is drawn at about 16 pixels, so it reads best as a simple silhouette. If your picture is detailed, prepare a second, simpler one for `--icon`.

## 2. Generate the theme

```bash
bin/kit new-theme forest --image ~/Pictures/forest.png --name Forest --tagline "Grow a little every day." --emoji 🌲
```

The command writes `~/.config/claude-kit/themes/forest/` and draws the result in your terminal. The `--emoji` is the character the patched font replaces with your mascot. Pick one close to the mascot, because terminals without the font show the emoji itself.

Inside the folder you now have these files.

| File | Made from |
| --- | --- |
| `theme.json` | The palette and terminal colors, taken from the picture and adjusted until every text color is readable |
| `claude.json` | Claude Code's own color theme, derived from the palette |
| `art.json` | The welcome card in three sizes |
| `glyph/icon.png` | The mascot for the font |
| `source/` | A copy of your picture, so you can regenerate the art later |

## 3. Check it

```bash
bin/kit check forest
```

A generated theme always passes, because the generator moves each color away from the background until it reaches WCAG AA contrast. If you edit colors by hand in step 4, run the check again.

## 4. Adjust to taste

Open `theme.json`. The palette names roles rather than hues, so you can change what a role looks like without hunting through code. `brand` colors the repository name, `accent` the branch, and `ok`, `warn` and `danger` the meters at each level. The [theme format reference](../reference/theme-format.md) describes every role. To make a color readable again after an edit, see [tune a palette](../how-to/tune-a-palette.md).

If the card art lost detail, regenerate it with other options.

```bash
bin/kit art forest ~/Pictures/forest.png --sampling average --colors 12
```

## 5. Preview it

```bash
bin/kit preview forest --here    # in this terminal
bin/kit preview forest           # live, in a new iTerm2 window with a Claude Code session
```

The live preview runs a real Claude Code session with the theme, while your own settings and default profile stay as they are.

## 6. Apply it

```bash
bin/kit apply forest --dry-run
bin/kit apply forest
```

Open a new tab and start `claude`. The welcome card greets you until your first message, and the status line uses your colors. To go back to Moonlit later, run `bin/kit apply moonlit`.
