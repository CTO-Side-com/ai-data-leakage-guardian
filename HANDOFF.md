---
status: active
phase: v1.0.0 · Published
next: v1.0.1 candidates (Needs you)
tests: CI 90/90 on Ubuntu 24.04 × Python 3.9/3.11/3.13, run 44812780212 green; local 90/90 on macOS 3.13.0 and 3.9.6 with TMPDIR on a real folder, 43 errors under the default macOS TMPDIR (2026-11-21)
updated: 2026-11-21 00:36 +0400
live: https://github.com/CTO-Side-com/ai-data-leakage-guardian
---
# AI Data Leakage Guardian: handoff

## Current state

- Published 2026-11-21 00:36: public https://github.com/CTO-Side-com/ai-data-leakage-guardian (`origin`,
  branch `main`), MIT, homepage ctoside.com, topics agent-skills, ai-security, canary-testing,
  claude-code, claude-code-plugin, cursor, data-leakage, github-copilot, llm-security, privacy, rag,
  security-audit. Siblings: Tenant Guardian, SOC 2 Engineering Guardian, HIPAA Guardian.
- CI run 44812780212 on `f61ee48`: green on all 3 jobs (90 tests and the example build each); the
  README badge reads "passing". `gh skill install CTO-Side-com/ai-data-leakage-guardian
  ai-data-leakage-guardian --dir <scratch>` installed the 16 skill files at `f61ee48`.
- History: `58ca990` imports v1.0.0 exactly as received (folder dated 2026-11-20); `cd8237f`
  marketplace rename (DLG-3); `1b22d78` CI runner pin (DLG-4); `01b605a` README, report preview and
  this file (DLG-2); `f61ee48` review fixes (DLG-5); then this release record.
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
- README: 36/36 local links and anchors resolve (scratch check); box rows match their borders and
  connectors outside boxes were checked by column after DLG-5 found one off by 8; no double-width
  characters in any text block.

## Known problems

- **macOS default `TMPDIR` breaks the tests and the example build.** `output()`
  (`scripts/guardian.py:24`) refuses a symlink anywhere above the path, and macOS `/var` and `/tmp`
  are symlinks, so 43 of 90 tests error with "Symlink output paths are refused" and
  `python3 docs/build_example.py` fails the same way. Ubuntu CI is unaffected. README tells macOS
  users to set `TMPDIR`. Tenant Guardian fixed the same guard in TG-6 (refuse the file, its folder
  and links inside the working directory only).
- **Email redaction is quadratic.** `clean()` (`scripts/guardian.py:31`, email pattern at `:33`): 0.29 s on 10k chars of
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
- `claude plugin validate .` passes with two warnings, both from v1.0.0: the marketplace has no
  `description` and the plugin has no icon (DLG-5).

## Needs you

- [ ] 2026-11-21 · Port Tenant Guardian's v1.0.1 fixes (output guard, recursive `**` in recheck,
  linear and wider redaction, macOS CI job) as v1.0.1 here? (recommended: yes, as one release with
  tests watched red first)

## Tasks

| ID | Task | Status | Started | Finished |
|---|---|---|---|---|
| DLG-1 | Import v1.0.0 as received | done | 2026-11-21 00:16 | 2026-11-21 00:17 |
| DLG-2 | README with ASCII art, report preview, HANDOFF | done | 2026-11-21 00:17 | 2026-11-21 00:25 |
| DLG-3 | Rename marketplace to ctoside-leakage | done | 2026-11-21 00:24 | 2026-11-21 00:24 |
| DLG-4 | Pin CI runner to ubuntu-24.04 | done | 2026-11-21 00:24 | 2026-11-21 00:24 |
| DLG-5 | Whole-branch review | done | 2026-11-21 00:26 | 2026-11-21 00:35 |
| DLG-6 | Create the GitHub repo, push, confirm CI and `gh skill install` | done | 2026-11-21 00:35 | 2026-11-21 00:36 |

## Regenerate the README preview

Rendered from `docs/example/AI-DATA-LEAKAGE.pdf` with poppler's `pdftoppm -r 110` (pages 1, 3, 9),
then composed on a `#F4F3EF` canvas with soft shadows and quantized to 128 colours with Pillow, as
the sibling previews are. Rebuild it whenever the example PDF changes.

## Decisions

- 2026-11-21 00:35 · DLG-5 review (reviewer agent, `58ca990..01b605a`): ship after fixes, no blocker. Gate
  90/90 on 3.13.0 and 3.9.6 (real TMPDIR), example build on a copy differs only in canary values
  and their hashes, `gh skill install --from-local` landed in every folder the README names, 3/3
  plants caught by the README checker. Applied: workflow diagram drop moved to column 80 (S1),
  scanner rows narrowed to the calls and `=` the patterns match (S2), no local paths in this file
  (S3), and nits N1-N8 (report order, sentinel row, sink-allows-all wording, label masked with
  value, JSON walk limits, `canary_audit.py --out` overwrite, tagline width, line pointer).
  Unverified by the review: "gh 2.90 or later", the tracker import menus, whether Copilot and
  Cursor read the git-only skill folders.

## Next steps

1. Decide the Needs-you item (port Tenant Guardian v1.0.1 fixes as v1.0.1 here).
2. If yes: fix the output guard, recheck `**`, redaction (linear, wider), each with a test watched
   red first; add a macOS CI job; bump the manifests to 1.0.1; update README and this file.
