#!/usr/bin/env python3
"""Prove that every rule in .golangci.yml rejects a deliberate violation.

Several lint rules enforce AGENTS.md in code (network, processes, file reads,
stdout, panics), and a renamed linter or a loosened path pattern would switch
one off without anyone noticing. testdata/lint/ mirrors the repository layout:
each line that must be rejected ends with `// want: <linter>[, <linter>]`, and
the files without annotations sit where a rule is deliberately allowed.

This copies that tree into a temporary module next to the real .golangci.yml,
runs golangci-lint, and fails if a wanted issue is missing, if any other issue
appears (so path-scoped rules are tested in both directions), or if an enabled
linter or formatter, or a custom rule's message, is never reported. The
fixtures are stored as *.go.txt and become *.go only in the copy: they break
vet and gofmt on purpose, so Go tooling, the editor hooks and the Stop hook
must not see them as code.

Usage: scripts/check-lint-rules.py
"""
import collections
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = ROOT / ".golangci.yml"
FIXTURES = ROOT / "testdata" / "lint"
MODULE = "example.com/lintfixture"
WANT = re.compile(r"//\s*want:\s*(.+?)\s*$")
# The message of each custom forbidigo and depguard rule.
RULE_MESSAGE = re.compile(r'^\s*(?:msg|desc):\s*"(.+)"\s*$', re.MULTILINE)
# The golangci-lint version CI pins, which the expected issues are calibrated to.
PINNED = re.compile(r"golangci-lint-action@\S+.*\n\s+with:\n\s+version:\s*(\S+)")


def golangci(tree, *args):
    # --config is explicit: golangci-lint would otherwise prefer a .golangci.yaml,
    # .json or .toml placed next to .golangci.yml.
    command = ["golangci-lint", *args, "--config", str(tree / ".golangci.yml")]
    return subprocess.run(command, cwd=tree, capture_output=True, text=True, check=False)


def go_version():
    match = re.search(r"^go\s+(\S+)\s*$", (ROOT / "go.mod").read_text(), re.MULTILINE)
    if not match:
        sys.exit("go.mod has no go directive")
    return match.group(1)


def wanted(tree):
    """Return every (file, line, linter) the fixtures say must be reported."""
    want = set()
    for path in sorted(tree.rglob("*.go")):
        name = path.relative_to(tree).as_posix()
        for number, line in enumerate(path.read_text().splitlines(), 1):
            match = WANT.search(line)
            if match:
                want.update((name, number, linter.strip()) for linter in match.group(1).split(","))
    return want


def enabled(tree):
    """Return the linters and formatters the configuration enables."""
    names = set()
    for kind in ("linters", "formatters"):
        result = golangci(tree, kind, "--json")
        if result.returncode != 0:
            sys.exit(f"golangci-lint {kind} failed:\n{result.stderr}")
        names.update(entry["name"] for entry in json.loads(result.stdout)["Enabled"])
    return names


def reported(tree):
    """Run golangci-lint and return every issue as ((file, line, linter), message)."""
    report = tree.parent / "report.json"
    result = golangci(tree, "run", "--output.json.path", str(report), "--issues-exit-code", "0", "./...")
    if result.returncode != 0:
        sys.exit(f"golangci-lint run failed:\n{result.stdout}{result.stderr}")
    issues = json.loads(report.read_text())["Issues"] or []
    return [((i["Pos"]["Filename"], i["Pos"]["Line"], i["FromLinter"]), i["Text"]) for i in issues]


def version_hint():
    installed = subprocess.run(["golangci-lint", "version", "--short"], capture_output=True, text=True, check=False)
    pinned = PINNED.search((ROOT / ".github" / "workflows" / "ci.yml").read_text())
    have = installed.stdout.strip().lstrip("v")
    want = pinned.group(1).lstrip("v") if pinned else "unknown"
    if have != want:
        return f" The fixtures are calibrated to golangci-lint {want}, the version CI pins; you have {have or 'an unknown version'}."
    return ""


def main() -> int:
    if shutil.which("golangci-lint") is None:
        print("golangci-lint is not installed; install the version pinned in .github/workflows/ci.yml", file=sys.stderr)
        return 1
    links = [p.relative_to(ROOT).as_posix() for p in FIXTURES.rglob("*") if p.is_symlink()]
    if links:
        print(f"testdata/lint/ must not contain symlinks: {', '.join(links)}", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as temp:
        tree = pathlib.Path(temp).resolve() / "module"
        shutil.copytree(FIXTURES, tree)
        for path in list(tree.rglob("*.go.txt")):
            path.rename(path.with_suffix(""))
        shutil.copy(CONFIG, tree)
        (tree / "go.mod").write_text(f"module {MODULE}\n\ngo {go_version()}\n")

        want = wanted(tree)
        issues = reported(tree)
        uncovered = enabled(tree) - {linter for _, _, linter in want}

    counts = collections.Counter(key for key, _ in issues)
    messages = "\n".join(text for _, text in issues)
    problems = [f"not rejected: {f}:{n} should be reported by {linter}" for f, n, linter in sorted(want - counts.keys())]
    problems += [f"unexpected: {f}:{n} {linter}: {text}" for (f, n, linter), text in sorted(issues) if (f, n, linter) not in want]
    problems += [f"unexpected: {f}:{n} {linter} reported {c} issues, want 1" for (f, n, linter), c in sorted(counts.items()) if c > 1 and (f, n, linter) in want]
    problems += [f"untested: {linter} is enabled but no fixture violates it" for linter in sorted(uncovered)]
    problems += [f"untested: no fixture triggers the rule {m!r}" for m in RULE_MESSAGE.findall(CONFIG.read_text()) if m not in messages]
    for problem in problems:
        print(problem)
    if problems:
        print(f"{len(problems)} lint rule problem(s); fixtures are in testdata/lint/.{version_hint()}")
        return 1
    print(f"Every lint rule rejected its violations ({len(issues)} issues) and allowed paths stayed quiet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
