# Meters share one ladder (long bar, short bar, no detail, number only), so a column of them steps
# together. $alert is the short warning that outlives the detail on the narrow rungs.

include "palette";
include "grid";

def meter($label; $short; $p; $color; $detail; $alert; $boost):
  cell(
    (bar($p; 10; $color) + percent($p; $color) + $detail | variant($label; 45 + $boost)),
    (bar($p; 5; $color) + percent($p; $color) + $detail | variant($label; 60 + $boost)),
    (bar($p; 5; $color) + percent($p; $color) + $alert | variant($label; 80 + $boost)),
    (percent($p; $color) + $alert | variant($short; 0)));

def weekday: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][strflocaltime("%w") | tonumber];
def day_key: strflocaltime("%Y-%m-%d");
def reset_time:
  strflocaltime("%H:%M") as $clock
  | if day_key == (now | day_key) then "at " + $clock
    elif day_key == (now + 86400 | day_key) then "tomorrow " + $clock
    else "\(weekday) " + $clock end;

# At the pace used so far in this window, when the limit runs out, or null if it lasts.
# The first 5% of a window and usage under 5% say too little about the pace to project from.
def runs_out_at($window; $length):
  if $window.resets_at == null then null
  else
    ($length - ($window.resets_at - now)) as $elapsed
    | if $elapsed < $length * 0.05 or $window.used_percentage < 5 then null
      else (now + (100 - $window.used_percentage) * $elapsed / $window.used_percentage) as $at
      | if $at < $window.resets_at then $at else null end
      end
  end;

def limit_meter($label; $short; $window; $length):
  when($window != null and $window.used_percentage != null;
    $window.used_percentage as $p
    | runs_out_at($window; $length) as $out
    | (if $out != null then danger else severity($p; 60; 85) end) as $color
    | (if $out != null then 40 else urgency($p; 60; 85) end) as $boost
    | maybe($window.resets_at != null; detail("  resets " + ($window.resets_at | reset_time))) as $reset
    | (if $out == null then $reset
       else paint(bold(danger); "  runs out " + ($out | reset_time)) + detail(" · resets " + ($window.resets_at | reset_time)) end) as $note
    | maybe($out != null; paint(bold(danger); "  out " + ($out | reset_time | ltrimstr("at ")))) as $alert
    | meter($label; $short; $p; $color; $note; $alert; $boost));
