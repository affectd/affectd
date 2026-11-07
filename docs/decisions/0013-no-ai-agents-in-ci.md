# 0013. No AI agents in CI

Status: Accepted, 6 November 2026

## Context

In 2026, researchers showed that pull request titles and issue comments could make AI agents running in GitHub Actions leak secrets, including Anthropic's own Claude Code security review action. affectd's CI constantly handles attacker-written text.

## Decision

No AI agent runs automatically in CI. Claude Code reviews run in maintainers' local sessions, through the reviewers in `.claude/agents/`.

## Consequences

No CI secret can be stolen through prompt injection. Contributors don't get automatic AI review on their pull requests; maintainers review instead.

## Alternatives considered

- Claude Code GitHub Action with restricted tools: automatic reviews, but still exposed to text the attacker controls.
