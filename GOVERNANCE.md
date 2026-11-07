# Governance

affectd is a small project with two maintainers. This document says who can do what, how we make decisions, and how contributors take on more responsibility. We'll grow it when the project needs more.

## Roles

**Contributors** are anyone who opens an issue, reviews a pull request, answers a question or sends a change. No permission is needed.

**Reviewers** have shown they know part of the codebase well, through several merged pull requests and helpful reviews. Their approval counts toward merging changes in that area. A maintainer nominates a reviewer in an issue, and the maintainers agree.

**Maintainers** are responsible for the project as a whole: reviewing and merging changes, triaging issues and security reports, approving releases, and keeping the project safe for its users. They have access to the project's sensitive resources, listed in [MAINTAINERS.md](MAINTAINERS.md).

To become a maintainer, you'll usually have been a reviewer for at least three months, reviewed changes across more than one area, and shown that you understand the [rules that protect users](AGENTS.md#rules-that-protect-users). Any maintainer can nominate you in an issue, and all current maintainers must agree.

**Emeritus maintainers** have stepped down. We list them in MAINTAINERS.md to thank them, and they can return by asking.

## Making decisions

Most decisions happen in issues and pull requests. A pull request can merge once a maintainer approves it, no one has raised an unresolved objection, and CI passes. Changes to releases, workflows and other files listed in `.github/CODEOWNERS` need every maintainer to approve.

Larger decisions, such as a new data source or a change to the threat-data format, start as an issue so contributors can comment before we decide.

If maintainers disagree, the change waits while we discuss it. With two maintainers, a tie means we don't go ahead. If it can't be settled and the decision can't wait, we'll ask a trusted person outside the project to advise, such as our OpenSSF working group sponsor once we have one.

## Security and releases

Releases follow a two-person rule: one maintainer pushes the release tag and the other approves the release in GitHub before anything is built or published. Both maintainers use two-factor authentication. Security reports are handled privately as described in [SECURITY.md](SECURITY.md).

## Stepping down

A maintainer can step down at any time by opening a pull request that moves them to the emeritus list. If a maintainer is inactive for six months, the others will ask whether they'd like to step down. When anyone leaves a role, their access to sensitive resources is removed within a week.

## OpenSSF

We plan to apply for the OpenSSF Sandbox after the first release. If affectd is accepted, OpenSSF's technical policies will apply alongside this document.

## Changing this document

Changes to this document need every maintainer to approve.
