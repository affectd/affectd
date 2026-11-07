# 0009. Record where credentials live, never their values

Status: Accepted, 6 November 2026

## Context

Attacks like Shai-Hulud steal credentials from well over a hundred known locations on a machine. To tell users what to rotate, affectd has to know where credentials are, but reading them would make affectd itself worth attacking.

## Decision

affectd records only where credentials are stored. The one exception is revoking a leaked GitHub token, which uses GitHub's public revocation endpoint and happens only when the user confirms it.

Response steps follow a fixed order: remove persistence first, because some attacks wipe the home folder when they see a token revoked, then revoke everything at once, look for abuse, clean up and verify.

## Consequences

A compromised affectd process has no secrets to leak. Users rotate credentials themselves, guided by the steps.

## Alternatives considered

- Reading tokens to check them against breach data: more automation, but affectd would become a credential store.
