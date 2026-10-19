# Colors by role from the active theme, and the small formatters every widget shares.
import "theme" as $theme;

def esc: "\u001b";
def paint($code; $s): "\(esc)[\($code)m\($s)\(esc)[0m";
def rgb($r; $g; $b): "38;2;\($r);\($g);\($b)";
def bold($color): "1;" + $color;

def token($name): $theme::theme[0].palette[$name] | ltrimstr("#") | ascii_downcase | explode
  | map(if . >= 97 then . - 87 else . - 48 end)
  | rgb(.[0] * 16 + .[1]; .[2] * 16 + .[3]; .[4] * 16 + .[5]);

def brand: token("brand");
def accent: token("accent");
def accent_soft: token("accent_soft");
def ok: token("ok");
def warn: token("warn");
def danger: token("danger");
def merged: token("merged");
def bright: token("bright");
def divider_color: token("divider");
def track: token("track");
def caption($s): paint(token("caption"); $s);
def detail($s): paint(token("detail"); $s);

def severity($p; $warn_at; $critical_at): if $p >= $critical_at then danger elif $p >= $warn_at then warn else ok end;
def urgency($p; $warn_at; $critical_at): if $p >= $critical_at then 40 elif $p >= $warn_at then 20 else 0 end;
def link($url; $text): "\(esc)]8;;\($url)\(esc)\\\($text)\(esc)]8;;\(esc)\\";
def when(cond; s): if cond then s else empty end;
def maybe(cond; s): if cond then s else "" end;
def clip($n): if length > $n then .[0:$n - 1] + "…" else . end;
def repeat($s; $n): if $n > 0 then $s * $n else "" end;
def lpad($n): repeat(" "; $n - length) + .;
def rpad($n): . + repeat(" "; $n - length);

# The patched font draws the icon character as the mascot, across the theme's icon cells.
# iTerm2 draws that glyph's outline in the text color, so the icon has a color of its own.
def icon_char: $theme::theme[0].icon.char;
def icon: paint(token("icon"); icon_char);

def visible_width:
  gsub("\u001b\\]8;;[^\u001b]*\u001b\\\\"; "") | gsub("\u001b\\[[0-9;]*m"; "")
  | length + ($theme::theme[0].icon.cells - 1) * (split(icon_char) | length - 1);

def compact:
  if . >= 1000000 then "\(. / 100000 | floor / 10)M"
  elif . >= 1000 then "\(. / 1000 | round)k"
  else tostring end;

def bar($p; $width; $color):
  ([$p, 100] | min) * $width / 100 | round as $filled
  | paint($color; repeat("━"; $filled)) + paint(track; repeat("━"; $width - $filled));

def percent($p; $color): paint(bold($color); "\($p | floor)%" | lpad(5));
