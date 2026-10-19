#!/bin/bash
# Claude Code's status line. One jq pass renders everything. Git state and the session's PR come
# from caches refreshed in the background, so after the first render nothing waits on git or the network.
# shellcheck source=env.sh
source "${BASH_SOURCE[0]%/*}/env.sh"

IFS= read -r -d '' input
{ IFS= read -r cwd; IFS= read -r session; IFS= read -r transcript; IFS= read -r has_pr; } < <(
  jq -r '.workspace.current_dir // .cwd // "", .session_id // "", .transcript_path // "", (.pr != null)' <<<"$input"
)
cwd="${cwd:-$PWD}"

cache_dir="${TMPDIR:-/tmp}/claude-kit"
[[ -d $cache_dir ]] || mkdir -p "$cache_dir"
git_cache="$cache_dir/git-${cwd//\//%}"
pr_cache="$cache_dir/pr-${session:-none}"
PR_TTL=60s
GIT_TTL_SECONDS=5

refresh_git() {
  git -C "$cwd" --no-optional-locks status --porcelain=v2 --branch >"$git_cache.$$" 2>/dev/null
  mv -f "$git_cache.$$" "$git_cache"
}

# Claude Code reports the PR of the current branch only. A session that opened a PR from another
# worktree stays on its own branch, so the last PR link in its transcript stands in.
refresh_session_pr() {
  [[ -n $session && -f $transcript ]] && command -v gh >/dev/null || return
  [[ -n $(find "$pr_cache" -mtime -"$PR_TTL" 2>/dev/null) ]] && return
  touch "$pr_cache"
  local url
  url="$(tail -c 4000000 "$transcript" | grep -oE 'https://github\.com/[^/"]+/[^/"]+/pull/[0-9]+' | tail -1)"
  [[ -n $url ]] || return
  local partial="$pr_cache.$$"
  if gh pr view "$url" --json number,url,state,isDraft,reviewDecision --jq '
    if .state == "CLOSED" then empty else
      {number, url, review_state: (
        if .state == "MERGED" then "merged" elif .isDraft then "draft"
        else ({APPROVED: "approved", CHANGES_REQUESTED: "changes_requested"}[.reviewDecision] // "pending") end)}
    end' >"$partial" 2>/dev/null; then
    mv -f "$partial" "$pr_cache"
  else
    rm -f "$partial"
  fi
}

git_is_fresh() { (($(date +%s) - $(stat -f %m "$git_cache") < GIT_TTL_SECONDS)); }

refresh() {
  git_is_fresh || refresh_git
  [[ $has_pr == true ]] || refresh_session_pr
}

if [[ -f $git_cache ]]; then
  refresh </dev/null >/dev/null 2>&1 &
else
  refresh_git
fi

session_pr=''
[[ -f $pr_cache ]] && session_pr="$(<"$pr_cache")"

jq -r -L "$kit_root/statusline" -L "$kit_root/widgets" -L "$theme_dir" \
  --arg git "$(<"$git_cache")" --arg session_pr "$session_pr" \
  --slurpfile config "$config" --slurpfile defaults "$kit_root/statusline/defaults.json" \
  -f "$kit_root/statusline/render.jq" <<<"$input"
