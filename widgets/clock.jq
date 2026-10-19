# The local time.

include "palette";
include "grid";

def widget: cell(now | strflocaltime("%H:%M") | detail(.) | variant(20));
