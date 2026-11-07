# 0008. Detection is deterministic; AI only explains

Status: Accepted, 6 November 2026

## Context

An AI assistant can make findings easier to understand. But attackers now plant text aimed at AI tools, so a model must never be able to clear a finding.

## Decision

Detection is exact matching against published data. The optional AI assistant receives only the structured finding and the official advisory text, never file contents or secrets, and answers in a fixed format. No code path lets it lower a severity, clear or hide a finding.

Users choose the provider: a local model through Ollama (a 4B model on 8 GB machines, 8B on 16 GB), their own Claude or Gemini API key, OpenAI's "Sign in with ChatGPT", affectd as a read-only MCP server inside their own AI app, or a button that copies a prepared summary to the clipboard.

## Consequences

Prompt injection can at worst produce a bad explanation, never a hidden attack. The AI feature works with nothing sent anywhere, through the local model.

## Alternatives considered

- AI-assisted triage that can dismiss false positives: fewer alerts, but an attacker could write text that dismisses a real one.
