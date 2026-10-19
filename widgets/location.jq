# The theme icon, the repository name, and the folder inside it when you are deeper.

include "palette";
include "grid";

def widget:
  (.workspace.project_dir // .workspace.current_dir // .cwd) as $root
  | (.workspace.current_dir // .cwd) as $cur
  | (.workspace.repo.name // ($root | split("/") | last)) as $name
  | maybe($cur != $root and ($cur | startswith($root + "/")); "/" + ($cur | ltrimstr($root + "/"))) as $sub
  | cell(
      (icon + " " + paint(bold(brand); $name) + detail($sub) | variant(40)),
      (icon + " " + paint(bold(brand); $name) | variant(88)),
      (icon + " " + paint(bold(brand); $name | clip(14)) | variant(0)));
