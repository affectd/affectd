# affectd CI

affectd's pipeline is held to a higher standard than most projects, because a security tool's own build is a prime target: Trivy was compromised through its CI twice, and in March 2025 attackers moved the version tags of `tj-actions/changed-files` to a malicious commit across more than 23,000 repositories. Every workflow passes actionlint and zizmor with no findings, even in zizmor's strictest auditor mode.

## Workflows

| Workflow | Runs | What it does |
| --- | --- | --- |
| `ci.yml` | Every pull request and push to main | Lint, tests on Linux, macOS and Windows (with the race detector on Linux and macOS), govulncheck, fuzz smoke tests, test integrity, benchmark comparison, a release test-build, the macOS app, and a check that each lint rule still rejects a deliberate violation. affectd starts scanning its own repository once `affectd scan` exists (F13). One aggregate job, **CI passed**, is the status check branch protection requires. |
| `security.yml` | Every pull request | Dependency review (vulnerabilities and licences of new dependencies), zizmor workflow audit, OSV-Scanner. |
| `codeql.yml` | Pull requests, main, weekly | CodeQL with the security-and-quality queries. |
| `scorecard.yml` | Main, weekly | OpenSSF Scorecard, published for the README badge. |
| `weekly.yml` | Weekly | Mutation testing, ten-minute fuzzing per target, full OSV-Scanner run. |
| `claude-config.yml` | Changes to Claude Code files | Blocks configuration that could run code or leak credentials. |
| `release.yml` | A `v*` tag, after the other maintainer approves | Reproducible GoReleaser build, SBOMs, keyless Cosign signature, SLSA provenance, draft-then-publish into an immutable release, Homebrew tap pull request. Network locked to the hosts a release needs. |
| `verify-release.yml` | Every published release | Downloads the release and verifies checksums, signature and provenance the way a user would. |
| `data-watch.yml` | Every three hours | Checks the threat data is recent and correctly signed; opens one issue if not. |

`docs/ci/data-build.yml` is the template for the data repository's hourly build.

## Hardening applied to every workflow

- Every action pinned to a full commit SHA of a release at least 14 days old (tj-actions moved tags; pinned workflows were unaffected).
- `permissions: {}` at the top; each job gets only what it needs, with a comment.
- harden-runner on every Linux job: audit mode for checks, a blocking allowlist for release and data jobs. It is how the tj-actions compromise was detected.
- `persist-credentials: false` on every checkout; no Go cache in release or data builds.
- No `pull_request_target`, no long-lived tokens: OIDC for signing, and a GitHub App token scoped to the tap repository.
- Untrusted values reach shell scripts only through `env:`.

## Bots

| Bot | Decision | Why |
| --- | --- | --- |
| Dependabot | Install | Updates Go modules and pinned action SHAs; the 14-day cooldown applies the release-age rule automatically. |
| CodeQL and secret scanning | Enable | Free for public repositories; push protection blocks committed secrets. |
| OpenSSF Scorecard | Install (workflow) | Used by all five OpenSSF projects compared below. |
| OpenSSF Allstar | Install on the org | Continuously enforces branch protection, SECURITY.md, outside-collaborator rules, binary artifacts and dangerous workflows, and catches someone briefly disabling protection. Policies are in `docs/ci/allstar/`. |
| DCO | Install | Checks every commit's sign-off, as Linux Foundation projects do. |
| Renovate | Skip | Dependabot covers Go and actions natively; two update bots would conflict. |
| Codecov | Skip | Adds an external upload and token; mutation testing measures test strength better. |
| Stale bot | Skip | Auto-closing issues discourages new contributors to a young project. |
| Auto-merge bots | Skip | They would bypass the two-person rule. |
| AI agents in CI (Claude Code Action and similar) | Skip for now | In 2026, PR titles and issue comments were used to make AI agents in GitHub Actions leak secrets, including Anthropic's Claude Code Security Review action. affectd's CI handles attacker-written text constantly. Claude reviews run in maintainers' local sessions instead. |

## Custom bots

