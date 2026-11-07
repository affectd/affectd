# Agent guidance

This file is for coding agents working in this repository. Human contributors should start with CONTRIBUTING.md; the rules here are the same.

affectd detects supply-chain attacks on developer machines. It inventories installed packages, editor extensions and MCP servers, matches them against a signed threat-data file, and tells the user what happened and what to do. Everything runs on the user's own machine; the project hosts no servers.

## Commands

- `make check`: formatting, vet, lint (`.golangci.yml`), tests with the race detector, and `govulncheck`. Run it before you call a task done.
- `go test ./internal/<pkg>/...`: the fast loop while working on one package.
- `make bench` then `make bench-compare`: benchmarks compared with `benchstat` against a saved baseline. Required for changes to matching, inventory or data loading.
- `make fuzz`: every fuzz target for 30 seconds each.
- `go test -run TestReplay ./internal/replay/...`: replays of real past attacks against fake machines.
- `make proto`: regenerate code after editing the local API schema in `proto/`.

Rules for the macOS app, CI workflows, campaign packs and the API schema are in `.claude/rules/`. Read the matching file before working in those areas.

## Layout

- `cmd/affectd/`: the single binary, both the command-line tool and the background service
- `internal/inventory/`: wraps OSV-SCALIBR; new ecosystems are extractors here, never special cases in matching
- `internal/match/`: matches the inventory against threat data; deterministic
- `internal/data/`: downloads and verifies the signed data file
- `internal/safeio/`: size-limited, symlink-aware file reading for everything that scans user files
- `internal/api/`: the local API used by the apps and the MCP connector
- `proto/`: the local API schema
- `campaigns/`: campaign packs (descriptions of known attacks)
- `apps/macos/`: the Swift menu-bar app
- `testdata/fixtures/`: synthetic "fake machines"; never real malware or real credentials
- `docs/roadmap/v0.1.json`: the feature list and what is verified as done
- `docs/decisions/`: decisions already made and why. Read the relevant record before proposing a change to a settled choice, and propose a new record instead of working around one.

## How we work

- Choose the approach before writing code. For anything beyond a small fix, outline two or three genuinely different approaches (different algorithms, data structures or designs, not variations of one), compare them on correctness, speed and memory at affectd's scale, simplicity and security, and pick the best, saying why in one sentence. Then list the edge cases and failure paths it must handle, so nothing is left out. For changes across packages, write the plan down and get it approved before editing.
- Work on one roadmap feature at a time. A feature is done when its acceptance test exists and `make check` passes; only then set its `"passes"` to `true`. Never change a feature's description or acceptance criteria to make it pass.
- Every detection change ships with a fixture in `testdata/fixtures/` that proves it fires, and stays quiet on `testdata/fixtures/clean/`.
- Build the simplest solution that is complete and correct for every valid input, not just the test cases; tests verify correctness, they don't define the solution. Simplicity is about structure: never cut correctness, validation at trust boundaries, tests or the performance budgets to make code shorter. Don't add options, abstractions or dependencies the task didn't ask for.
- Finish the whole task: no placeholders, TODOs, stubbed branches, mock implementations or quietly simplified versions. If the work is bigger than expected, say so and propose how to split it rather than cutting scope. Context is compacted automatically, so don't rush or stop early because a session is long; record progress and continue.
- When a requirement is ambiguous, or a choice is hard to reverse (data formats, the local API, dependencies, concurrency design), present the options with their trade-offs and ask before building.
- If a test looks wrong, stop and explain why instead of changing it. Never delete, skip or loosen an existing test, or special-case inputs, to make a change pass; a passing test that proves nothing hides real bugs from users.
- Measure before optimising, and show the `benchstat` result for any change that claims to be faster. Hot paths keep allocations low and stream large files rather than loading them whole.
- Sign off every commit with `git commit -s`; the DCO check rejects commits without it. Don't credit the AI tool in a commit: no `Co-Authored-By:` line naming the agent and no `Assisted-by:` trailer.

## Design

Write code the way experienced Go engineers do, following Effective Go and Google's Go Style Guide. When goals conflict, prefer, in order: clarity, simplicity, concision, maintainability, consistency with the existing code.

These are the specific patterns that make code harder to change; don't introduce them:

- An interface with one implementation and no test that needs it. Define interfaces where they are used, and return concrete types.
- Helpers, wrappers or packages for a one-time operation, and catch-all packages such as `util`, `common` or `helpers`.
- Manager, factory or service types that only forward calls; getters and setters; class hierarchies imitated with embedding.
- Options, flags or extension points no current feature needs.
- Defensive checks for states that can't occur inside a package. Validate at trust boundaries instead: scanned files, threat data, the local API and command-line input.
- Duplicated logic. Search for an existing function before writing one, and when you would copy a block, extract it instead.
- Comments that restate the code. Explain why, and document every exported identifier.

## Rules that protect users

Each rule exists because breaking it would turn affectd into an attack vector.

- Detection is deterministic. AI features may explain a finding or raise concern, but no code path may let a model clear, downgrade or hide a finding, because attackers now plant text aimed at AI tools.
- Record where credentials live, never their values. The one exception is the user-confirmed GitHub token revocation in `internal/respond/`.
- Treat every scanned file and every threat-data field as attacker-written: read it through `internal/safeio`, never execute or interpret it, and strip control and invisible Unicode characters before display.
- The engine makes no network calls except the data-file fetcher in `internal/data/` and the user-configured AI provider client. No telemetry.
- affectd runs as the logged-in user. Never require root or administrator rights.
- Log with structured `slog` attributes, never by building a message from untrusted text, so attacker-written names can't forge log lines.
- A new Go dependency needs a one-line justification in the pull request; prefer the standard library and OSV-SCALIBR. Confirm the module really exists and is the intended one before adding it, because AI tools sometimes invent package names that attackers then register.
- Changes to `.claude/`, `AGENTS.md`, `CLAUDE.md`, `.mcp.json` and `.github/` need the other maintainer's review, because they run on contributors' machines or publish releases.

## Test data

- Fixtures use obviously fake secrets such as `FAKE-npm-token-0000`. Never copy a real token, key or file from your own machine into the repository.
- Real malware samples are never opened or stored in this repository.
