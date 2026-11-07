#!/usr/bin/env python3
"""Fail if the repository's Claude Code configuration could run code or leak
credentials on a contributor's machine.

Repository-controlled .claude/settings.json and .mcp.json were used in 2025-2026
for remote code execution (project hooks, MCP auto-approval) and API key theft
(ANTHROPIC_BASE_URL). See CVE-2025-59536 and CVE-2026-21852. This check keeps
those patterns out of affectd's own repository.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Keys that let a repository change credentials, endpoints or MCP approval.
FORBIDDEN_KEYS = {
    "env",
    "apiKeyHelper",
    "awsAuthRefresh",
    "awsCredentialExport",
    "otelHeadersHelper",
    "enableAllProjectMcpServers",
    "enabledMcpjsonServers",
}
NETWORK_TOOLS = re.compile(r"\b(curl|wget|nc|ncat|socat|ssh|scp|rsync)\b|/dev/tcp/")
HOOK_PREFIX = '"$CLAUDE_PROJECT_DIR"/.claude/hooks/'
STATUSLINE_COMMAND = '"$CLAUDE_PROJECT_DIR"/.claude/statusline.sh'


def check_imports(problems):
    """Imports in agent instruction files must be files inside the repository."""
    for name in ("AGENTS.md", "CLAUDE.md"):
        path = ROOT / name
        if not path.is_file():
            continue
        in_fence = False
        for number, line in enumerate(path.read_text().splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            text = re.sub(r"`[^`]*`", "", line)
            for target in re.findall(r"(?:^|\s)@([^\s]+)", text):
                resolved = (ROOT / target).resolve()
                if target.startswith(("/", "~")) or ".." in target or ROOT.resolve() not in resolved.parents or not resolved.is_file():
                    problems.append(f"{name}:{number} imports {target!r}; imports must be files inside the repository")


def main() -> int:
    problems = []
    settings = ROOT / ".claude" / "settings.json"
    if settings.exists():
        text = settings.read_text()
        data = json.loads(text)
        for key in sorted(FORBIDDEN_KEYS & data.keys()):
            problems.append(f".claude/settings.json sets '{key}'")
        if "BASE_URL" in text:
            problems.append(".claude/settings.json mentions a BASE_URL")
        for event, groups in data.get("hooks", {}).items():
            for group in groups:
                for hook in group.get("hooks", []):
                    if hook.get("type") != "command":
                        problems.append(f"{event} hook of type '{hook.get('type')}' needs a maintainer decision")
                        continue
                    command = hook.get("command", "")
                    if not command.startswith(HOOK_PREFIX):
                        problems.append(f"{event} hook must run a reviewed script from .claude/hooks/: {command}")

        status_line = data.get("statusLine")
        if status_line and status_line.get("command") != STATUSLINE_COMMAND:
            problems.append(f"statusLine must run the reviewed .claude/statusline.sh: {status_line.get('command')}")

    scripts = list((ROOT / ".claude").glob("*.sh")) + list((ROOT / ".claude" / "hooks").glob("*"))
    for script in sorted(scripts):
        if script.is_file() and NETWORK_TOOLS.search(script.read_text(errors="ignore")):
            problems.append(f"{script.relative_to(ROOT)} uses a network tool")

    if (ROOT / ".mcp.json").exists():
        problems.append(".mcp.json exists: project MCP servers need both maintainers' decision first")

    check_imports(problems)

    for problem in problems:
        print(f"::error::{problem}")
    if not problems:
        print("Claude Code configuration check passed.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
