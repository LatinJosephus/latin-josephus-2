# Source TOC typography refinement — 8 October 2026

GO for human browser review. The production patch adds three lines to `assets/css/tei.css`. All other 468 tracked files remain byte-identical to the worktree baseline.

## Isolation and cause

Base: `1cf003beeb03f7b0acf2c42057ace062cdb7ebff`. Branch: `codex/source-toc-typography`. Worktree: `C:\workspace\LatinJosephus-source-toc-typography`. Canonical `v2-development` and `origin/v2-development` still equal the base, and canonical is clean. The completed TOC worktree and historical reviews remain unchanged.

`_sass/_typography.scss` registers existing local regular, italic and bold fonts as `"LJ Coelacanth"` and defines `--lj-font-text: "LJ Coelacanth", Georgia, "Times New Roman", serif`. Ordinary `tei-p` and `tei-head` explicitly use that stack. Greek narrative uses this same existing stack and its Unicode fallbacks; no separate Greek-only font is registered.

The book layout loads MDB after the main stylesheet. MDB sets the body font to `Roboto, sans-serif`. Contents fragments sit outside `tei-text`, so list entries and Lodge TCP headings inherited this sans-serif body font. Some TEI paragraphs/headings already had the explicit reader-font rule, producing mixed typography.

## Scoped correction

```css
.source-contents {
  font-family: var(--lj-font-text);
}
```

This sets the existing reader font on the contents wrapper and its inheriting descendants. No font files, font loading, JavaScript, XML, registry, source numeral, ID, sameAs, segmentation, Sass, template or navigation code changed. Existing italic selectors remain untouched; Chrome confirms the actual `Coelacanth-It` face for supplied passages.

Only font family is set. Font sizes, spacing, indentation, weights, colours and theme behaviour are preserved. Different line wrapping follows naturally from the requested typeface; no extra layout adjustment was required.

## Computed fonts

Full computed styles and actual platform-font records for representative source headings, entries, numerals and supplements are in `COMPUTED_FONTS.json` and `BROWSER_QA.json`. The following entry samples are representative. Both themes produce the same font families.

| Source sample | Before | After | Ordinary Chapter text |
| --- | --- | --- | --- |
| antiquities-III / Latin | `Roboto, sans-serif` | `"LJ Coelacanth", Georgia, "Times New Roman", serif` | `"LJ Coelacanth", Georgia, "Times New Roman", serif` |
| antiquities-V / Latin | `Roboto, sans-serif` | `"LJ Coelacanth", Georgia, "Times New Roman", serif` | `"LJ Coelacanth", Georgia, "Times New Roman", serif` |
| antiquities-V / Greek | `"LJ Coelacanth", Georgia, "Times New Roman", serif` | `"LJ Coelacanth", Georgia, "Times New Roman", serif` | `"LJ Coelacanth", Georgia, "Times New Roman", serif` |
| antiquities-XIV / Latin | `Roboto, sans-serif` | `"LJ Coelacanth", Georgia, "Times New Roman", serif` | `"LJ Coelacanth", Georgia, "Times New Roman", serif` |
| antiquities-XIV / Greek | `"LJ Coelacanth", Georgia, "Times New Roman", serif` | `"LJ Coelacanth", Georgia, "Times New Roman", serif` | `"LJ Coelacanth", Georgia, "Times New Roman", serif` |
| bellum-Lodge-I / English | `Roboto, sans-serif` | `"LJ Coelacanth", Georgia, "Times New Roman", serif` | `"LJ Coelacanth", Georgia, "Times New Roman", serif` |

Latin III/XIV TEI headings already used Coelacanth. Lodge's source heading changes from Roboto to Coelacanth. Greek source headings are first paragraphs, and their existing reading stack remains unchanged. Source numerals inherit the reader stack. Latin III's 42 italic nodes and XIV's 8 supplied numeral nodes remain italic in both themes. These are display-node counts, not a fresh source adjudication; XIV editorial numerals remain distinct from Blatt supplements. Latin/English contents keep 16px text and Greek paragraphs keep 18px.

## QA

- 16/16 contents scenarios pass: the four requested cases, in light and dark themes, before and after; eight before/after pairs. Antiquities V/XIV include Latin and Greek checks.
- 16/16 ordinary Book/Chapter comparisons pass: exact pane HTML, text, computed styles, actual font usage and navigation-control fonts match. 16/16 final visible reading-area pixel hashes also match.
- Source contents text is identical. Genuine italics and Blatt supplements remain visibly distinguished; XIV supplied numerals retain brackets.
- All eight final after views were visually inspected. No horizontal overflow or illegible text was observed at 1600 x 1050. Colours are unchanged; measured entry contrast ranges from 11.85:1 to 14.05:1, exceeding WCAG AA's 4.5:1 normal-text threshold.
- No browser page errors or failed requests in the final run.
- All 114 XML files, 9 font assets and 187 historical review files are byte-identical. All 469 canonical tracked files match their own preflight hashes.

The reproducible browser test uses the actual renderer and XML in a local fixture with the existing compiled main stylesheet, local fonts and the existing layout's MDB/Roboto URLs. It compares the exact before stylesheet against the patched stylesheet. Readiness/state instrumentation is in memory only. No site build or deployment was performed. Initial fixture diagnostics are preserved separately; final results are in `BROWSER_QA.json`.

## Before/after screenshots

| Case | Light | Dark |
| --- | --- | --- |
| Antiquities III | [Before](antiquities-III_light_before.png) · [After](antiquities-III_light_after.png) | [Before](antiquities-III_dark_before.png) · [After](antiquities-III_dark_after.png) |
| Antiquities V | [Before](antiquities-V_light_before.png) · [After](antiquities-V_light_after.png) | [Before](antiquities-V_dark_before.png) · [After](antiquities-V_dark_after.png) |
| Antiquities XIV | [Before](antiquities-XIV_light_before.png) · [After](antiquities-XIV_light_after.png) | [Before](antiquities-XIV_dark_before.png) · [After](antiquities-XIV_dark_after.png) |
| Bellum I, Lodge | [Before](bellum-Lodge-I_light_before.png) · [After](bellum-Lodge-I_light_after.png) | [Before](bellum-Lodge-I_dark_before.png) · [After](bellum-Lodge-I_dark_after.png) |

## Changed-file SHA-256

`assets/css/tei.css`:

- Before: `9c25a64aebba4c28c13b5ce0ff60b837fe5b850395702f43762e480193c1a96c` (2,485 bytes).
- After: `f69cd787e47351d1dbf083097ecc3b037791a05309761d865a2e237ac91afeda` (2,542 bytes).

`FILE_MANIFEST.json` hashes the production edit and all new review artifacts except itself. Changes remain unstaged and uncommitted. No merge, push or Git configuration change occurred.
