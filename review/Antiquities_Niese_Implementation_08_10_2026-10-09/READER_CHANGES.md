# Shared generic reader dependency

renderTei.js gains a generic per-book Niese identity registry: declared availability, executable-label exceptions, unavailable language sections, broader English context targets and reader-facing correspondence notes. Metadata folio numbers and apparatus are excluded from narrative identities. Existing I–VII availability remains unchanged. New declarations are explicit keys 8 and 10; IX is absent. There are no book-specific rendering branches.

display-settings.html adds optional Antiquities Niese Previous/Next controls. Their behavior follows actual citation identities, including X.108, and disables endpoints. Chapter, Subchapter, Bamberg, Alignment and contents semantics remain unchanged.

The shared reader commit contains the generic machinery with an empty new registry declaration. The VIII commit adds only key 8; the X commit adds key 10. Each book commit includes its own data and independent certificate. Shared batch proof follows in a separate certification commit. The combined tested production reader differs from the per-book intermediate state only in those explicit availability keys.
