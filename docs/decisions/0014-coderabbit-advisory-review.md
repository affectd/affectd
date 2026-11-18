# 0014. CodeRabbit as an advisory reviewer

Status: Proposed, 18 November 2026

## Context

Maintainers review every pull request, and `/feature` runs three AI reviews in the author's own session. Pull requests from contributors get no AI review before a maintainer reads them. CodeRabbit is a hosted service that reviews pull requests through a GitHub App.

[0013](0013-no-ai-agents-in-ci.md) keeps AI agents out of CI, because attacker-written text could make them leak CI secrets. CodeRabbit doesn't run in our CI and can't read its secrets. It brings a different risk. Its app has read-and-write access to code, pull requests, issues, checks, commit statuses and workflows. In January 2025, [Kudelski Security showed](https://kudelskisecurity.com/research/how-we-exploited-coderabbit-from-a-simple-pr-to-rce-and-write-access-on-1m-repositories) that a pull request to any repository could run code on CodeRabbit's servers and read the app's private key. That key gave write access to about a million repositories. CodeRabbit has since fixed the flaw. None of the OpenSSF projects affectd compares itself with use CodeRabbit.

## Decision

We use CodeRabbit as an advisor, never as a gate. It is installed and configured so that its access can't reach what users trust:

- It is installed on affectd/affectd only, through "Only select repositories". It is never installed on affectd/data, which builds the signed threat data, or on affectd/homebrew-tap.
- Its reviews never count. Merging to `main` needs a code owner's approval, and CODEOWNERS lists only maintainers. `.coderabbit.yaml` also turns off approving and requesting changes.
- It never pushes commits. The settings that write code (unit tests, autofix, CI fixes and merge-conflict fixes) are off.
- It keeps no learnings, so a comment can't plant instructions for later reviews.
- Secrets live only in the `release` environment, which needs the other maintainer's approval and runs only for `v*` tags. Anything with write access, an app or a person, can push a branch with a workflow that reads repository-level secrets, so we keep none there.
- The labels it applies are only for finding things. No workflow, ruleset or release step may depend on a label.
- Changing `.coderabbit.yaml` needs both maintainers' review.

0013 still holds: no AI agent runs in our GitHub Actions.

## Consequences

Contributors get an AI review, and pull requests get area labels. Until the repository has 10 stars, CodeRabbit reviews only when someone comments `@coderabbitai review`.

If CodeRabbit's key leaked again, an attacker could push branches, comment, and edit issues and pull requests in affectd/affectd. They couldn't merge to `main`, publish a release or read release secrets.

CodeRabbit reads text the attacker wrote, including any `AGENTS.md` the pull request changes. A review saying a change is safe therefore means nothing on its own, and maintainers review every change as before.

Remove CodeRabbit if it has another incident that exposes its app key. Also remove it if, by the v0.1 release, its reviews haven't found problems the maintainers' reviews missed.

## Alternatives considered

- Not installing it: no new access, but contributors wait for a maintainer before they get any review.
- An AI review action in our own CI: rejected by 0013, because it would run alongside our CI secrets.
- Installing it on every repository: wider coverage, but write access to affectd/data could change the threat data every user trusts.
