# Every widget by the name a layout uses. A new widget is a file in this folder plus two lines here.

import "location" as location;
import "git" as git;
import "model" as model;
import "context" as context;
import "limit_5h" as limit_5h;
import "limit_week" as limit_week;
import "clock" as clock;

def widget($name):
  if $name == "location" then location::widget
  elif $name == "git" then git::widget
  elif $name == "model" then model::widget
  elif $name == "context" then context::widget
  elif $name == "limit_5h" then limit_5h::widget
  elif $name == "limit_week" then limit_week::widget
  elif $name == "clock" then clock::widget
  else empty end;
