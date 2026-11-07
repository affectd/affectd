---
paths:
  - "internal/match/**"
  - "internal/data/**"
---

# Matching and threat data

These decisions are settled; follow them rather than re-deriving them.

Which source wins when sources disagree:

- **Affected versions:** ecosystem databases (OSV, GitHub Advisory Database) for open-source packages; the vendor's own advisory for vendor products; NVD only as a fallback. Explicit fixed versions and bounded ranges beat open-ended ranges.
- **Exploited:** one trusted source is enough (CISA KEV, CISA's "active" exploitation rating, or a vendor's in-the-wild statement).
- **Malicious:** an OpenSSF report counts until it is withdrawn. A withdrawal always wins; remove the finding and tell the user why.
- If sources still disagree about the installed version, report the finding with a "sources disagree" note. Never drop it silently.

Other invariants:

- Re-matching new threat data runs against the stored inventory and must not touch the disk. That is what keeps retroactive alerts cheap.
- Reject a data file that fails the signature or signing-identity check, or that is older than the stored copy. Keep using the last good copy and warn the user once data is more than 48 hours old.
- Devices only download threat data. No code path may send a device's inventory anywhere.

Performance budget, checked by `BenchmarkMatch` and `BenchmarkRematch`: matching 10,000 installed packages against the full index takes under 50 ms on a laptop, and the in-memory index stays under 100 MB.
