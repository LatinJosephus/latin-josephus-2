**DEH ↔ Bellum parallels pilot — Phase 2, 2 October 2026**

Implemented only in the canonical `LatinJosephus-v2-development` checkout on
`v2-development`, extending `40b1b62`, confirmed in history before work began.
Pre-existing branding and local preview changes were inventoried and preserved.
No recovery-repository change, push, deployment, dependency installation, or full
concordance import is part of this work.

The static Jekyll site uses `_pages/deh.md` and `_pages/bellum-judaicum.md`, shared
`_layouts/book.html`, display-settings/annotations includes, CETEIcean, and
`assets/js/renderTei.js`. The renderer loads per-book canonical XML from
`assets/xml/{work}/{language}/book-NN.xml`. Existing translation `sameAs` links
belong to within-work reader alignment; they do not encode DEH–Bellum parallels.

DEH URLs use `book`, `chapter`, and chapter-local `unit`. I.1.4 uses unit 4 but
canonical ID `latin-deh1-num7`, following three Prologue units. V.53.1 resolves to
`latin-deh5-num120`. Bellum retains legacy `chapter` / `unit` navigation and
independent `book` / `niese` navigation. These routes and identities are unchanged.

The smallest extension retains the separate scholarly alignment layer,
`assets/data/deh-bj-alignment.json`, and optional DEH comparison component.
Exactly eleven records are included: ten I.1 entries and V.53.1. The runtime
scope guard also restricts the interface to those passages. Complete records,
including raw cell values, ordered segments, separators, offsets, other-work
strings, parentheses, decisions, and unresolved questions, remain unchanged from
the editorial package. V.53.1 is workbook row 554. `package_provenance` retains
the original audit flags, which describe the input package rather than this QA.
The source ZIP filename and SHA-256 identify the input. Scholarly relation
identity is independent of either selected display source.

The separate `dehParallels.js` module listens for the existing DEH
render-completion event, adds comparison links to matched reading paragraphs,
and loads cached XML into cloned comparison panes. The shared renderer, layouts,
and script wiring required no Phase-2 changes. English–English remains default.

| Pane | Source | Identity |
| --- | --- | --- |
| DEH English | Pollard v1.0 | English translation of the Latin DEH |
| DEH Latin | Ussani (1932) | Latin DEH |
| Bellum Greek | Niese | Greek Bellum |
| Bellum Latin | Cardwell (1837) | Latin translation of the Bellum |
| Bellum English | Whiston | English translation of the Greek Bellum |

Whiston is not described as translating Cardwell. A parallel indicates
corresponding material, not exact verbal equivalence, full-unit correspondence,
or dependence between the Latin versions. The visible provenance wording states
that the parallel references were transcribed from Ussani/Mras and still require
independent print verification. Visible BJ references use Roman books and en
dashes; stored numbers, literal editorial strings, and URL coordinates remain
unchanged.

All three Bellum sources resolve the same Niese coordinates. Greek has one
complete canonical paragraph per section, with ID
`greek-bellum{book}-num{section}`. The module clones that paragraph and supplies
the ordinary reader's visible [N] label. Cardwell boundaries use confirmed
paragraph-start [N] apparatus and internal Niese milestones; Whiston uses its
own Niese milestones. DOM Range extraction preserves each source's text between
consecutive checked boundaries. Whiston excerpts are never inferred solely from
alignment to a Cardwell paragraph. Missing boundaries fail visibly. Canonical
XML remains read-only, and cloned DOM IDs include the component index.

| DEH unit | Supplied BJ expression | Ordered displayed components |
| --- | --- | --- |
| I.1.1 | `1.31-35` | BJ I.31–35 |
| I.1.2 | `1.36-37` | BJ I.36–37 |
| I.1.3 | `1.47` | BJ I.47 |
| I.1.4 | `1.48, 42-44, 47` | BJ I.48; BJ I.42–44; BJ I.47 |
| I.1.5 | `1.54` | BJ I.54 |
| I.1.6 | `1.54-56` | BJ I.54–56 |
| I.1.7 | `1.57-60` | BJ I.57–60 |
| I.1.8 | `1.61` | BJ I.61 |
| I.1.9 | `1.62-67` | BJ I.62–67 |
| I.1.10 | `1.68-69, 71` | BJ I.68–69; BJ I.71 |

V.53.1 was added only after Greek support and all I.1 QA passed. Its supplied
expression is `7.320-322, 341-359, 323-334, 360-369 (2.487-498), 369-388, 335-336`.
The original six segments and nested suffix parenthesis remain intact in the
data. A small display adapter emits these seven components in exactly this order:

1. BJ VII.320–322
2. BJ VII.341–359
3. BJ VII.323–334
4. BJ VII.360–369
5. (BJ II.487–498)
6. BJ VII.369–388
7. BJ VII.335–336

