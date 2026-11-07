# 0004. What the first run checks

Status: Accepted, 6 November 2026

## Context

A new user wants to know straight away whether they are already affected, including by attacks reported before they installed affectd.

## Decision

The first run downloads the full data file, which includes the complete history of malicious-package reports. It checks everything installed now, plus package caches automatically. Scanning Git history is optional, one click. Results arrive as one summary grouped by severity, except that a compromised package alerts immediately.

When a report is withdrawn, affectd removes the finding and says why.

## Consequences

Old installs left in caches are caught without extra steps. Git history is opt-in because scanning it takes longer.

## Alternatives considered

- Checking only what is installed now: faster, but misses copies sitting in caches.
