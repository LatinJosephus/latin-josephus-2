# LatinJosephus public preview: publishing handoff

Verified 24 October 2026 by MilletWorkBot2, from the editor's explicit identification of the preview, existing Git remotes and the previous release publisher. Keep this reference with the project so a successor does not need to rediscover the hosting arrangement.

## Repositories and destinations

| Purpose | Repository | Branch / address |
| --- | --- | --- |
| Development source | https://github.com/LatinJosephus/latin-josephus-2.git | `v2-development` |
| Public preview, generated static files | https://github.com/LatinJosephus/LatinJosephus.github.io.git | `main` |
| Preview website | https://latinjosephus.github.io/ | GitHub Pages |
| Preview DEH reader | https://latinjosephus.github.io/deh/ | Same static Pages publication |

The preview does **not** deploy automatically from the development repository. The source repository also has an upstream remote, `https://github.com/performant-software/latin-josephus-2.git`; that remote and the source `master` branch are not the preview publishing targets. The production domain `www.latinjosephus.org` is a separate destination and is outside the Millet preview request.

Known local checkouts:

- Source: `C:\Users\Pollard_R\Git\LatinJosephus-v2-development`.
- Existing preview publisher target: `C:\Users\Pollard_R\Git\LatinJosephus-preview-Ant-I-X-20261020-095544`.
- Older preview checkout: `C:\Users\Pollard_R\Git\LatinJosephus-pages-preview`.
- Isolated Millet source worktree: this project's `worktrees/millet1556-deh`.

Do not assume that a local branch equals the published head. The previous publisher deliberately preserved original checkouts and pushed prepared commit objects without moving their local branches.

## Established release procedure

The previous reviewed publisher is preserved at `C:\Users\Pollard_R\Downloads\LatinJosephus-De-Excidio-English-Search`: `Publish-De-Excidio-English-Search.ps1`, `publish-de-excidio-english-search.mjs` and `release.json`. These are historical reference material, not a command to replay that old release.

Its final source commit was `e3fe7b1a677dd340d707d544bdb7e90bc84a08cb`; its final preview commit was `cd0ccb63deda3bceb0bd495944b7d57e3f00cf24`. Both remote heads were verified at these values on 24 October before preparing the Millet release. The preview tree was `b5831a8b781ccec95a4c630fdc4b6684ee2510ab`.

Follow the same two-repository procedure:

1. Read the live remote branch heads. Snapshot the original repositories' local heads, status, index, configuration and working files. Preserve unrelated work.
2. Finish and test the exact source commit in an isolated worktree. Build the static site, run the existing publication/corpus gates, and prepare a separate preview commit directly atop the current live preview `main`.
3. Review every static output difference. Preserve unrelated published files, search data, all scholarly inputs and exact character-offset assets. Do not publish private recovery material merely because Jekyll copied it into a local build.
4. Preserve `.nojekyll`. The verified preview tree has no `CNAME`; do not copy the production-domain `CNAME` from the local build into this preview repository.
5. Record the source and preview commit/tree IDs, exact file hashes, tests and rollback bases. Recheck live heads immediately before release; an unexpected change requires reassessment.
6. After the editor authorises publication of the prepared candidate, push the exact source commit to source `v2-development`, then the exact static preview commit to preview `main`. Use normal non-forced pushes, with mirror mode, follow-tags and submodule recursion disabled. Verify the resulting remote heads. A completed first target can be skipped on a verified retry.
7. Verify the GitHub Pages `pages-build-deployment` result and the public URLs and assets. A successful Git push alone does not certify that Pages has served the new version.

The existing `bin/deploy` script is **not** this procedure: it defaults to `master`/`gh-pages`, rewrites a checkout and force-pushes. Do not use it for the separate public preview.

## Millet release preservation and QA

Keep the frozen Millet/Ussani master, original PAGE XML, source-line payloads, canonical mappings and offsets unchanged. Publish the nine intended slim `assets/data/deh-millet1556` assets with the reader runtime and generated pages; do not publish the multi-gigabyte transcription evidence or recovery archives.

The prepared Millet implementation includes all 558 Ussani units and 19,104 source-line payloads. Its local records contain the build/corpus checks, all-unit and whole-chapter browser regressions, compact-interface screenshots and preservation hashes. The pre-existing AJ Latin comparison hash-pin limitation remains documented; changing scholarly pins is outside this interface release.

The release comparison found an important difference between the two repositories: preview `cd0ccb63` already contains an Antiquities book-numbering display-copy helper absent from source `e3fe7b1`. The isolated Millet source now carries that existing published helper and its call unchanged. Against the published runtime, the combined `renderTei.js` retains every original line and adds only the eighteen Millet integration lines in three insertions. This preserves existing preview behaviour rather than replacing it with the older source version. No scholarly XML or numbering authority is edited.

The scoped static candidate updates the DEH reader, its edition guide, the three reader JavaScript files, Millet stylesheet and nine Millet data assets. Existing non-DEH pages, search, publication receipts, XML, `.nojekyll`, preview metadata and historical review files remain at their published bytes. Do not mirror the entire local Jekyll output over the preview: that output also contains a production `CNAME`, production-domain feed/sitemap and local review artefacts.

Release evidence belongs in a new dated directory under `outputs/Millet_Site_Integration/`. Preserve previously issued evidence and receipts. Include exact candidate IDs and the actual publication state there; this handoff is not evidence that a public deployment has occurred.

## Approval boundary

On 24 October the editor supplied the preview details and instructed: "Continue with local testing and certification. Do not push to the public preview without my explicit approval." Prepare a concrete, certified candidate before requesting any outstanding release approval. Do not infer permission to deploy production or alter scholarly data from permission to publish the preview.
