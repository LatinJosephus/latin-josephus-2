# LatinJosephus Pages publishing handoff

The separate Pages repository became the production site on 9 November 2026. It publishes from the root of `main` with `www.latinjosephus.org` as its custom domain. The release procedure below follows the preview handoff verified on 24 October 2026.

## Repositories and destinations

| Purpose | Repository | Branch / address |
| --- | --- | --- |
| Development source | https://github.com/LatinJosephus/latin-josephus-2.git | `v2-development` |
| Production, generated static files | https://github.com/LatinJosephus/LatinJosephus.github.io.git | `main` |
| Production website | https://www.latinjosephus.org/ | GitHub Pages |

Publish the generated site to the separate Pages repository. Use `LatinJosephus/latin-josephus-2` and `v2-development` for source changes.

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

1. Read the live remote branch heads and Pages settings. Snapshot the original repositories' local heads, status, index, configuration and working files. Preserve unrelated work.
2. Finish and test the exact source commit in an isolated worktree. Build the static site with `bundle exec jekyll build` and run the existing publication and corpus gates. Fetch `main` in an isolated Pages checkout and fast-forward it to include any remote changes, including commits to `CNAME`.
3. Copy only reviewed build outputs into the Pages checkout and review every static difference. Preserve unrelated published files, search data, all scholarly inputs and exact character-offset assets. Keep private recovery material out of the publication.
4. Keep the root `CNAME` and `.nojekyll` from the Pages checkout. Exclude both paths from the copy and verify both are unchanged in the publication diff. `CNAME` must contain exactly `www.latinjosephus.org`.
5. Record the source and Pages commit/tree IDs, exact file hashes, tests and rollback bases. Recheck live heads immediately before release and review any unexpected change before proceeding.
6. After the editor authorises publication, push the exact source commit to `v2-development`. Use the required check below to publish the exact static commit to Pages `main`. Use normal non-forced pushes with mirror mode, follow-tags and submodule recursion disabled. Verify the resulting remote heads. A completed first target can be skipped on a verified retry.
7. Verify the GitHub Pages `pages-build-deployment` result, the custom domain in Pages settings, and the live HTTPS URLs and assets.

Use the separate-repository procedure for this site. The legacy `bin/deploy` script rewrites a checkout and force-pushes to a branch of the source repository.

### Required check before the Pages push

In PowerShell, run this block from the source checkout with `$pagesCheckout` set to the separate Pages checkout and `$pagesCommit` set to the full SHA of the reviewed static commit. The check reads both files from the commit being pushed and stops the push if either is missing or `CNAME` has different bytes.

```powershell
node bin/check-pages-domain.mjs $pagesCheckout $pagesCommit
if ($LASTEXITCODE -ne 0) { throw 'Pages domain check failed' }
git -C $pagesCheckout -c remote.origin.mirror=false push --no-follow-tags --recurse-submodules=no origin "${pagesCommit}:refs/heads/main"
if ($LASTEXITCODE -ne 0) { throw 'Pages push failed' }
```

During the next routine update, remove `deployment-check-20261109.txt` from the root of both the source repository (`v2-development`) and the Pages repository (`main`). Leave the test file live until that update.

## Historical Millet release preservation and QA

Keep the frozen Millet/Ussani master, original PAGE XML, source-line payloads, canonical mappings and offsets unchanged. Publish the nine intended slim `assets/data/deh-millet1556` assets with the reader runtime and generated pages; do not publish the multi-gigabyte transcription evidence or recovery archives.

The prepared Millet implementation includes all 558 Ussani units and 19,104 source-line payloads. Its local records contain the build/corpus checks, all-unit and whole-chapter browser regressions, compact-interface screenshots and preservation hashes. The pre-existing AJ Latin comparison hash-pin limitation remains documented; changing scholarly pins is outside this interface release.

The release comparison found an important difference between the two repositories: preview `cd0ccb63` already contains an Antiquities book-numbering display-copy helper absent from source `e3fe7b1`. The isolated Millet source now carries that existing published helper and its call unchanged. Against the published runtime, the combined `renderTei.js` retains every original line and adds only the eighteen Millet integration lines in three insertions. This preserves existing preview behaviour rather than replacing it with the older source version. No scholarly XML or numbering authority is edited.

The scoped static candidate updates the DEH reader, its edition guide, the three reader JavaScript files, Millet stylesheet and nine Millet data assets. Existing non-DEH pages, search, publication receipts, XML, `.nojekyll`, preview metadata and historical review files remain at their published bytes. Do not mirror the entire local Jekyll output over the preview: that output also contains a production `CNAME`, production-domain feed/sitemap and local review artefacts.

Release evidence belongs in a new dated directory under `outputs/Millet_Site_Integration/`. Preserve previously issued evidence and receipts. Include exact candidate IDs and the actual publication state there; this handoff is not evidence that a public deployment has occurred.

## Approval boundary

On 24 October the editor supplied the preview details and instructed: "Continue with local testing and certification. Do not push to the public preview without my explicit approval." Prepare a concrete, certified candidate before requesting any outstanding release approval. Do not infer permission to deploy production or alter scholarly data from permission to publish the preview.
