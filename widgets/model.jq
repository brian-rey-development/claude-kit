# The model, its effort level and fast mode, and the session's API cost when there is one.

include "palette";
include "grid";

def dollars: (. * 100 | round) as $c | "$\($c / 100 | floor).\($c % 100 + 100 | tostring | .[1:])";

def widget:
  when(.model.display_name != null;
    .model.display_name as $name
    | ([.effort.level, when(.fast_mode == true; "fast")] | map(select(. != null))) as $extras
    | (.cost.total_cost_usd // 0) as $usd
    | maybe($usd > 0; "   " + caption("API cost ") + paint(bold(bright); $usd | dollars)) as $cost
    | maybe($usd > 0; "   " + paint(bright; $usd | dollars)) as $cost_short
    | (paint(bold(bright); $name) + maybe($extras != []; detail(" · " + ($extras | join(" · "))))) as $full
    | cell(
        ($full + $cost | variant(35)),
        ($full + $cost_short | variant(50)),
        (paint(bold(bright); $name) + $cost_short | variant(65)),
        (paint(bold(bright); $name) | variant(0))));
