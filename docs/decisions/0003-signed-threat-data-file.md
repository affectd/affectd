# 0003. Threat data as a signed file built on GitHub

Status: Accepted, 6 November 2026

## Context

affectd needs fresh malicious-package and vulnerability data on every machine. Asking an online service about each installed package would reveal the user's inventory, and running our own servers would cost money and give attackers a target.

## Decision

A scheduled GitHub Actions workflow builds one compressed data file every hour at 17 minutes past and signs it with Sigstore. It is published on GitHub Releases and the GitHub container registry, with Amazon ECR Public added when usage grows. Devices only download.

Devices check the signature and that it came from our workflow, refuse files older than the copy they have, and warn if the data is more than 48 hours old. If downloads fail, affectd keeps using its last good copy and can fetch the CISA KEV list directly.

## Consequences

Devices never send their inventory anywhere, so matching is private by design. The project runs no servers. Anyone can read the workflow that builds the data. Compressing the raw sources, about 1.9 GB, gives a file of roughly 4 MB.

## Alternatives considered

- Querying OSV's API with each package: always fresh, but it sends the inventory off the machine.
- Running our own update server: full control, but cost, operations work and a target to defend.
