**DEH ↔ Bellum parallels pilot — 2 October 2026**

Implemented in the canonical `LatinJosephus-v2-development` checkout on
`v2-development`, starting at `3d60d67`. The current-production ZIP's nine site
files matched this checkout byte for byte before work began. Existing branding
changes were present and are excluded from the pilot commit. No deployment or
recovery-repository change is part of this work.

The site is a static Jekyll site. `_pages/deh.md` and
`_pages/bellum-judaicum.md` share `_layouts/book.html`, the display-settings and
annotations includes, CETEIcean, and `assets/js/renderTei.js`. That renderer
defines the available works and sources, loads per-book XML from
`assets/xml/{work}/{language}/book-NN.xml`, and builds book, chapter, and unit
views. Existing `sameAs` links align a translation with that work's Latin
paragraphs; they are not DEH–Bellum scholarly correspondences.

DEH citation URLs use `book`, `chapter`, and chapter-local `unit` parameters.
For example, I.1.4 is `/deh/?book=1&chapter=1&unit=4`, although its canonical
Latin paragraph is `latin-deh1-num7` because three Prologue units precede I.1.
Explicit `num` is accepted as a compatibility input. Bellum retains both
paragraph navigation (`chapter` / `unit`) and independent Niese navigation
(`book` / `niese`). Cardwell uses checked paragraph-start [N] apparatus plus
internal Niese milestones; Whiston uses its own Niese milestones. Whiston
excerpts must not be selected merely by Cardwell paragraph IDs.

The smallest implementation adds an optional comparison component to the DEH
page. It loads only the ten I.1 records in
`assets/data/deh-bj-alignment.json`. Every record, including original cells,
raw strings, separators, ordered segments, other-work strings, and editorial
fields, is copied unchanged from the working package. `package_provenance`
preserves the package's original metadata and audit flags; those flags describe
the package before this pilot's QA. The source ZIP filename and SHA-256 identify
the input. Runtime relation identity is independent of either selected source.

The shared renderer gains only a DEH render-completion event. A separate script
adds comparison links to the recorded DEH paragraphs, including chapter and
book views. Selecting one opens two panes, defaults to Pollard–Whiston, and
offers independent Ussani/Pollard and Cardwell/Whiston choices. Bellum sections
are clipped using each displayed source's own boundaries. Ordered components
remain separate, and omitted intervening sections stay omitted. DOM clone IDs
are namespaced; canonical XML is never edited. The ordinary reader and its
controls return at the selected DEH citation when comparison is closed.

| DEH unit | Supplied BJ expression | Rendered ordered section groups |
| --- | --- | --- |
| I.1.1 | `1.31-35` | 31–35 |
| I.1.2 | `1.36-37` | 36–37 |
| I.1.3 | `1.47` | 47 |
| I.1.4 | `1.48, 42-44, 47` | 48; 42–44; 47 |
| I.1.5 | `1.54` | 54 |
| I.1.6 | `1.54-56` | 54–56 |
| I.1.7 | `1.57-60` | 57–60 |
| I.1.8 | `1.61` | 61 |
| I.1.9 | `1.62-67` | 62–67 |
| I.1.10 | `1.68-69, 71` | 68–69; 71 |

The existing query architecture supports sharing without introducing another
route or changing citation semantics. The comparison adds `parallel`,
`deh-source`, and `bj-source` to the DEH citation URL. For example:

```text
/deh/?book=1&chapter=1&unit=4&parallel=deh-1-1-4&deh-source=pollard&bj-source=whiston
```

Language changes push the corresponding URL, leaving the relation unchanged.
Back, forward, reload, and the visible comparison link restore the selected
sources. A relation is displayed only when it matches the renderer's resolved
canonical DEH passage. Each BJ component links back to its starting Niese
section in the existing Bellum reader.

QA passed in the local browser against the Jekyll-generated site:

- Ten units × four language combinations: 40 successful comparisons, with
  matching DEH citation, independent source choices, and no excerpt errors.
- All 29 distinct cited BJ sections checked against the existing reader in
  Cardwell and Whiston: 58 matching excerpts, comparing visible text after
  whitespace and generated citation-label normalization. Greek remained
  present in the ordinary Bellum reader.
- I.1.4 retained `48 → 42–44 → 47` in every combination; I.1.10 retained
  `68–69 → 71`, excluding 70. Single sections and contiguous ranges also passed.
- Back, forward, reload, source switching, and return to the selected DEH
  reading unit passed. History checks waited for resolved rendering.
- DEH book, chapter, Prologue, sub-chapter, and English pane controls passed.
  Chapter I.1 and Book I each had ten comparison links per language; I.2,
  the Prologue, and Book II had none.
- Bellum book, chapter, legacy paragraph route, and Niese controls passed.
  `/bellum-judaicum/?book=1&chapter=1&unit=31` retained its existing Latin ID,
  English `sameAs`, and Greek ID; switching to Book II loaded all three panes.
- Editorial package comparison passed for all ten complete records. Every
  canonical DEH ID resolved uniquely in both Ussani and Pollard.
- Final English–English view had no duplicate DOM IDs or browser error/warning
  logs. JavaScript syntax checks and Git whitespace checks passed. No XML
  changes appear in the diff.

The fully configured local Jekyll build cannot load the pre-existing
`jekyll-responsive-image` plugin because `rmagick` is missing. A build with only
that plugin omitted passed using all other configured plugins. No dependency
was installed and no repository build configuration was changed. Existing Sass
deprecation and pagination warnings remain. The successful QA build was:

```powershell
$env:JEKYLL_NO_BUNDLER_REQUIRE = 'true'
ruby -e "require 'jekyll'; config = Jekyll.configuration({'source'=>Dir.pwd,'destination'=>File.join(Dir.pwd,'_site')}); config['plugins'].delete('jekyll-responsive-image'); Jekyll::Site.new(config).process"
node --check assets/js/dehParallels.js
node --check assets/js/renderTei.js
```

Changed files: this report; `_includes/deh-parallels.html`;
`_includes/scripts/misc.html`; `_layouts/book.html`;
`assets/css/deh-parallels.css`; `assets/data/deh-bj-alignment.json`;
`assets/js/dehParallels.js`; `assets/js/renderTei.js`.

Rollback is a single commit revert. No full-concordance import, Antiquities
comparison, Prologue parallel, or difficult-notation interpretation is included.
The reported edition references still require individual print verification.
The pilot deliberately rejects unreviewed parentheses or open-ended excerpt
boundaries if they are later added to its data; broader editorial integration
requires separate work.
