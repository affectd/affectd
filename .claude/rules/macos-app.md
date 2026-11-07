---
paths:
  - "apps/macos/**"
---

# macOS app (Swift)

- Build with `swift build --package-path apps/macos`; test with `swift test --package-path apps/macos`. Update these lines if the app moves to an Xcode project.
- Use SwiftUI for windows and the menu bar (`MenuBarExtra`), and AppKit only where SwiftUI can't do the job.
- Follow Swift's API Design Guidelines for naming. Prefer value types (`struct`, `enum`); add a protocol only when two types conform or a test needs a stand-in.
- Build in the Swift 6 language mode, so the compiler rejects data races, and write tests with Swift Testing.
- No force unwraps (`!`) or `try!` in app code: a crash hides alerts from the user.
- Display threat data with `Text(verbatim:)`. Never render advisory HTML or Markdown and never embed a web view: package names and advisories are written by attackers, and a web view turns an escaping mistake into code execution.
- Show a link's real domain before opening it in the browser.
- Talk to the service only through the client generated from `proto/`. Never read the service's database directly.
- Store secrets in the Keychain, never in UserDefaults or files.
