# Tune a palette

Every role in a theme's palette that draws text needs a contrast ratio of at least 4.5:1 against `terminal.background`, which is the WCAG AA level for normal text. The icon needs 3:1, the level for graphics. `divider` and `track` are decorative and have no minimum. This guide shows how to find a color that fails and fix it without losing its character.

## Find what fails

```bash
bin/kit check forest
```

Each failing role is listed with its color, its ratio and the minimum, for example `caption #6B7389 has 3.86:1 against the background, needs 4.5:1`.

## Fix it by lightness alone

Keep the hue and the saturation and change only the lightness. On a dark background make the color lighter, and on a light background make it darker. The kit does the same when it generates a theme, in steps of 2% lightness.

```bash
.venv/bin/python -c "
from claude_kit.generate import readable
print(readable('#6B7389', '#11151F'))"
```

`readable(color, background)` returns the nearest color with the same hue and saturation that reaches 4.5:1. Pass a third argument such as `3.0` for the icon. Paste the result into `theme.json` and run `bin/kit check` again.

## Keep the roles distinct

Readable is not enough when two roles look alike. `ok`, `warn` and `danger` color the same meters at different levels, so they need hues far apart, and should not rely on hue alone, since about one man in twelve sees red and green as similar. The meters also change the bar length and print the number, so they stay readable for everyone.

`caption` and `detail` are the quiet roles. Keep them lighter or darker than the body text by a clear step, so labels recede while values stand out.
