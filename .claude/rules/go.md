---
paths:
  - "**/*.go"
---

# Go conventions

Idiomatic Go (Go has no classes; don't imitate them):

- Compose small types; accept the narrowest interface a function needs, defined in the consuming package.
- Make zero values useful, so types need no constructor where possible.
- Name packages for what they provide (`inventory`, `match`), and don't repeat the package name in identifiers (`match.Result`, not `match.MatchResult`). No `Get` prefix on accessors.
- Handle errors first and keep the success path unindented ("line of sight").
- Keep functions short enough to read at a glance; the linter flags high cognitive complexity and duplicated blocks.

Correctness and safety:

- Return errors with context, such as `fmt.Errorf("parse %s: %w", path, err)`. Don't panic outside `main` and tests: a crash stops protection.
- Pass `context.Context` as the first argument to anything that does I/O, so a scan can be cancelled when the user's machine needs the resources back.
- Read user files through `internal/safeio`. Its size limits and symlink checks stop a crafted file from exhausting memory or leading the scanner outside its roots. The linter enforces this.
- Log with `log/slog` attributes. Never log file contents, credential values or whole threat-data records; logs end up in bug reports.

Tests:

- Table-driven, next to the code, with assertions that check the actual values, not only that no error occurred.
- Every parser of user files or threat data gets a fuzz test (`func FuzzXxx`), because those inputs are attacker-written.
- Tests make no network calls and don't depend on wall-clock time or map order; inject clocks and sort results.
- Golden files live in `testdata/` and change only when the output is meant to change; say so in the commit message.

Performance and scale (affectd runs all day on someone else's laptop):

- Add a benchmark (`func BenchmarkXxx` with `b.ReportAllocs()`) before optimising, and compare with `make bench-compare`.
- Stream large files with decoders instead of reading them whole; preallocate slices and maps when the size is known.
- Bound concurrency with `errgroup.Group.SetLimit`, never one goroutine per file.
- Keep lookups O(1) by indexing threat data in maps keyed by ecosystem and name; never scan the whole index per package.
