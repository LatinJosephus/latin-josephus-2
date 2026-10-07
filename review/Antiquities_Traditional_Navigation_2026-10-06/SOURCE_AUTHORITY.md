# Source authority and implementation scope

Production base: `f7d9142cad998e8a005adea1a22532b9a78592db` on `v2-development`, verified clean before isolated worktree creation and unchanged after implementation. Worktree: `C:\workspace\LatinJosephus-antiquities-traditional-navigation`; branch: `antiquities-traditional-navigation`.

- Structural reconciliation v1.1: recovery commit `41e817680549767d36e3f80dbc825682908ea5e6`, tag `antiquities-structure-reconciliation-v1.1`.
- Independent Loeb–Niese verification v1.0: recovery commit `19308a8ed937525c540827205b0c763768f5ce44`, tag `antiquities-loeb-niese-verification-v1.0`.
- Historical frozen Loeb extraction identifier: `e03d32a`.
- Reconciliation manifest SHA-256: `cfc898b9f051a003de7045dbf352229097855e2c39696a33213c4454be50ff11`.
- Independent verification manifest SHA-256: `1a254cd03a3cb01541cb25e2b73f6e926da7ccbb2c724f1df244363d1e323b70`.

Existing manifests verified before preparation; complete frozen-packet inventories remain unchanged. No source PDF, manuscript image, human workbook or Word audit was reopened or altered. The registry consumes completed source metadata; the frozen packets were not copied into production. Every one of 1,689 source identities, literal labels, associations, independent statuses and physical-copy check records is machine-compared with the frozen authorities.

Chapter/Subchapter names the traditional Hudson-Havercamp division retained by Niese and substantially reproduced by Loeb. Niese citation numbers, literal printed readings, frozen extraction associations and independent verification statuses remain separate data. All nine Loeb omissions of lower 1 and four Niese-only lower-1 observations remain witness-specific; no new Loeb division is invented.

Current-text overlay corrections are separated from source judgments: VI.xiii / VI.xiii.1 Latin/English refer to existing num272; VII.i / VII.i.1 Latin directly refer to existing latin-book07-num without repairing sameAs; Book XI has ordered physical spans. The three Greek Book VI alignment bindings were separately and expressly authorized. None changes frozen v1.1 or source status.

The user supplied Levenson and Martin (2016), p.330, identifying Ba with Group D and its transposed/interpolated Book XI order. Publication identity is supported by https://onlinelibrary.wiley.com/doi/10.1002/9781118325162.ch21; the page itself was not independently re-read. The interpretation of Book XI as a corpus-order defect is withdrawn. Its XML order and all bytes remain untouched. Greek/English current editorial alignment order is distinguished from the original editions' order.

The registry uses standard TEI P5 elements: TEI, teiHeader/fileDesc, listBibl/bibl, text/body, list/item/label, fs/f/string, vColl and note/p. Ordered spans use `vColl org="list"` and nested feature structures; no private XML elements were introduced. Validation against official P5 4.12.0 Relax NG passes. Schema source: https://tei-c.org/Vault/P5/4.12.0/xml/tei/custom/schema/relaxng/tei_all.rng. All 13 new inline anchors point to certified identities in the external registry.

Canonical production uses some CRLF files; Git materialized LF in the isolated checkout. BASELINE.json distinguishes both inventories. Removing only the 13 authorized empty anchors restores every isolated-checkout XML file byte-for-byte. No pre-existing XML text, ID, sameAs, numeral, apparatus, paragraph or inline node was rewritten, moved or normalized.

This is an implementation ready for human review, not a new frozen scholarly authority. It remains unstaged and uncommitted. Public Niese navigation remains at existing I-VII coverage; VIII-XX expansion and Bamberg navigation remain future phases.
