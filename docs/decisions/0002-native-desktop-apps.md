# 0002. Native desktop apps, no web views

Status: Accepted, 6 November 2026

## Context

affectd displays text that attackers write: package names, descriptions and file paths. In a web view, one escaping mistake turns that text into code running with the app's rights.

## Decision

A Go service does all detection on every platform. Each desktop app is a thin native client that talks to it over a local API defined in Protocol Buffers, on a Unix socket (macOS and Linux) or a named pipe (Windows) that only the user can open.

- macOS: Swift and SwiftUI menu-bar app that shows untrusted text as plain text (`Text(verbatim:)`).
- Windows: C# with WinUI 3 and the Windows App SDK, planned for 2028.
- Linux: the command-line tool and a systemd user service first; a native app later.

## Consequences

Attacker text can't become code in the apps. We maintain separate UI code per platform, which is why the Windows app comes later. Tailscale uses the same pattern of a Go service with native wrappers.

## Alternatives considered

- Electron, Tauri and Wails: one shared UI, but each renders in a web view, and these tools have had bypasses that turned injected text into code execution.
