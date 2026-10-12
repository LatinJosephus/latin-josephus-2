# Exact canonical bytes and Git representation

The pinned canonical English file has 76 CRLF line endings (SHA-256 d790d8c8138235db359479b6d92a230151852e55506fe36a8e502757df0dc678). Its pre-existing Git blob has 76 LF endings (SHA-256 a235d02f6d8af17961a124c417e3d9e2393f760442facf7963db47a1c7d9d96c).

The frozen original and segmented output preserve the canonical CRLF file bytes exactly. Removing the new milestones reconstructs that frozen canonical file byte for byte. The English source was staged with core.autocrlf=true scoped to this single file on the isolated branch, maintaining its pre-existing LF Git representation. Removing the new milestones from the committed Git blob reconstructs the original Git blob byte for byte. The committed segmented blob is also exactly the archived segmented file with CRLF mapped to LF; no other character changes are permitted.

The review pack is scoped with * -text and staged with core.autocrlf=false, so every archived input, output, ledger and script has identical staged Git bytes. Recovery uses output/book-17.xml and the frozen canonical file, preserving exact canonical bytes. IMPLEMENTATION.patch represents the independently checked LF repository change. No canonical checkout or other workstream was normalized or edited.
