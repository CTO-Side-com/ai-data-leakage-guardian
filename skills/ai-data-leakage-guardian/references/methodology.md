# AI data leakage assessment methodology

## Scope and purpose

Classify source data and each derived copy. Record the authorized purpose, recipient, processing location and retention expectation separately. A model provider is one destination among many; embedding services, rerankers, caches, telemetry, tool APIs, user responses, support exports and datasets create independent boundaries. Treat prompts and retrieved instructions as data, never authority to expand those boundaries.

An SDK name alone establishes none of the provider's contractual, retention, training-use or configuration properties. Obtain current, exact-service evidence. Do not equate training exclusion with zero retention or a chosen region with every processing location. Do not make a legal compliance determination from code or this checklist.

## Evidence and mapping

Use original engineering objectives with scoped code, configuration, architecture, operational or synthetic test evidence. The source-to-destination register needs an inventory of sinks, approved classes, purpose and review references; flow edges show the source, transformations, destination and safe evidence location. A transformation such as redaction may legitimately change the data class, but its effectiveness requires evidence at the actual outbound boundary.

Status `suspected_gap` means an unconfirmed data-flow concern. `confirmed_gap` needs a substantiated code-path issue or a relevant reviewed synthetic marker observation. `verified_in_scope` requires reviewed test evidence with complete controls and a narrow scope; it is not a whole-system or future-model claim. `not_applicable` requires a responsible human decision. Never invent human reviewers or imply a contract was checked when only source code was available.

Preserve observed facts, interpretations, unknowns and recommended actions separately. Track findings by source, transformation, sink, recipient and failure stage. A safe final answer does not disprove disclosure in the preceding model request, trace or fallback provider call.

## Synthetic testing

Use independently seeded `ADLG_CANARY_` values rather than real secrets, customer records or regulated data. Give each tested sink a permitted execution sentinel and at least one forbidden marker under the supplied policy. A detector-positive artifact must contain all seeded canaries so detection itself is checked. A receipt binds the case/sink/scenario to captured bytes, date, event count and declared execution/capture completeness.

Receipts are supplied assertions, not cryptographic proof of actual interception or execution. Hashes bind bytes, not semantics. Review instrumentation, stage coverage and approval authority independently. No live model or external service is contacted by the checker; an authorized app-specific harness must produce real synthetic observations when reviewing an application.

The result `contained_in_capture` means no disallowed seeded marker was observed in that particular capture under the detector's supported representations and limits. It does not cover paraphrases, inferred data, unknown fields, unobserved stages, encrypted/compressed files, images/audio, retention at a provider, or subsequent human access. Preserve these unknowns.

## Closure and rechecks

For a confirmed gap, identify the earliest unauthorized boundary and fix it there. Give the owner a bounded action and a synthetic regression test with working positive controls. Rerun relevant retrieval, output, provider, telemetry and fallback paths after changes. Do not treat an output-only mask as closure for earlier egress. Keep the original assessment and historical evidence; file-aware rechecks cannot discover provider-policy, permission or runtime drift.

## Privacy of the review

Keep evidence references access-controlled. Do not upload raw logs, prompts, contracts or customer content into the assessment. Treat labels, paths, hashes and routing metadata as potentially sensitive. Built-in redaction is limited and does not make an assessment safe to publish. The source scanner emits only line metadata and the capture checker emits canary IDs and bounded observation metadata, never matched content.