Build them as workflows, not a GitHub App: an App is a long-lived credential across repositories, while a workflow runs with a short-lived, minimal token. There are four:

1. The self-scan, added to `ci.yml` with `affectd scan` (F13), runs affectd against its own repository on every pull request, the way gittuf verifies its own repository with gittuf.
2. `verify-release.yml` checks every published release the way a user would. Cosign's `validate-release` test-builds releases on pull requests; affectd does that too and then also verifies what it published.
3. `data-watch.yml` checks the threat data from outside the data repository, so a broken pipeline can't silence its own alarm.
4. `scripts/test-integrity.py`, `scripts/check-claude-config.py` and `scripts/check-lint-rules.py` guard the tests, the Claude Code configuration and the lint rules.

## Compared with OpenSSF projects

Checked 6 November 2026 from each project's `.github/workflows`.

| Practice | cosign | scorecard | gittuf | guac | slsa-verifier | affectd |
| --- | --- | --- | --- | --- | --- | --- |
| Scorecard | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| CodeQL | ✓ | ✓ | ✓ | | ✓ | ✓ |
| Dependency review | ✓ | ✓ | | | ✓ | ✓ |
| zizmor | | | ✓ | | | ✓ (auditor, zero findings) |
| harden-runner | | some jobs | | | | every Linux job; blocking for releases |
| Actions pinned by SHA | most | most | all | most | most | all, at least 14 days old |
| Release test-built on pull requests | ✓ | | | | | ✓ |
| Published releases verified like a user | | | | | | ✓ |
| Verifies itself with its own tool | | | ✓ | | | from F13 |
| Reproducible build settings | ✓ | ✓ | ✓ | | n/a (other builder) | ✓ (tested) |

## Verification performed

Last run on 18 November 2026, for F01.

- actionlint 1.7.12 and the official workflow and Dependabot schemas: no problems.
- zizmor 1.31.1 (the version CI runs) and 1.32.0, auditor persona: no findings. The first audit found one real issue (an over-privileged GitHub App token) and missing names, concurrency limits and permission comments, all fixed. CI runs zizmor in the auditor persona with its online audits.
- Every pinned action SHA matches its release tag, and every release is at least 14 days old.
- GoReleaser 2.19.0: `goreleaser check` passes. Two snapshot builds from the same commit, the second after touching every file, produced identical checksums for all six archives, and the binary reports the version set at build time. The first attempt, during setup, did not: archive timestamps differed until they were fixed to the commit date.
- `scripts/check-lint-rules.py` was tested against deliberately weakened configurations. It fails when an exclusion is unanchored or lifts more than its own rule, when a depguard exception is widened or matches nested packages, when a code-generation header or an import alias hides a violation, and when a linter or custom rule has no violation fixture. Building it found four holes, now fixed: `path: cmd/` also exempted packages such as `internal/subcmd/`; the safeio exclusion lifted every forbidigo rule there, including `panic`; depguard's exceptions matched nested packages at any depth; and a `Code generated … DO NOT EDIT.` header switched every rule off.
- golangci-lint always gets `--config .golangci.yml`, because it would otherwise prefer a `.golangci.yaml`, `.json` or `.toml` added next to it.

## One-time GitHub setup

1. Settings → General: enable **immutable releases**.
2. Settings → Environments: create `release`, require the other maintainer as reviewer, and allow only `v*` tags.
3. Settings → Rules: protect `main` with the four required checks in `docs/ci/allstar/branch_protection.yaml`, signed-off commits, and code-owner review.
4. Settings → Code security: enable CodeQL, secret scanning with push protection, Dependabot alerts and security updates, and private vulnerability reporting.
5. Install the Allstar and DCO GitHub Apps; copy `docs/ci/allstar/` into the org's `.allstar` repository.
6. Create a GitHub App with contents and pull-request write access to `homebrew-tap` only; store its ID as the `TAP_APP_ID` variable and its key as the `TAP_APP_PRIVATE_KEY` secret.
7. Create the `data-watch` issue label.
