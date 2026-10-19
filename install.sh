#!/bin/bash
# Checks what claude-kit needs from macOS, then starts the guided setup.
# Usage: ./install.sh          guided setup, nothing changes until you confirm
#        ./install.sh --help   every command, including non-interactive ones for scripts and agents
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

missing() {
  printf '\033[1;31m✗\033[0m %s\n  %s\n' "$1" "$2" >&2
  exit 1
}

[[ $(uname -s) == Darwin ]] || missing "claude-kit runs on macOS." "The status line works elsewhere, but fonts and iTerm2 profiles are macOS only."
xcode-select -p >/dev/null 2>&1 || missing "Apple's command line tools are not installed." "Run: xcode-select --install, then run this script again."
command -v jq >/dev/null || missing "jq is not installed." "Run: brew install jq (macOS 15 and later include it)."
command -v claude >/dev/null || missing "Claude Code is not installed." "See https://docs.claude.com/en/docs/claude-code/setup, then run this script again."

if [[ $# -eq 0 ]]; then
  exec "$root/bin/kit" setup
fi
exec "$root/bin/kit" "$@"
