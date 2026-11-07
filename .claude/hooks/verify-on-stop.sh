#!/bin/sh
# Stop hook: before Claude finishes, vet and test the Go packages it changed.
# If they fail, exit 2 so Claude sees the output and keeps working.
# Gates once per stop: if Claude is already continuing because of this hook,
# let it stop instead of looping. Offline: modules come from the local cache.
input=$(cat)
active=$(printf '%s' "$input" | python3 -c 'import json,sys; print(str(json.load(sys.stdin).get("stop_hook_active", False)).lower())' 2>/dev/null)
[ "$active" = "true" ] && exit 0
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
command -v go >/dev/null 2>&1 || exit 0

dirs=$( { git diff --name-only HEAD -- '*.go'; git ls-files --others --exclude-standard -- '*.go'; } 2>/dev/null \
  | while read -r f; do dirname "$f"; done | sort -u)
pkgs=""
for d in $dirs; do
  [ -d "$d" ] && pkgs="$pkgs ./$d"
done
[ -z "$pkgs" ] && exit 0

export GOPROXY=off GOFLAGS=-mod=readonly
if ! out=$(go vet $pkgs 2>&1 && go test -race -count=1 -timeout 120s $pkgs 2>&1); then
  printf 'Changed packages fail vet or tests. Fix the cause before finishing; do not edit, skip or loosen tests to pass:\n%s\n' \
    "$(printf '%s\n' "$out" | tail -n 40)" >&2
  exit 2
fi
exit 0
