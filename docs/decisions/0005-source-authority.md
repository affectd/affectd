# 0005. Which source wins when sources disagree

Status: Accepted, 6 November 2026

## Context

OSV, the GitHub Advisory Database, NVD and vendors sometimes disagree about which versions are affected or whether something is exploited.

## Decision

For open-source packages, the ecosystem's own database wins. For vendor products, the vendor's advisory wins. NVD is the fallback. Any trusted source reporting active exploitation counts. A withdrawn report always wins.

## Consequences

Results are predictable and explainable: affectd can always say which source it followed and why.

## Alternatives considered

- Taking the most severe answer from any source: simpler, but it would produce false alarms users learn to ignore.
