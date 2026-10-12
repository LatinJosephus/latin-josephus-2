# Original byte and Git representation preservation

The canonical Book XVIII file uses CRLF. Its Git object uses LF. Segmentation retains every actual canonical byte, including CRLF. Removing only the inserted niese milestones reproduces the exact frozen canonical file.

Only this isolated branch's active English file is staged with explicit autocrlf normalization to preserve its inherited Git representation. Every review-pack file is staged without text conversion, governed by this pack's scoped `.gitattributes`. GIT_REPRESENTATION_QA.json verifies reconstruction of both representations; GIT_REVIEW_PACK_BYTE_QA.json verifies all staged review bytes. No global Git setting or other worktree file is changed.
