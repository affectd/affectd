#!/bin/sh
# UserPromptSubmit hook: when context passes 60%, 75% or 85%, tells Claude once
# per threshold so it can advise you at a natural break. Reads the percentage
# the status line recorded. Local only, no network. Prints nothing otherwise.
python3 -c '
import json, os, re, sys, tempfile
d = json.load(sys.stdin)
sid = re.sub(r"[^A-Za-z0-9_-]", "", str(d.get("session_id", "default")))[:64] or "default"
tmp = tempfile.gettempdir()
try:
    pct = int(open(os.path.join(tmp, "affectd-claude-ctx-" + sid)).read().strip())
except (OSError, ValueError):
    sys.exit(0)
marker = os.path.join(tmp, "affectd-claude-ctx-told-" + sid)
try:
    told = int(open(marker).read().strip())
except (OSError, ValueError):
    told = 0
level = max([t for t in (60, 75, 85) if pct >= t], default=0)
if level <= told:
    sys.exit(0)
open(marker, "w").write(str(level))
print(f"Context is {pct}% full. At the next natural break, not mid-step, tell the user in one line which to do: "
      "/compact if the same feature continues (say what the summary must keep, such as the plan and failing tests), "
      "or commit, update docs/roadmap/v0.1.json and start a fresh session if the feature is done, the task is changing, "
      "or the current approach went wrong. Keep working until then.")
' 2>/dev/null
exit 0
