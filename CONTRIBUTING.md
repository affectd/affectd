# Contributing to affectd

Thanks for your interest in affectd. This guide covers how to report problems, how to get a change merged, and the few rules that exist because affectd handles attacker-written data on people's machines.

Everyone taking part follows our [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to help

The most useful thing you can send us is a report of an attack affectd misses or something it flags wrongly. Use the [detection report form](https://github.com/affectd/affectd/issues/new?template=detection_report.yml) for those, and the [bug report form](https://github.com/affectd/affectd/issues/new?template=bug_report.yml) for anything else that doesn't work.

You can also fix bugs or add features (issues labelled [`good first issue`](https://github.com/affectd/affectd/labels/good%20first%20issue) are a good place to start), add a campaign pack for a real attack, or answer questions in [Discussions](https://github.com/affectd/affectd/discussions).

Security vulnerabilities are different: report them privately as described in [SECURITY.md](SECURITY.md).

## Before you start

For anything bigger than a small fix, open an issue first and describe what you want to change. It saves you from writing code we can't merge, for example because it conflicts with the [rules that protect users](AGENTS.md#rules-that-protect-users).

Settled choices, such as Go for the engine or native desktop apps, are recorded with their reasons in [docs/decisions/](docs/decisions/). To change one, open an issue that proposes a new decision record.

Comment on an issue before you start work on it, so two people don't fix the same thing.

## Setting up

You need Go (the version in `go.mod`), `make` and Git. For the macOS app you also need Xcode with Swift 6.

```sh
git clone https://github.com/affectd/affectd.git
cd affectd
make check
```

`make check` runs formatting, `go vet`, the linters, the tests with the race detector, and `govulncheck`. CI runs the same checks, so if it passes locally it should pass there.

Other targets you'll use:

| Command | What it does |
| --- | --- |
| `go test ./internal/<pkg>/...` | Tests for one package while you work |
| `make fuzz` | Every fuzz target for 30 seconds each |
| `make bench` and `make bench-compare` | Benchmarks compared with a saved baseline |

## Making a change

1. Fork the repository and create a branch from `main`.
2. Make your change with tests. Pull requests that change behaviour without a test won't be merged.
3. Run `make check`.
4. Sign off every commit (see below) and open a pull request. The template asks for what changed, why, and how you tested it.

A maintainer will review your pull request, usually within a week. If you've heard nothing after a week, comment on it to remind us. Changes to `.github/`, `.claude/`, `AGENTS.md`, `CLAUDE.md`, the Makefile, the linter configuration, `scripts/` or `campaigns/` need both maintainers to approve, because they affect releases or run on contributors' machines.

We squash small pull requests when merging. For larger ones, please keep the commits meaningful so they can be merged as they are.

## Standards

Go code follows [Effective Go](https://go.dev/doc/effective_go) and [Google's Go Style Guide](https://google.github.io/styleguide/go/). The linters enforce most of it. The rest, such as keeping interfaces small and avoiding abstractions with one user, is listed in [AGENTS.md](AGENTS.md#design).

Some changes need more than a unit test:

- A detection change needs a fixture in `testdata/fixtures/` that proves it fires, and it must stay quiet on `testdata/fixtures/clean/`.
- A new file parser needs a fuzz test.
- A change to matching, inventory or data loading needs benchmark results from `make bench-compare` in the pull request. Matching 10,000 packages must stay under 50 ms.

Never delete, skip or weaken an existing test to make a change pass. If a test looks wrong, say why in the pull request instead. CI lists every weakened test for reviewers.

## Developer Certificate of Origin

affectd uses the [Developer Certificate of Origin](https://developercertificate.org/) (DCO) instead of a contributor licence agreement. By signing off a commit, you confirm you wrote it or otherwise have the right to submit it under the project's licence.

Sign off with `-s`:

```sh
git commit -s -m "Add pnpm lockfile support"
```

This adds a `Signed-off-by:` line with your name and email. If you forgot, fix the last commit with `git commit --amend -s --no-edit`, or every commit on your branch with `git rebase --signoff main`, then force-push.

## Campaign packs

A campaign pack describes one real attack: the packages involved and the traces it leaves behind, such as files, startup items or workflows. Each pack needs:

- at least one primary source, such as the advisory or the security researchers' write-up
- a replay fixture that recreates the attack's traces on a fake machine, using made-up file contents
- the response steps in the right order, with anything that could trigger a destructive payload removed before credentials are revoked

## Test data

Use obviously fake secrets in fixtures, such as `FAKE-npm-token-0000`. Never commit a real token or key, even an expired one, and never commit real malware or files copied from a compromised machine.

## Dependencies

Every dependency is code that runs on our users' machines, so we add them carefully. Prefer the standard library and OSV-SCALIBR. If you need a new dependency, explain in the pull request why, and check that:

- the module is the one you meant, since AI tools sometimes suggest package names that don't exist and that attackers then register
- it's actively maintained and its licence is Apache-2.0, MIT, BSD, ISC or MPL-2.0
- it doesn't pull in a large tree of other dependencies for a small feature

## Using AI tools

You can use AI tools to help write your contribution. affectd's maintainers use Claude Code, and the repository's [AGENTS.md](AGENTS.md) gives coding agents the same rules this guide gives you.

You are responsible for everything you submit:

- Understand every line and be able to explain it in review.
- Make sure the tool's terms don't restrict how its output can be used, and that it hasn't reproduced someone else's code without a compatible licence, as the [Linux Foundation's guidance](https://www.linuxfoundation.org/legal/generative-ai) asks.
- Don't credit the AI tool in your commits: no `Co-Authored-By:` line naming the agent and no `Assisted-by:` trailer.
- Keep pull request descriptions and comments short and in your own words. Long generated text costs reviewers time.

Pull requests opened by an agent with no person reviewing them first will be closed.

## Becoming a reviewer or maintainer

Regular contributors can become reviewers and then maintainers. [GOVERNANCE.md](GOVERNANCE.md) explains how.
