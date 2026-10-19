# shellcheck shell=bash
# Sourced by the status line scripts: where the kit, the active theme and the config live.
# CLAUDE_KIT_THEME_DIR points one session at another theme, which is how `kit preview` works.

kit_root="$(cd "${BASH_SOURCE[0]%/*}/.." && pwd)"
kit_user="${CLAUDE_KIT_HOME:-$HOME/.config/claude-kit}"
theme_dir="${CLAUDE_KIT_THEME_DIR:-$kit_user/current}"
config="$kit_user/config.json"
# jq 1.8.2 aborts on modules that load other modules (jqlang/jq#3636), and Homebrew installs it, so
# the status line prefers the jq that macOS ships.
jq_bin=/usr/bin/jq
[[ -x $jq_bin ]] || jq_bin=jq
[[ -f $config ]] || config="$kit_root/statusline/defaults.json"
