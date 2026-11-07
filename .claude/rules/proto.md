---
paths:
  - "proto/**"
---

# Local API schema

The macOS app, the future Windows app and the MCP connector all depend on this contract, and users may run an app and a service from different releases.

- Only make additive changes. Never renumber or reuse a field number; mark removed fields and names as `reserved`.
- Run `make proto` after every change and commit the generated code in the same commit.
- Every field that carries threat data is documented as attacker-controlled text, so client authors know to display it as plain text.
