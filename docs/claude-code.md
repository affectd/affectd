# How affectd uses Claude Code

This setup follows Anthropic's Claude Code documentation and two 2026 studies of repository instruction files. Its guiding constraint: Claude's context window fills up fast and performance drops as it fills, so every line that loads must earn its place.

## Who writes the code

The main Claude Code session writes all code: the conversation you work in, directly or through `/feature`. Subagents never write code here. Reviews run in fresh contexts, because a reviewer that didn't write the code isn't biased toward it: the bundled `/code-review` skill checks for bugs, the `quality-reviewer` subagent checks design, duplication, performance and tests, and the `security-reviewer` subagent checks the threat model. For large changes, the other maintainer reviews the pull request in their own session too.

## The quality system

Anthropic's June 2026 study of about 400,000 Claude Code sessions found verification, not code generation, is now the bottleneck. So every quality goal is a check Claude can run, enforced by tools rather than by instructions:

| Goal | Check | Why (evidence) |
| --- | --- | --- |
| Correct | Test first; `make check`; Stop hook re-tests changed packages before Claude can finish | Claude stops when work *looks* done unless it has a check to run (Claude Code best practices) |
| Honest tests | `scripts/test-integrity.py` flags deleted, skipped or loosened tests; reviewers treat them as blocking | Agents edit failing tests instead of fixing code; for Claude models, mostly by modifying the tests (ImpossibleBench, ICLR 2026) |
| Strong tests | Fuzz tests for parsers; weekly mutation testing on critical packages | 100% line coverage can still mean a 4% mutation score (MutGen, 2025); Meta found mutation-guided tests that coverage would have discarded (ACH, FSE 2025) |
| Safe | `.golangci.yml` enforces CLAUDE.md rules in code (network, processes, file reads, panics) plus `gosec`; `govulncheck`; two fresh-context reviews | About a quarter of security-sensitive tasks still fail even for the best 2026 models (Veracode, October 2026) |
| Fast | Benchmarks with `b.ReportAllocs()`; `benchstat` comparison on every pull request; budgets in `.claude/rules/matching.md` | Correct AI code averaged 3.12 times slower than the best human solutions, and correctness didn't predict efficiency (EffiBench, NeurIPS 2024) |
| Clean and simple | Smallest change that works; the `/code-review` pass flags unneeded complexity | Current models tend to over-engineer when not told otherwise (Anthropic prompting guide) |

## Judging Claude's output

Accept work on evidence, never because it is the first draft, or the fifth.

- Don't accept unverified output. Agents stop early, skip checks or mis-check their own work: in a NeurIPS 2025 study of 1,642 agent runs, verification and termination problems were 23.5% of failures, and adding a check against the task objective raised success by 15.6%. In this setup the evidence is the acceptance test, `make check`, the benchmarks, the three reviews, and your own read of the diff.
- Don't iterate blindly either. Asking for repeated "improvements" without human review increased critical vulnerabilities by 37.6% after five rounds (IEEE ISTAS 2025). Iterate on a specific finding (a failing test, a reviewer's must-fix, a benchmark miss), never "make it better".
- Own the plan. Anthropic's 2026 study of about 400,000 sessions found expertise was the strongest predictor of verified success. Approve plans and decisions that are hard to reverse yourself; that is where your judgement matters most.
- Restart rather than argue. After two failed corrections on the same problem, run `/clear` and start again with a better prompt that includes what you learned. Errors left in context make further errors more likely.
- Keep the default effort (medium) for implementation, which on Claude Opus 5.5 matches or beats the previous model at high. Raise it to high for planning core designs such as the data format, the local API, the matcher and concurrency. Anthropic advises reserving the highest levels for work where you have measured a gain.

## Context: when to compact or start fresh

Claude's performance drops as the context window fills (Claude Code best practices). The status line shows Claude Code's own `used_percentage` with advice, and a hook tells Claude once each time context passes 60%, 75% and 85%, so it can advise you at a natural break instead of mid-step. The thresholds are judgement calls, not measured cut-offs; adjust them if they fire too early or late.

