# 0011. Homebrew first on macOS; SignPath for Windows

Status: Accepted, 6 November 2026

## Context

A downloadable macOS app needs Apple's paid developer programme for signing and notarisation, $99 a year. Windows binaries need code signing too.

## Decision

Until v0.3, macOS users install through our Homebrew tap, which builds from source. Locally built apps get no quarantine flag, so they run without warnings and can show notifications. We join the Apple Developer Programme for the downloadable app in v0.3, funded through GitHub Sponsors or OpenSSF support if possible. Windows releases are signed through the SignPath Foundation, which is free for open source.

## Consequences

No signing costs until the macOS app is ready. Still to confirm with a prototype: that SMAppService works for a locally built, ad-hoc-signed app.

## Alternatives considered

- Paying for the Apple programme now: a downloadable app sooner, but a cost before anyone uses affectd.
