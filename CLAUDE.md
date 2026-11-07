@AGENTS.md

## Claude Code

- For changes across packages, use plan mode and wait for approval before editing.
- Implement roadmap features with `/feature`. It runs the design step, tests first, benchmarks and the reviews.
- Reviews run in fresh contexts: `/code-review` for bugs, the `quality-reviewer` subagent for design, duplication and performance, and the `security-reviewer` subagent for the threat model.
- When the context note appears or a feature is finished, tell the user in one line whether to `/compact` (the same feature continues) or start a fresh session (the feature is done, the task is changing, or the approach went wrong).
- Rules in `.claude/rules/` load automatically when you open matching files.
