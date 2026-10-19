# Lays widgets out as rows of up to three cells. The first column is padded to one width so the
# second starts at the same column on every row, and labels in a column share a width so bars line
# up. Each cell is a ladder of variants, widest first. While the grid is wider than the terminal,
# the lowest-keep cell among those that set the overflowing width steps down one rung.

include "palette";

def divider: "  " + paint(divider_color; "│") + "  ";
def spacer: "   ";
def gap_before($c): if $c == 1 then divider else spacer end;
def gap_width($c): if $c == 1 then 5 else 3 end;

def variant($label; $keep): {label: $label, body: ., bw: visible_width, keep: $keep};
def variant($keep): variant(null; $keep);
def cell(variants): {i: 0, v: [variants]};

def current: .v[.i];
def label_width: current | if .label == null then 0 else .label | length end;
def cell_width($lw): current | if .bw == 0 then 0 elif .label == null then .bw else $lw + 1 + .bw end;

def column_label_width($grid; $c): [$grid[] | .[$c] | select(. != null) | label_width] | max // 0;
def column_width($grid; $c):
  column_label_width($grid; $c) as $lw
  | [$grid[] | .[$c] | select(. != null) | cell_width($lw)] | max // 0;

def row_width($grid):
  [ range(0; 3) as $c
    | {c: $c, w: (if $c == 0 then column_width($grid; 0)
                  else (.[$c] | if . == null then 0 else cell_width(column_label_width($grid; $c)) end) end)} ]
  | map(select(.w > 0))
  | if length == 0 then 0 else (map(.w) | add) + ([.[1:][] | gap_width(.c)] | add // 0) end;

def grid_width: . as $grid | [.[] | row_width($grid)] | max // 0;

def steppable: . != null and .i < (.v | length) - 1;

def binding_cells:
  . as $grid
  | grid_width as $gw
  | column_width($grid; 0) as $first
  | column_label_width($grid; 0) as $lw0
  | [ range(0; $grid | length) as $r
      | $grid[$r] as $row
      | ( ($row[0] | select(steppable and cell_width($lw0) == $first) | {r: $r, c: 0, keep: current.keep}),
          ( select(($row | row_width($grid)) == $gw)
            | range(1; 3) as $c
            | $row[$c] | select(steppable and current.bw > 0) | {r: $r, c: $c, keep: current.keep} ) ) ];

# The second column steps as one, so its rows always read as a table.
def step($next):
  if $next.c == 1
  then map(if .[1] == null then . else .[1].i = ([.[1].i + 1, (.[1].v | length) - 1] | min) end)
  else .[$next.r][$next.c].i += 1 end;

def fit($budget):
  if grid_width <= $budget then .
  else
    (binding_cells | min_by(.keep)) as $next
    | if $next == null then . else step($next) | fit($budget) end
  end;

def render_cell($lw; $width):
  if . == null or current.bw == 0 then repeat(" "; $width)
  else
    current as $v
    | (if $v.label == null then $v.body
       else caption($v.label + repeat(" "; $lw - ($v.label | length))) + " " + $v.body end)
      + repeat(" "; $width - cell_width($lw))
  end;

def last_filled: [range(0; 3) as $c | select(.[$c] != null and (.[$c] | current.bw) > 0) | $c] | max // -1;

def render_row($grid):
  . as $row
  | last_filled as $last
  | [ range(0; $last + 1) as $c
      | (if $c == 0 then "" else gap_before($c) end)
        + ($row[$c] | render_cell(column_label_width($grid; $c); if $c == 0 and $last > 0 then column_width($grid; 0) else 0 end)) ]
  | join("");

def render($budget):
  fit($budget) as $fitted
  | $fitted[]
  | render_row($fitted)
  | select(gsub(" "; "") | length > 0);
