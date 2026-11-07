#!/bin/sh
# Status line: shows how full the context window is and what to do about it.
# Uses Claude Code's own context_window.used_percentage. Local only, no network.
# Also records the percentage for the context-advice hook, so Claude can tell
# you at a natural break.
python3 -c '
import json, os, re, sys, tempfile
d = json.load(sys.stdin)
pct = int(float((d.get("context_window") or {}).get("used_percentage") or 0))
model = (d.get("model") or {}).get("display_name", "")
sid = re.sub(r"[^A-Za-z0-9_-]", "", str(d.get("session_id", "default")))[:64] or "default"
try:
    with open(os.path.join(tempfile.gettempdir(), "affectd-claude-ctx-" + sid), "w") as f:
        f.write(str(pct))
except OSError:
    pass
if pct >= 85:
    advice = "finish this step, then /compact or start fresh"
elif pct >= 60:
    advice = "compact at the next natural break"
else:
    advice = "ok"
print(f"affectd | {model} | context {pct}% | {advice}")
' 2>/dev/null || echo "affectd"