| Situation | Do |
| --- | --- |
| The same feature continues and the plan still matters | `/compact`, telling it what to keep (the plan, failing tests, decisions) |
| The feature is finished, or you're switching tasks | Commit, update `docs/roadmap/v0.1.json`, start a fresh session |
| Two failed corrections, or the approach went wrong | Fresh session with a better prompt; errors left in context make more errors likely |

Fresh sessions lose nothing important here: the plan lives in the feature list and the work in git, and Anthropic notes current Claude models are very good at rediscovering state from the file system.

## Getting the best plan the first time

When you ask "is there a faster way?" and Claude finds one, you are adding the variety of ideas it lacked. PlanSearch (ICLR 2025) found that models keep producing similar ideas, that whether code succeeds is largely decided by the plan behind it, and that exploring genuinely different plans before coding lifted Claude 3.5 Sonnet from 41.4% to 77% on LiveCodeBench. So CLAUDE.md and `/feature` require comparing two or three different approaches on correctness, speed, memory, simplicity and security before writing code, and listing the edge cases first so nothing is left out. Comparing plans is cheap; repeatedly rewriting finished code is costly and can degrade security. For core designs, also raise effort to high, as Anthropic advises when reasoning looks shallow.

## Balancing "too much" against "too little"

| Risk | What guards against it |
| --- | --- |
| Over-engineering | Named anti-patterns in CLAUDE.md; `quality-reviewer` simplicity check; linters for duplication and complexity; reviewers report only problems with a concrete cost; one review round |
| Shortcuts and incomplete work | "Finish the whole task" rule; `godox` rejects TODO and FIXME; acceptance tests; Stop hook; test-integrity check; `quality-reviewer` completeness check |
| Wrong approach chosen | Plan mode for multi-package changes; options with trade-offs for hard-to-reverse choices; your approval |
| Stopping because a session is long | Context is compacted automatically, the feature list records progress, and CLAUDE.md says to continue rather than rush |

## Design principles: named patterns, not acronyms

KISS, YAGNI and DRY are in CLAUDE.md as the specific patterns they rule out, not as acronyms. Three findings drove this:

- Vague aspirations such as "keep it simple" add nothing: the model already believes it is doing that. Anthropic's guidance on over-engineering lists concrete rules instead, such as not creating helpers for one-time operations.
- Claude Opus 5.5 responds well to instructions that name specific patterns to avoid, while a general instruction mostly swaps one default for another (Anthropic, Prompting Claude Opus 5.5).
- Classic OOP doesn't fit Go, which has no classes. Google's Go Style Guide ranks clarity, simplicity, concision, maintainability and consistency, and warns that abstractions such as interfaces must earn their cost. The rules follow that, and the Swift rule follows Swift's own API Design Guidelines.

Duplication gets special attention: across 211 million changed lines, GitClear found refactored code fell from 24.8% to 9.5% of changes between 2021 and 2024 while copy-pasted code rose, with an eightfold rise in duplicated blocks in 2024.

The same named patterns appear in CLAUDE.md, in the `quality-reviewer`, and, where they can be measured, in `.golangci.yml` (`dupl`, `gocognit`, `gocritic`, `revive`, `unparam`, `perfsprint`). The writer and the reviewer apply one standard, and the linter enforces the measurable part.

## OpenSSF quality checks

| OpenSSF expectation | Where it is met |
| --- | --- |
| Code review on every change | Branch protection plus CODEOWNERS; three fresh-context AI reviews before each pull request |
| Tests and CI | `make check` in CI; test-first features; Stop hook |
| Static analysis (SAST) | golangci-lint with `gosec`; CodeQL with the security-and-quality queries |
| Fuzzing | Native Go fuzz tests for every parser; fuzz smoke test in CI |
| Pinned dependencies and least-privilege tokens | Actions pinned by SHA with Dependabot updates; explicit `permissions:`; go.mod tools |
| Known vulnerabilities | `govulncheck` in `make check` |
| Measured continuously | OpenSSF Scorecard workflow, publishing results for the README badge |

## What is here and why

