# shellcheck shell=bash
# Sourced by the status line scripts: where the kit, the active theme and the config live.
# CLAUDE_KIT_THEME_DIR points one session at another theme, which is how `kit preview` works.

kit_root="$(cd "${BASH_SOURCE[0]%/*}/.." && pwd)"
kit_user="${CLAUDE_KIT_HOME:-$HOME/.config/claude-kit}"
theme_dir="${CLAUDE_KIT_THEME_DIR:-$kit_user/current}"
config="$kit_user/config.json"
[[ -f $config ]] || config="$kit_root/statusline/defaults.json"
