# The 5-hour usage limit, when it resets, and when it runs out at the current pace.

include "meters";

def widget: limit_meter("5h limit"; "5h"; .rate_limits.five_hour; 18000);