| File | Loads | Purpose |
| --- | --- | --- |
| `AGENTS.md` | Every session, for any AI tool | Commands, layout, how we work, design rules and the rules that protect users. Shared with Copilot, Codex, Cursor and other agents, as in Scorecard and Cosign. |
| `CLAUDE.md` | Every Claude Code session | Imports `AGENTS.md`, then adds the Claude Code workflow: plan mode, `/feature`, the reviewers and context advice. |
| `.claude/rules/*.md` | Only when Claude opens matching files | Go, matching, campaign packs, CI, the macOS app and the API schema. |
| `.claude/settings.json` | Enforced by Claude Code | Allowed commands, prompts before pushes and CI edits, blocked reads of credential files, bypass mode disabled, a formatting hook, and the Stop hook that re-tests changed packages. |
| `.claude/statusline.sh`, `.claude/hooks/context-advice.sh` | Always visible; hook on each prompt | Context percentage with advice; tells Claude when to recommend `/compact` or a fresh session. |
| `Makefile`, `.golangci.yml` | Run by Claude, the Stop hook and CI | The quality gates. Protected by CODEOWNERS, since weakening them would be the easy way to pass. |
| `.claude/agents/quality-reviewer.md` | When asked, in its own context | Read-only review of design, duplication, idiom, performance and test quality. |
| `.claude/agents/security-reviewer.md` | When asked, in its own context | Read-only review against affectd's threat model. |
| `.claude/skills/feature/` | When you type `/feature` | One verified roadmap feature per session. |
| `.claude/skills/add-campaign-pack/` | When you type `/add-campaign-pack` | A sourced campaign pack with its replay fixture. |
| `docs/roadmap/v0.1.json` | Read by `/feature` | What is verified as done. Only the `passes` field changes. |
| `scripts/check-claude-config.py` | In CI | Blocks the configuration patterns used in the 2025-2026 Claude Code attacks. |
| `scripts/test-integrity.py` | In CI and in reviews | Lists every removed, skipped or loosened test on a branch. |
| `.github/workflows/`, `.goreleaser.yaml` | In CI | The CI system; see `docs/ci.md` for every workflow, bot and decision. |
| `.github/dependabot.yml` | Weekly | Keeps Go modules and pinned action SHAs current. |

Deliberately absent: `.mcp.json` (the `gh` command-line tool covers GitHub more cheaply, and repository MCP servers were an attack vector), output styles, and extra subagents. Add them only when a trigger below appears.

## Grow it from friction, not up front

| When this happens | Do this |
| --- | --- |
| Claude gets a command or convention wrong twice | Add one line to `CLAUDE.md`, or to a rule if it only matters for some files |
| You paste the same procedure into chat a third time | Make it a skill |
| A side task floods the conversation with output | Route it through a subagent |
| Something must happen every time, without exceptions | Write a hook or a CI check, not a sentence |

Never commit an unedited `/init` draft. A 2026 ETH Zurich study found that LLM-generated instruction files slightly lowered task success and raised cost by over 20%, while focused human-written files helped.

## Writing instructions that work

- Say what to do, plainly, and explain why. Current Claude models follow instructions closely, so "CRITICAL" and "YOU MUST" cause over-triggering rather than better compliance.
- Every line must be true. Agents follow these files faithfully, so a stale command or wrong path does real damage.
- For each line, ask: would removing this cause a mistake? If not, cut it.
- Once a month, run `/context` to see what loads, and `/doctor` for trim suggestions on `CLAUDE.md`.

## Security of this folder

- `.claude/settings.json` hooks run on every contributor's machine, so `.claude/`, `CLAUDE.md`, `.mcp.json` and `.github/` need both maintainers' review (see `.github/CODEOWNERS`).
- CI rejects `env`, credential helpers, MCP auto-approval, any `BASE_URL`, hooks outside `.claude/hooks/`, and hook scripts that use network tools.
- Never open a real malware sample in a Claude Code session: its text can contain instructions aimed at AI tools.

## Recommended personal setup (not committed)

- Keep Claude Code up to date. The project-file vulnerabilities above were fixed in versions 1.0.87, 1.0.111 and 2.0.65.
- Turn on the sandbox with `/sandbox`. Permission rules match command text; the sandbox enforces file and network limits at the operating-system level.
- Install the Go code-intelligence plugin, so Claude finds code by symbol instead of reading whole files.
- Before running `claude -p` in a repository you don't trust, pass `--setting-sources user` so its settings and hooks don't load.
