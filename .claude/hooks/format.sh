#!/bin/sh
# Formats the file Claude just edited, so diffs stay clean without spending
# context on formatting. Runs locally and makes no network calls.
# Input: the hook JSON on stdin. Always exits 0: a missing formatter
# must never block work.
file=$(python3 -c "import json,sys; print(json.load(sys.stdin).get(\"tool_input\",{}).get(\"file_path\",\"\"))" 2>/dev/null) || exit 0
case "$file" in
  *.go)    command -v gofmt >/dev/null 2>&1 && gofmt -w "$file" ;;
  *.swift) command -v swift-format >/dev/null 2>&1 && swift-format format --in-place "$file" ;;
esac
exit 0
