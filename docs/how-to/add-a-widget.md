# Add a status line widget

A widget is one jq file in `widgets/` that turns the session into one cell of the status line. This guide adds `lines`, a widget that shows the lines added and removed in the session, and puts it in the layout. The [widget contract](../reference/widgets.md) lists everything a widget can read and call.

## 1. Write the widget

Create `widgets/lines.jq`. Its first line is the description that `kit widgets` shows.

```jq
# Lines added and removed in this session.

include "palette";
include "grid";

def widget:
  (.cost.total_lines_added // 0) as $added
  | (.cost.total_lines_removed // 0) as $removed
  | (paint(ok; "+\($added)") + " " + paint(danger; "-\($removed)")) as $counts
  | when($added + $removed > 0;
      cell(
        (caption("lines ") + $counts | variant(30)),
        ($counts | variant(0))));
```

`widget` returns a cell, or nothing when there is nothing to show. A cell lists its variants from widest to narrowest, and each variant carries a keep value. While the status line is wider than the terminal, the cell with the lowest keep among those that set the width steps down to its next variant. Give a widget a low keep when its detail matters less than its neighbours' detail.

## 2. Register it

Add an import and a branch to `widgets/registry.jq`.

```jq
import "lines" as lines;
```

```jq
  elif $name == "lines" then lines::widget
```

`make test` fails when a widget file is missing from the registry, so this step cannot be forgotten.

## 3. Put it in the layout

```bash
bin/kit layout "location,context" "git,limit_5h" "model,lines"
```

Each argument is one row of up to three widgets. The second column steps down as one across all rows, so meters there stay aligned as a table. The status line reads the layout on its next refresh, and `bin/kit preview <theme> --here` shows the result at once.

## 4. Test it

Add a case to `tests/test_statusline.py` that sets the fields your widget reads, renders at a wide and a narrow width, and checks the text. Then run `make check`.
