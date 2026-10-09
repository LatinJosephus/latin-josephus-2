# Recognize Niese milestones in anonymous narrative paragraphs

The pinned renderer required a parent `tei-p[id]` for executable Latin Niese milestones. XIV's surviving narrative includes anonymous paragraphs. Sections 73–76 require starts inside one of these paragraphs; adding paragraph IDs or splitting the source paragraphs is outside the authorized segmentation method.

The milestone branch now requires a parent `tei-p`, preserving the existing body and apparatus guards. The num-label branch, reader architecture, source selection and availability configuration are unchanged. Existing registry `contextTarget` supplies the stable alignment context when the paragraph itself is anonymous.

Validation used the actual assignment build at `C:\workspace\Antiquities-Niese-14-15-runtime-20261009\build2\site` and independent local browser profiles. The partial reviewed-range harness passed 139 XIV and 79 XV adjoining intervals, including XIV 73–76, both inherited-label exceptions identified in the reviewed XIV range, and approved XV.39–40 reciprocal notes. It checked exact Greek/Latin extents, independent English context, unique IDs, chapter/subchapter marker coverage, deep links, previous/next, reload/history, pane switching and light/dark themes. This validates these reviewed intervals and the shared reader change; it is not full-book certification.

The protected regression harness passed all 26 accepted VIII/X critical URLs, 15 protected routes, full VIII/X executable identity census and chapter/subchapter coverage, navigation, history, panes, themes, IX fallback, X.108 language independence and Lodge note switching. It reported zero browser exceptions, console errors and failed requests. Exact result: [PROTECTED_READER_CHANGE_BROWSER_QA.json](PROTECTED_READER_CHANGE_BROWSER_QA.json).

The initial test setup failures remain in diagnostics: a partial registry originally used the full expected book range and failed schema validation; the protected adapter initially pointed at a nonexistent reference build2 directory. Both setup issues were corrected before the passing checks. No new reader error was waived as an inherited exception.

No full-book availability has been enabled. No canonical, other-worker, preview or publication state has been modified.
