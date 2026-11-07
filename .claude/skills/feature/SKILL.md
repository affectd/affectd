---
name: feature
description: Implements one unfinished feature from docs/roadmap/v0.1.json end to end, verified by tests, then commits it.
disable-model-invocation: true
argument-hint: "[feature-id]"
---

Implement one roadmap feature. `$ARGUMENTS` is the feature id. If it is empty, pick the first feature whose `"passes"` is `false` and whose `depends_on` features all pass.

1. **Orient.** Run `git log --oneline -15` and read the feature's entry in `docs/roadmap/v0.1.json`. Run `make check` to confirm the tree is green before changing anything. If it isn't green, stop and report what fails.
2. **Design.** Before any code:
   - Outline two or three genuinely different approaches and compare them on correctness, time and memory at affectd's scale (the budgets in `.claude/rules/matching.md`), simplicity and security. Pick the best and say why.
   - List the edge cases, failure paths and inputs the approach must handle, including attacker-written ones.
   - List the files you expect to change and the tests that will prove the acceptance criteria.
   - If the plan touches more than one package or makes a hard-to-reverse choice, show it to the user and wait for approval.
3. **Test first.** Write the acceptance test, plus the fixture under `testdata/fixtures/` for detection work, and a fuzz test for any new parser. Run the test and confirm it fails for the expected reason.
4. **Implement** the smallest change that makes the test pass. If the test turns out to be wrong, stop and tell the user rather than changing it.
5. **Measure** if the feature touches matching, inventory or data loading: add or update the benchmark, run `make bench`, and compare with `make bench-compare` against the saved baseline. Stay within the budgets in `.claude/rules/matching.md`.
6. **Verify.** Run `make check`. Then get three fresh-context reviews, running the two subagents in parallel: `/code-review` for bugs, the `quality-reviewer` for design, duplication, performance and tests, and the `security-reviewer` for the threat model. Fix every blocking or must-fix finding, and each should-fix finding unless you can state why it doesn't apply. Leave "consider" items alone unless they're clearly worth it. Run `make check` again. Do at most one review-and-fix round; if new blocking findings appear after it, or a finding calls for a redesign, stop and bring them to the user.
7. **Record.** Set `"passes": true` for this feature only. Leave its description and acceptance criteria unchanged.
8. **Commit** with `git commit -s` and a message that names the feature id. Then tell the user what changed, the test and benchmark evidence, the reviewers' findings and how they were resolved, and anything left open. Finish by recommending a fresh session for the next feature, since everything needed is now in git and the feature list.
