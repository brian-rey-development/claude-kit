# How full the context window is, with the token count.

include "palette";
include "meters";

def widget:
  .context_window as $cw
  | ($cw.used_percentage // 0) as $p
  | (if $cw.used_percentage == null then track else severity($p; 50; 75) end) as $color
  | maybe(($cw.total_input_tokens // 0) > 0;
      detail("  \($cw.total_input_tokens | compact) / \($cw.context_window_size | compact)")) as $tokens
  | meter("context"; "ctx"; $p; $color; $tokens; ""; urgency($p; 50; 75));
