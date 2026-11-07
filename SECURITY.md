# Security policy

affectd reads files that attackers write, so a bug in it can hurt the people who rely on it. Thank you for helping us find them.

## Reporting a vulnerability

Please report vulnerabilities privately through [GitHub's private vulnerability reporting](https://github.com/affectd/affectd/security/advisories/new). Don't open a public issue, pull request or discussion.

If you can't use GitHub, email <rayanalyasi@gmail.com> with "affectd security" in the subject.

A useful report includes:

- the affectd version (`affectd version`) and your operating system
- what an attacker could do, and what they would need first
- steps or a proof of concept that reproduce it, using fake data rather than real malware or real credentials

If you believe the problem is being exploited now, say so in the first line.

## What happens next

- We acknowledge your report within three business days.
- Within ten business days we tell you whether we accept it, and our plan.
- We keep you updated at least every two weeks until it's fixed.
- We aim to release a fix within 90 days. If we need longer, we'll agree a date with you.
- When the fix is out, we publish a GitHub Security Advisory, request a CVE, and credit you unless you'd rather we didn't.

Please keep the details private until the advisory is published.

## What counts

Report it here if it lets someone:

- make affectd run code, crash, or use excessive resources with a crafted file, package, extension or configuration it scans
- hide a finding from the user or lower its severity, including through text aimed at the optional AI assistant
- get affectd to accept threat data, a campaign pack or an update that our pipeline didn't sign
- read credential values through affectd, or reach its local API or MCP connector from another user account
- tamper with our release or data pipelines

Some problems belong elsewhere. An attack that affectd misses or flags wrongly is a detection problem rather than a vulnerability, so use the [detection report form](https://github.com/affectd/affectd/issues/new?template=detection_report.yml). A malicious package that no database lists yet should go to [OpenSSF Malicious Packages](https://github.com/ossf/malicious-packages), which feeds affectd. A known vulnerability in one of our dependencies is already public, so a normal issue is fine.

## Supported versions

Until 1.0, only the latest release gets security fixes. affectd also refuses threat data older than the copy it already has, so keeping the data current needs no action from you.

## Verifying a release

Every release's `checksums.txt` is signed with Sigstore by our release workflow. To check a download:

```sh
cosign verify-blob checksums.txt \
  --bundle checksums.txt.sigstore.json \
  --certificate-identity "https://github.com/affectd/affectd/.github/workflows/release.yml@refs/tags/<version>" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
sha256sum --check --ignore-missing checksums.txt
```

Each binary also has SLSA build provenance, which you can check with `gh attestation verify <file> --repo affectd/affectd`.
