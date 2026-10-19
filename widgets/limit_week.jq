# The weekly usage limit, when it resets, and when it runs out at the current pace.

include "meters";

def widget: limit_meter("weekly limit"; "week"; .rate_limits.seven_day; 604800);
