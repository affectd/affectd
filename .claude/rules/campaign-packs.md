---
paths:
  - "campaigns/**"
---

# Campaign packs

A campaign pack describes one known attack: what it installs, what it leaves behind, and how to respond.

- Every indicator (file path, hash, process name, workflow pattern) cites a public source in the pack's `references`. No source, no indicator: a wrong indicator causes false alarms for every user.
- Prefer indicators specific to the campaign. Generic locations such as `~/.npmrc` are credential locations for the response steps, not evidence of infection.
- Each pack has a replay fixture in `testdata/fixtures/<pack-id>/` that triggers it, and it must stay quiet on `testdata/fixtures/clean/`.
- Response steps keep this order, because attackers plant dead-man switches that wipe the machine when a token is revoked: remove persistence first, then revoke all affected credentials at once, then look for abuse, then clean up, then verify.
