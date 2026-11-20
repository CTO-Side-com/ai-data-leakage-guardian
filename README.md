# AI Data Leakage Guardian

**Trace protected data through AI applications and test the boundaries with reviewed synthetic evidence.**

Built by [CTOside](https://ctoside.com). Python 3.9+, standard library only. Offline by default. The source is an installable coding-agent skill and a Claude Code plugin.

## Included

- 37 original objectives across data inventory, prompts, retrieval/memory, outbound routing, observability, provider review, tools/output and lifecycle.
- A source-to-destination register with approved data classes, purpose, review references and separate retention/training evidence.
- 12 conservative source/configuration heuristics. Findings contain file/line metadata, never matching source content.
- Offline synthetic capture auditing with execution sentinels, detector-positive controls, case-bound receipts and hash checks.
- Bounded exact-canary detection across literal, URL, HTML, JSON-ASCII, base64/base64url, MIME-wrapped base64 and hexadecimal representations.
- PDF/Markdown reports, risk register, hashed handoff manifest, Jira/Notion/Slack task files and change-aware rechecks.
- Safe and leaky synthetic offline fixtures, tests and reproducible examples. No AI provider or other external service is contacted by the supplied scripts.

This is engineering assurance support, not a production DLP gateway, general secret detector, legal opinion or confidentiality certification. A clean capture covers only known seeded markers, observed stages and supported representations. It cannot establish that an entire application or provider retains no sensitive data.

## Install from the source ZIP

Download and extract `AI_Data_Leakage_Guardian_Source.zip`. Open a terminal in the extracted `ai-data-leakage-guardian` folder and load the plugin:

```bash
claude --plugin-dir .
```

Inside Claude Code:

```text
/ai-data-leakage-guardian:ai-data-leakage-guardian
```

Alternatively, copy `skills/ai-data-leakage-guardian` to your coding agent's supported skills directory, retaining its LICENSE and bundled resources.

## Ask your agent

```text
Use AI Data Leakage Guardian to review this application read-only.
Map sensitive inputs through prompts, retrieval, embeddings, caches, tools,
model requests, user output, logs, traces, analytics and datasets.
Identify the authorized data classes and purpose for every destination.
Separate confirmed code-path issues, suspected gaps and unknown provider settings.
Produce a scoped data-flow register, regression plan, PDF report and tracker tasks.
Do not read real customer data or credentials, execute the app, or contact providers.
```

## Offline assessment commands

```bash
SKILL_DIR=skills/ai-data-leakage-guardian
python3 "$SKILL_DIR/scripts/guardian.py" init --product "My AI SaaS" --environment staging --out leakage-output/assessment.json
python3 "$SKILL_DIR/scripts/guardian.py" scan --repo . --out leakage-output/scanner-findings.json
python3 "$SKILL_DIR/scripts/guardian.py" plan --assessment leakage-output/assessment.json --out leakage-output/TEST-PLAN.md
# Review and populate the assessment using safe references and actual scoped evidence.
python3 "$SKILL_DIR/scripts/guardian.py" validate --assessment leakage-output/assessment.json
python3 "$SKILL_DIR/scripts/guardian.py" report --assessment leakage-output/assessment.json --out leakage-output/handoff --pdf
python3 "$SKILL_DIR/scripts/guardian.py" tasks --assessment leakage-output/assessment.json --out leakage-output/tasks
```

The agent reviews provider-specific settings using current official documentation and authorized configuration evidence. No provider retention, training, residency or agreement claim is inferred from SDK names. A raw-output option or training-file reference may be intentional and requires context.

## Synthetic capture demonstration

Use a fresh output directory. This generates only local synthetic files; it does not call a model:

```bash
python3 skills/ai-data-leakage-guardian/assets/demo_pipeline.py --out synthetic-safe-run --mode safe
python3 skills/ai-data-leakage-guardian/scripts/canary_audit.py --manifest synthetic-safe-run/manifest.json --dry-run
python3 skills/ai-data-leakage-guardian/scripts/canary_audit.py --manifest synthetic-safe-run/manifest.json --capture-root synthetic-safe-run --out synthetic-safe-observations.json
```

Repeat with a fresh directory and `--mode leaky` to demonstrate two disallowed canary observations, including a base64 attachment. The checker makes no network requests and performs no application execution. To assess your own app, an authorized synthetic test harness must instrument its actual outbound and retained-data boundaries.

Empty captures, missing positive controls, absent execution sentinels, invalid/incomplete receipts, mismatched hashes and unsafe or oversized artifacts remain inconclusive. Instrumentation receipts are supplied attestations, not proof of authenticity or completeness. A reviewer must validate their provenance and scope. Observations never update assessment conclusions automatically.

## Verification and examples

```bash
python3 -m unittest discover -s skills/ai-data-leakage-guardian/tests -v
python3 docs/build_example.py
```

The example builder generates safe and leaky captures, positive controls and receipts using owned synthetic data, then produces a clearly synthetic evidence-linked report and tasks. It contacts no real providers or customers. Generated fixtures are retained under docs/example so hashes and observations can be checked.

See [the synthetic report](docs/example/AI-DATA-LEAKAGE.md), [safe observations](docs/example/safe-observations.json), and [leaky observations](docs/example/leaky-observations.json). The report records two intentionally introduced fixture findings and leaves untested controls unverified.

## Limits and interpretation

Capture testing covers exact seeded markers through bounded supported transforms. It does not detect paraphrased or inferred information, unknown real secrets, encrypted/compressed artifacts, images/audio, provider retention, subsequent human review or stages that were never captured. Detector work limits and instrumentation completeness must be reviewed separately.

Redaction in exported reports is limited. Paths, labels, hashes and routing metadata can be confidential. Do not publish real assessments, receipts or captures. PDF uses Western built-in fonts; Markdown preserves Unicode. Provider and service documentation must be checked for the exact configured product and use.

The original objectives reference OWASP and NIST primary guidance without claiming endorsement or certification. MIT License.