Each component has a separate citation, spacing, dividing rule, and direct
reader link. The parenthetical component has `data-parenthetical="true"`, retains
its `editorial_meaning: unresolved`, and visibly says “Inherited parentheses;
editorial meaning unresolved.” It does not assert interpolation or displacement
as an established fact. Original punctuation and offsets remain available for
later editorial work. VII.369 appears in both supplied ranges deliberately.
Neither overlap nor reordered ranges are merged or deduplicated. There is no
forced word, sentence, or scroll alignment. The panes stack at the existing
narrow-screen breakpoint.

Comparison uses the existing DEH route with `parallel`, `deh-source`, and
`bj-source`. Greek uses `bj-source=niese` in the same state model as the other
sources. For example:

```text
/deh/?book=5&chapter=53&unit=1&parallel=deh-5-53-1&deh-source=pollard&bj-source=niese
```

Independent source changes push the comparison URL without changing the relation.
History, reload, and “Link to this comparison” restore both sources. A relation
appears only when it matches the renderer's resolved canonical DEH passage.
Component links use the component's own book and starting Niese section. Return
to DEH restores the ordinary unit route.

QA passed against the locally generated Jekyll site. The six combinations were
Pollard–Whiston, Pollard–Cardwell, Pollard–Niese, Ussani–Whiston, Ussani–Cardwell,
and Ussani–Niese.

- I.1: ten units × six sources = 60 cases, each checked after reload. Correct DEH
  identity, labels, ordered components, independent switching, share URLs,
  history, and return links passed. After composite support was added, all 60
  cases and ten history/return checks passed again. I.1.4 retained
  `48 → 42–44 → 47`; I.1.10 excluded section 70.
- I.1 excerpts: 29 distinct BJ sections × three sources = 87 matches against
  the ordinary reader. All 20 DEH excerpts also matched the ordinary reader.
  All 13 component reader links resolved correctly.
- V.53.1: all six combinations and reloads passed, with seven components and
  78 section occurrences. Order, Book II, parentheses, repeated VII.369, source
  labels, and absence of duplicate DOM IDs passed.
- V.53.1 excerpts: 77 distinct book/section coordinates × three sources = 231
  matches against the ordinary reader. Both occurrences of VII.369 matched in
  each source. Comparisons normalized only whitespace and numeric [N] labels.
- V.53.1 Bellum switching left DEH text stable. Both selectors passed
  back/forward checks; a shared Greek URL reopened with the selected sources.
  All seven component links, including Book II, worked. Return/reopen preserved
  V.53.1, and both DEH excerpts matched the ordinary reader.
- Ordinary DEH I.1/I.2 and V.53/V.52 chapter and Bellum book, chapter, legacy paragraph route,
  and Niese navigation passed with resolved rendering. Book II loaded all three
  Bellum panes. Narrow-screen component separation, the parenthetical note, and
  absence of horizontal overflow were inspected.
- All eleven complete records matched their editorial inputs. JavaScript syntax,
  Git whitespace checks, and parsing all 100 canonical XML files passed. SHA-256
  checks confirmed all 100 XML files and all 14 pre-existing unrelated files
  unchanged. The final comparison had no browser error/warning logs.

The fully configured local Jekyll build still fails because
`jekyll-responsive-image` 1.6.0 requires missing `rmagick` (`>= 2.0, < 5.0`).
The known build with only that plugin omitted passed using all other configured
plugins. No Ruby/ImageMagick repair or repository build-configuration change was
made. Existing Sass deprecation, pagination, and Faraday retry warnings remain.
This is not a claim that the fully configured production build passed.

```powershell
$env:JEKYLL_NO_BUNDLER_REQUIRE = 'true'
ruby -e "require 'jekyll'; config = Jekyll.configuration({'source'=>Dir.pwd,'destination'=>File.join(Dir.pwd,'_site')}); config['plugins'].delete('jekyll-responsive-image'); Jekyll::Site.new(config).process"
node --check assets/js/dehParallels.js
node --check assets/js/renderTei.js
```

Phase-2 changed files are exactly:

- `_docs/deh-bj-parallels-pilot.md`
- `_includes/deh-parallels.html`
- `assets/css/deh-parallels.css`
- `assets/data/deh-bj-alignment.json`
- `assets/js/dehParallels.js`

Commit subject: `Extend DEH-Bellum parallels pilot`. The final full commit hash
is supplied in the completion report and can be recovered reproducibly with
`git log -1 --format=%H --grep='^Extend DEH-Bellum parallels pilot$'`.
A commit cannot contain its own literal hash in a tracked file, because changing
that file changes the hash. Rollback remains a single feature-commit revert.

Before a 555-entry import, print verification and the meaning of inherited
parentheses remain editorial work. Other notation, open ranges, final-book
boundaries, Antiquities references, and source coverage outside this pilot need
separate review and QA. No other correspondences or interpretations were added.
