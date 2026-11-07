#!/usr/bin/env python3
"""Make changes to existing tests visible to reviewers.

Coding agents that cannot fix the code sometimes edit, skip or delete the
failing test instead; Claude models did this mostly by modifying tests
(ImpossibleBench, ICLR 2026). This lists every such change on a branch so a
reviewer looks at it on purpose. It never fails the build: some test changes
are legitimate, and a human decides.

Usage: scripts/test-integrity.py [base-ref]   (default: origin/main)
"""
import re
import subprocess
import sys

ASSERTION = re.compile(r"\b[tbf]\.(Error|Errorf|Fatal|Fatalf|Fail|FailNow)\b|^\s*func (Test|Fuzz|Benchmark)\w*\(")
SKIP = re.compile(r"\.Skip(Now|f)?\(")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False).stdout


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    merge_base = git("merge-base", base, "HEAD").strip() or base
    notes = []

    for row in git("diff", "--name-status", merge_base, "--", "*_test.go", "testdata").splitlines():
        parts = row.split("\t")
        kind, path = parts[0], parts[-1]
        if kind.startswith("D"):
            notes.append(f"deleted: {path}")
        elif kind.startswith("M") and path.startswith("testdata/") and "golden" in path:
            notes.append(f"golden file changed: {path}")

    current = None
    for line in git("diff", "-U0", merge_base, "--", "*_test.go").splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else line[4:]
        elif line.startswith("-") and not line.startswith("---") and ASSERTION.search(line[1:]):
            notes.append(f"{current}: removed `{line[1:].strip()}`")
        elif line.startswith("+") and not line.startswith("+++") and SKIP.search(line[1:]):
            notes.append(f"{current}: added `{line[1:].strip()}`")

    for note in notes:
        print(f"::warning::Existing test changed, review on purpose: {note}")
    if notes:
        print(f"{len(notes)} change(s) to existing tests need a reviewer's attention.")
    else:
        print("No existing tests were removed, skipped or loosened.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
