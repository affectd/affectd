# Maintainers

| Name | GitHub | Affiliation |
| --- | --- | --- |
| Rayan Alyasi | [@RayanAlyasi](https://github.com/RayanAlyasi) | King Abdulaziz University |
| Omar | [@omarg-dev](https://github.com/omarg-dev) | King Abdulaziz University |

[GOVERNANCE.md](GOVERNANCE.md) describes what maintainers do and how to become one.

## Access to sensitive resources

Only maintainers have this access, and it's reviewed whenever someone joins or leaves.

| Resource | Who |
| --- | --- |
| GitHub organisation (owner) | Both maintainers |
| Release approval (the `release` environment) | Both maintainers |
| Private security reports and advisories | Both maintainers |
| Homebrew tap GitHub App | Both maintainers |
| `affectd.dev` domain | Rayan Alyasi |

Release signing has no long-lived key to hold. Releases and threat data are signed by GitHub Actions workflows through Sigstore, so access to them is controlled by who can change and approve those workflows.

## Emeritus maintainers

None yet.
