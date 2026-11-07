# 0001. Go for the detection engine

Status: Accepted, 6 November 2026

## Context

affectd needs an inventory of everything installed on a machine. OSV-SCALIBR, Google's inventory library, already reads dozens of package formats, and it is written only in Go.

## Decision

The engine is written in Go and uses OSV-SCALIBR for inventory.

## Consequences

We get maintained extractors for every major ecosystem from day one. Go is memory-safe, and the update and signing libraries we need, go-tuf and sigstore-go, are Go too, as are most OpenSSF projects, which makes reviewers and contributors easier to find.

## Alternatives considered

- Rust: also memory-safe and faster, but we would have to rebuild the whole extractor library ourselves before detecting anything.
