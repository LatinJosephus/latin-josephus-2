# Replaying integrated QA

The tested merge is 7dc8a633d76bff08f2d79b54bb04bc6e98d7918a. Review-only evidence is excluded from the native build. Use new isolated runtime/profile/destination paths for replay, never overwrite the preserved runtime.

Native builder: `ruby qa/build.rb SOURCE DESTINATION qa/local.yml`. Build frozen canonical cf4cdb90 separately and the integrated merge separately; record their destination paths in BUILD_CONTEXT.json. Set PLAYWRIGHT_MODULE to the installed Playwright library and REPAIR_RUNTIME/REPAIR_ROOT to isolated paths for common.cjs. All local servers use independent ports; no public writes occur.

Run `node qa/all-niese.cjs baseline` and `node qa/all-niese.cjs candidate-final` against those sites. Run the permanent `VII1-context-regression.test.cjs integrated`, then targeted-ui.cjs, containing-real.cjs and context-guards.cjs. `reader-structure-crosswork.cjs --final` uses disposable getter exports from qa-common18.cjs, no production function modifications. It runs every protected structural projection and cross-work source configuration; the all-niese script separately uses actual uninstrumented UI selection.

Run VII2-6-disposition.cjs for actual observed context gaps and containing views; VII2-6-resolver-proof.cjs supplies getter-only correspondence proof. source-facts.py records pinned XML/registry facts. compare.py builds the exhaustive matrix and exceptional-case index. integrity.py uses the original snapshot from INTEGRATION_START.json; its canonical-original check applies before canonical promotion. Post-promotion exact original source preservation is instead recorded by INTEGRATION_RECEIPT.json.

Raw full route exports, baseline fixture and start snapshot remain in C:/workspace/Antiquities-VII1-Whiston-Integration-runtime-20261010. Some copied harnesses retain fixed local runtime paths; adapt those in an isolated copy before replay. No test script is part of the production reader or run by the public site. New evidence includes no rerun of unsupported I.1, Home/About startup or inherited apparatus 404 checks.
