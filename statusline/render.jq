# The status line: the session JSON Claude Code sends, plus the git state and the session's PR, laid
# out as the rows in the config. Run by statusline.sh.

include "grid";
import "registry" as registry;

def slot($name): if $name == null then null else first(registry::widget($name)) // null end;

((($ENV.COLUMNS // "" | tonumber?) // 120) - 4) as $budget
| . + {git_status: $git, session_pr: ($session_pr | fromjson? // null)}
| . as $session
| ($config[0].statusline.rows? // null | arrays) // $defaults[0].statusline.rows
| [ .[] | [.[] as $name | $session | slot($name)] ]
| render($budget)
