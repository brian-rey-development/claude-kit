# One row per subagent in the agent panel, columns aligned across rows:
#   mark  type  label …  ━━━━━  17%  34k  2m10s
# The label takes whatever width is left; on narrow panels the bar goes first, then the token count.

include "palette";

def status_style:
  { completed: {mark: "✓", tone: "done"},
    killed: {mark: "■", tone: "done"},
    failed: {mark: "✗", tone: "failed"} }[.status] // {mark: "●", tone: "live"};

def toned($tone; $live; $s):
  if $tone == "failed" then paint(danger; $s)
  elif $tone == "done" then caption($s)
  else paint($live; $s) end;

def two_digits: tostring | lpad(2) | gsub(" "; "0");
def elapsed:
  ((now * 1000 - .) / 1000 | floor | [., 0] | max) as $s
  | if $s >= 3600 then "\($s / 3600 | floor)h\($s % 3600 / 60 | floor | two_digits)m"
    elif $s >= 60 then "\($s / 60 | floor)m\($s % 60 | two_digits)s"
    else "\($s)s" end;

def kind: .agentType // .name // "agent";
def context_pct: if .contextWindowSize then .tokenCount * 100 / .contextWindowSize else null end;

# Fixed parts: mark and space, type, three two-space gaps, meter (bar 5 + pct 5), tokens 5 + gap, time 6.
def layout($columns; $type_width):
  ($columns - (2 + $type_width + 6 + 10 + 7 + 6)) as $room
  | if $room >= 12 then {bar: true, tokens: true, room: $room}
    elif $room + 5 >= 12 then {bar: false, tokens: true, room: ($room + 5)}
    else {bar: false, tokens: false, room: ([$room + 12, 4] | max)} end;

def meter_cell($l):
  context_pct as $p
  | if $p == null then repeat(" "; if $l.bar then 10 else 5 end)
    else severity($p; 50; 75) as $color | maybe($l.bar; bar($p; 5; $color)) + percent($p; $color) end;

def row($l; $type_width):
  status_style as $style
  | toned($style.tone; accent; $style.mark) as $mark
  | toned($style.tone; bold(accent_soft); kind | clip($type_width) | rpad($type_width)) as $type
  | toned($style.tone; token("detail"); (.label // .description // "") | clip($l.room) | rpad($l.room)) as $label
  | maybe($l.tokens; detail((.tokenCount // 0) | compact | lpad(5)) + "  ") as $tokens
  | "\($mark) \($type)  \($label)  \(meter_cell($l))  \($tokens)\(detail(.startTime | elapsed | lpad(6)))";

.columns as $columns
| ([.tasks[] | kind | length] | max // 5 | [., 16] | min) as $type_width
| layout($columns; $type_width) as $layout
| .tasks[]
| {id, content: row($layout; $type_width)}
