# 0007. How releases and pipelines are protected

Status: Accepted, 6 November 2026

## Context

A security tool's own build is a prime target. Trivy was compromised twice through incomplete credential rotation, and in 2025 attackers moved the version tags of a popular GitHub Action to a malicious commit.

## Decision

- Releases are immutable GitHub releases: tags are locked and assets can't be replaced.
- Two-person rule: one maintainer tags, the other approves before anything is built.
- Both maintainers use two-factor authentication.
- Actions are pinned to full commit hashes of releases at least 14 days old.
- Publishing uses short-lived OIDC tokens only, never stored credentials.
- Release builds are reproducible and run with network access limited to the hosts they need.

## Consequences

An attacker needs to compromise both maintainers or the workflow itself, and a changed tag upstream can't change what we run. Releases take slightly longer because a second person has to approve.

## Alternatives considered

- Single-maintainer releases: faster, but one stolen account would be enough.
