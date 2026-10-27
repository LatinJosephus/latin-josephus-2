# Manuscript annotation display redesign

Implementation for LatinJosephus v3, based on the current `v2-development` branch. 26 October 2026.

- [Reconnaissance and source exceptions](RECONNAISSANCE.md)
- [Editorial notation inventory](NOTATION-INVENTORY.md)
- [English translations of editorial notes](ENGLISH-EDITORIAL-NOTES.md)
- [Citation mapping, provenance and exceptions](CITATIONS.md)
- [Automated QA and visual checks](QA-REPORT.md)
- [Before-and-after screenshot index](SCREENSHOTS.md)
- [DEH compatibility](DEH-COMPATIBILITY.md)
- [Changes, branch and implementation commit](CHANGE-REPORT.md)

The implementation preserves the canonical XML and original associations. Source-level anomalies are documented and retained for editorial review. No merge, push, public preview or deployment is part of this delivery.

Run `node bin/annotations/qa.cjs` for the repeatable source, citation, interpretation and integrity checks. Run `bin/annotations/browser-qa.cjs` against locally generated baseline/final sites for browser certification. A static citation lookup must be regenerated and checked whenever canonical segmentation inputs change; it is not a second manually edited authority.
