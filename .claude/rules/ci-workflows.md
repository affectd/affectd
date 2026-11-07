---
paths:
  - ".github/**"
  - ".goreleaser.yaml"
  - "docs/ci/**"
---

# CI workflow rules

affectd's pipeline is a prime target: Trivy was compromised through CI twice, and tj-actions showed tags can be moved to malicious commits. Every workflow must pass actionlint and zizmor with no findings in the auditor persona.

- Pin every action and reusable workflow to a full commit SHA with the version in a comment, and only to a release at least 14 days old. Dependabot's cooldown keeps it that way.
- Start each workflow with `permissions: {}`; grant each job only what it needs, with a comment saying why.
- Begin every Linux job with harden-runner. Use `egress-policy: block` with an allowlist for release and data jobs.
- Check out with `persist-credentials: false`. Disable the Go cache in release and data builds.
- Never put `${{ github.event.* }}` or other untrusted text directly in `run:`; pass it through `env:`.
- No `pull_request_target`, no long-lived tokens (use OIDC or a GitHub App token scoped with `permission-*` inputs), and no AI agents processing pull-request or issue text in CI.
- Releases stay reproducible: `-trimpath`, `mod_timestamp` and fixed archive times in `.goreleaser.yaml`.
