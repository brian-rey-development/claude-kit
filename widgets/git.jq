# Branch, commits ahead and behind, staged, changed and untracked files, and the PR with its review state.

include "palette";
include "grid";

def parse_status:
  reduce (split("\n")[] | select(length > 0)) as $l (
    {head: null, oid: "", ahead: 0, behind: 0, staged: 0, modified: 0, untracked: 0, conflicts: 0};
    ($l[0:2]) as $kind
    | if $l | startswith("# branch.head ") then .head = $l[14:]
      elif $l | startswith("# branch.oid ") then .oid = $l[13:20]
      elif $l | startswith("# branch.ab ") then
        ($l[12:] | split(" ") | map(.[1:] | tonumber)) as [$a, $b] | .ahead = $a | .behind = $b
      elif $kind == "1 " or $kind == "2 " then
        .staged += (if $l[2:3] != "." then 1 else 0 end)
        | .modified += (if $l[3:4] != "." then 1 else 0 end)
      elif $kind == "u " then .conflicts += 1
      elif $kind == "? " then .untracked += 1
      else . end
  );

def counts($g):
  [ when($g.ahead > 0; paint(accent_soft; "↑\($g.ahead)")),
    when($g.behind > 0; paint(danger; "↓\($g.behind)")),
    when($g.staged > 0; paint(accent_soft; "+\($g.staged)")),
    when($g.modified > 0; paint(warn; "~\($g.modified)")),
    when($g.untracked > 0; detail("?\($g.untracked)"))
  ] | join(" ");

def pr_label($pr):
  if $pr == null or $pr.number == null then {full: "", short: ""}
  else
    ({approved: accent, changes_requested: danger, merged: merged}[$pr.review_state // ""] // warn) as $color
    | {full: ("  " + paint($color; link($pr.url; "PR #\($pr.number)"))),
       short: ("  " + paint($color; link($pr.url; "#\($pr.number)")))}
  end;

def widget:
  (.pr // .session_pr) as $pr
  | (.git_status // "" | parse_status) as $g
  | pr_label($pr) as $p
  | when($g.head != null;
      (if $g.head == "(detached)" then $g.oid else $g.head end) as $branch
      | maybe($g.conflicts > 0; paint(bold(danger); " !\($g.conflicts)")) as $conflicts
      | maybe($g.staged + $g.modified + $g.untracked > 0; paint(warn; " ●")) as $dirty
      | counts($g) as $counts
      | (paint(bold(accent); $branch) + $conflicts) as $head
      | cell(
          ($head + maybe($counts != ""; "  " + $counts) + $p.full | variant(55)),
          ($head + maybe($counts != ""; "  " + $counts) + $p.short | variant(62)),
          ($head + $dirty + $p.short | variant(78)),
          (paint(bold(accent); $branch | clip(18)) + $conflicts + $dirty | variant(0))));
