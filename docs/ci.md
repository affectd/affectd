# affectd CI

affectd's pipeline is held to a higher standard than most projects, because a security tool's own build is a prime target: Trivy was compromised through its CI twice, and in March 2025 attackers moved the version tags of `tj-actions/changed-files` to a malicious commit across more than 23,000 repositories. Every workflow passes actionlint and zizmor with no findings, even in zizmor's strictest auditor mode.

## Workflows

| Workflow | Runs | What it does |
| --- | --- | --- |
| `ci.yml` | Every pull request and push to main | Lint, tests with the race detector on Linux, macOS and Windows, govulncheck, fuzz smoke tests, test integrity, benchmark comparison, a release test-build, the macOS app, and affectd scanning its own repository. One aggregate job, **CI passed**, is the status check branch protection requires. |
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

Build them as workflows, not a GitHub App: an App is a long-lived credential across repositories, while a workflow runs with a short-lived, minimal token. Four exist:

1. The self-scan in `ci.yml` runs affectd against its own repository on every pull request, the way gittuf verifies its own repository with gittuf.
2. `verify-release.yml` checks every published release the way a user would. Cosign's `validate-release` test-builds releases on pull requests; affectd does that too and then also verifies what it published.
3. `data-watch.yml` checks the threat data from outside the data repository, so a broken pipeline can't silence its own alarm.
4. `scripts/test-integrity.py` and `scripts/check-claude-config.py` guard the tests and the Claude Code configuration.

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
| Verifies itself with its own tool | | | ✓ | | | ✓ |
| Reproducible build settings | ✓ | ✓ | ✓ | | n/a (other builder) | ✓ (tested) |

## Verification performed

- actionlint 1.7.12 and the official workflow and Dependabot schemas: no problems.
- zizmor 1.32.0, auditor persona: no findings, after fixing one real issue (an over-privileged GitHub App token) and adding names, concurrency limits and permission comments.
- `goreleaser check` passes. Two release builds from the same commit, the second after touching every file, produced identical checksums for all six archives. The first attempt did not: archive timestamps differed until they were fixed to the commit date.

## One-time GitHub setup

1. Settings → General: enable **immutable releases**.
2. Settings → Environments: create `release`, require the other maintainer as reviewer, and allow only `v*` tags.
3. Settings → Rules: protect `main` with the four required checks in `docs/ci/allstar/branch_protection.yaml`, signed-off commits, and code-owner review.
4. Settings → Code security: enable CodeQL, secret scanning with push protection, Dependabot alerts and security updates, and private vulnerability reporting.
5. Install the Allstar and DCO GitHub Apps; copy `docs/ci/allstar/` into the org's `.allstar` repository.
6. Create a GitHub App with contents and pull-request write access to `homebrew-tap` only; store its ID as the `TAP_APP_ID` variable and its key as the `TAP_APP_PRIVATE_KEY` secret.
7. Create the `data-watch` issue label.
