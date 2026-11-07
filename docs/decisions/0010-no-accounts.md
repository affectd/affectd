# 0010. No accounts; team features come later

Status: Accepted, 6 November 2026

## Context

Teams will want shared dashboards, but accounts mean storing user data and running servers.

## Decision

affectd has no accounts. Team features are deferred to a self-hosted hub later. From v0.1, findings are saved as documented JSON and can be sent to webhooks, so the hub can be added without redesigning the engine.

## Consequences

Individuals get everything with no sign-up. Teams can build on the JSON and webhooks until the hub exists.

## Alternatives considered

- A hosted team service: easier for teams, but it contradicts the no-servers design.
