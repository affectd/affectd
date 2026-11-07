# 0006. Updates depend on how affectd was installed

Status: Accepted, 6 November 2026

## Context

Some users install affectd with a package manager, others download it directly. Updating the program behind a package manager's back breaks that package manager.

## Decision

affectd detects how it was installed. Package-manager installs only get a notice that an update exists. Direct downloads update themselves, with automatic rollback if the new version fails to start.

## Consequences

Package managers stay in charge of their own installs, and direct-download users still get fixes without effort.

## Alternatives considered

- Always self-updating: simpler, but it fights Homebrew and Linux package managers.
