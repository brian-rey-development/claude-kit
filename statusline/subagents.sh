#!/bin/bash
# One row per subagent in Claude Code's agent panel, in the theme's colors.
# shellcheck source=env.sh
source "${BASH_SOURCE[0]%/*}/env.sh"
exec jq -c -L "$kit_root/statusline" -L "$theme_dir" -f "$kit_root/statusline/subagents.jq"
