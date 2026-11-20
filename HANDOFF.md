---
status: active
phase: v1.0.0 · Publishing
next: DLG-5 · Whole-branch review
tests: local 90/90 on macOS 3.13.0 and 3.9.6 with TMPDIR on a real folder; 47/90 pass (43 errors) under the default macOS TMPDIR (2026-11-21)
updated: 2026-11-21 00:27 +0400
---
# AI Data Leakage Guardian: handoff

## Current state

- Local git repository on `main`, not yet pushed. Target: public
  `https://github.com/CTO-Side-com/ai-data-leakage-guardian`, homepage ctoside.com, like the siblings
  Tenant Guardian, SOC 2 Engineering Guardian and HIPAA Guardian (all public in CTO-Side-com).
- History: `58ca990` imports v1.0.0 exactly as received (folder dated 2026-11-20); `cd8237f`
  marketplace rename (DLG-3); `1b22d78` CI runner pin (DLG-4); then the README, report preview and
  this file (DLG-2).
- 2026-11-21 session: README rewritten after the Tenant Guardian README, with an ASCII banner (a
  "leak" drip under LEAKAGE) and four ASCII diagrams in place of the siblings' SVG infographics, plus
  `docs/images/report-preview.png` (pages 1, 3 and 9 of the example PDF). No code, test or example
  output changed.

## What's working

- 37 objectives in 8 areas (MAP 4, PROMPT 5, RAG 5, EGRESS 5, OBS 5, PROVIDER 5, TOOL 4, LIFE 4),
  each ending in one of five conclusions that `guardian.py validate` enforces, plus a sink and
  data-flow register.
- `scripts/guardian.py`: init, scan (12 rules, file and line only), plan, validate, report
  (Markdown, PDF, risk register, redacted assessment, hashed manifest), tasks (Jira, Notion, Slack
  Lists, Slack text, Markdown), recheck.
- `scripts/canary_audit.py`: offline synthetic capture audit; receipt, positive control and
  execution sentinel gate every case; `leak_observed` / `contained_in_capture` / `inconclusive`.
- Tests: 90 in `skills/ai-data-leakage-guardian/tests`. 90/90 on Python 3.13.0 and 3.9.6 with
  `TMPDIR` on a real folder. `docs/build_example.py` rebuilt the example on a scratch copy: only the
  random canary values and the hashes that depend on them differ from the shipped `docs/example`.
- README: 36/36 local links and anchors resolve (scratch check); every box diagram row matches its
  border width; no double-width characters in any text block.

## Known problems

- **macOS default `TMPDIR` breaks the tests and the example build.** `output()`
  (`scripts/guardian.py:24`) refuses a symlink anywhere above the path, and macOS `/var` and `/tmp`
  are symlinks, so 43 of 90 tests error with "Symlink output paths are refused" and
  `python3 docs/build_example.py` fails the same way. Ubuntu CI is unaffected. README tells macOS
  users to set `TMPDIR`. Tenant Guardian fixed the same guard in TG-6 (refuse the file, its folder
  and links inside the working directory only).
- **Email redaction is quadratic.** `clean()` (`scripts/guardian.py:33`): 0.29 s on 10k chars of
  `a.`, 1.15 s on 20k, 4.65 s on 40k (measured 2026-11-21). Tenant Guardian TG-8 replaced the same
  pattern.
- **Redaction is narrow.** Only emails, SSN-format IDs, `Bearer` values and bare
  `password`/`secret`/`token`/`api_key` labels. `DB_PASSWORD=`, `access_token=`, quoted JSON keys,
  `api-key`, phones, URL passwords, private keys and provider key shapes pass through; `logo@2x.png`
  is masked. Verified 2026-11-21 on 3.9.6 and 3.13.0; README lists it exactly.
- **Recheck `**` is not recursive.** `PurePosixPath.match` treats `**` like `*` on 3.9 and 3.13, so
  `backend/**` misses `backend/api/app.py` (fails open for that objective). README says so. Tenant
  Guardian fixed this in TG-7.
- Scanner skip list is exact, case-sensitive folder names (`SKIP` in `scripts/guardian.py:156`).
- Example data-flow `FLOW-MODEL` cites `assets/demo_pipeline.py` while `FLOW-TRACE` cites the full
  `skills/ai-data-leakage-guardian/assets/demo_pipeline.py` (comes from `assets/assessment-example.json`).
- CI rebuilds the example without diffing it against `docs/example/`.

## Needs you

- [ ] 2026-11-21 · Port Tenant Guardian's v1.0.1 fixes (output guard, recursive `**` in recheck,
  linear and wider redaction, macOS CI job) as v1.0.1 here? (recommended: yes, as one release with
  tests watched red first)

## Tasks

| ID | Task | Status | Started | Finished |
|---|---|---|---|---|
| DLG-1 | Import v1.0.0 as received | done | 2026-11-21 00:16 | 2026-11-21 00:17 |
| DLG-2 | README with ASCII art, report preview, HANDOFF | active | 2026-11-21 00:17 | |
| DLG-3 | Rename marketplace to ctoside-leakage | done | 2026-11-21 00:25 | 2026-11-21 00:25 |
| DLG-4 | Pin CI runner to ubuntu-24.04 | done | 2026-11-21 00:25 | 2026-11-21 00:25 |
| DLG-5 | Whole-branch review | todo | | |
| DLG-6 | Create the GitHub repo, push, confirm CI and `gh skill install` | todo | | |

## Regenerate the README preview

Rendered from `docs/example/AI-DATA-LEAKAGE.pdf` with poppler's `pdftoppm -r 110` (pages 1, 3, 9),
then composed on a `#F4F3EF` canvas with soft shadows and quantized to 128 colours with Pillow, as
the sibling previews are. Rebuild it whenever the example PDF changes.

## Next steps

1. Commit README, `docs/images/report-preview.png` and this file (DLG-2).
2. Run the whole-branch review (DLG-5); apply its fixes in their own commits.
3. Create `CTO-Side-com/ai-data-leakage-guardian` (public, description and topics like the
   siblings), push `main`, wait for CI, check the badge, and install with `gh skill install` into a
   scratch `--dir` (DLG-6).
4. Record the CI run and live URL in the front matter and Current state.
