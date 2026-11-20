# Offline synthetic capture workflow

## Manifest

Use the bundled capture-manifest.json as a shape reference. Declare `synthetic_only: true`, environment local/test/staging, scenario ID, policy reference and actual policy reviewer. Define two to thirty-two distinct synthetic canaries, up to thirty-two destination policies and up to sixty-four cases. Each canary needs an ID, classification and a unique `ADLG_CANARY_` value. Overlapping values are refused.

Each sink declares exactly which marker IDs it allows and a policy approval reference. Each case declares its sink, capture path, detector-positive path, receipt path and at least one permitted required execution sentinel. Include at least one forbidden marker for a meaningful containment case. For an otherwise fully authorized dataset, add a distinct restricted fixture field or choose another objective rather than inventing a violation.

All capture paths are relative to the approved root. Dot paths, traversal, absolute paths, backslashes, symlinks and known credential-file basenames are refused. Only explicitly supplied files are opened; the checker does not crawl log directories. A dry run validates the manifest without reading captures.

## Execution receipt

Provide a JSON receipt with the exact scenario_id, case_id, sink_id, capture_sha256, capture_bytes, positive integer event_count, execution_complete: true, capture_complete: true, synthetic_only: true, observed_on and instrumentation_ref. Hashes use the exact captured bytes. The observation date cannot be in the future. Bind the receipt to the actual tested boundary; a generated request object before the SDK call is a different observation from the bytes handed to a provider or log exporter.

The source harness must honestly attest to completeness. An omitted or sampled sink cannot be assumed complete merely because a receipt says so. Review the harness and corroborate its execution when using results as assessment evidence. Captures and receipts can be forged; the tool makes no authenticity guarantee.

## Detector controls and limits

The positive-control artifact must expose every seeded canary to the same detector. The target capture must contain its allowed execution sentinel. Missing controls, empty captures, invalid receipts, mismatched hashes and missing/oversized artifacts produce inconclusive results. A forbidden-marker match remains visible as metadata even when incomplete controls prevent a supported leakage conclusion.

Exact marker matching examines literal bytes plus common URL, HTML entity, JSON ASCII escape, base64/base64url and hexadecimal representations. At most two decoding layers are expanded, with up to sixty-four candidate tokens per view, one MiB per artifact, 128 decoded views and eight MiB of decoded-byte work. Reaching supported-work limits prevents a clean containment result. Representation coverage is limited even when work limits are not reached. No semantic inference, arbitrary recursive decoding, archive expansion, decryption, image OCR or audio analysis is provided.

A valid controlled case with a forbidden marker yields leak_observed under the supplied destination policy. A valid controlled case with no forbidden marker and no work-limit exhaustion yields contained_in_capture for that capture only. No checker result updates the assessment or changes application code. Link reviewed observations manually with data_scope and sink_scope.

## Output

Outputs contain case/sink IDs, byte counts, hashes, marker IDs, transform labels, validity flags, reason categories and the canonical manifest SHA256. They exclude raw capture data, canary values, credential values and capture paths. The manifest hash uses sorted-key compact JSON; compare it with the exact approved manifest. Metadata remains sensitive and requires review before sharing.

The bundled demo_pipeline.py writes synthetic request/telemetry payloads, positive controls and receipts. It performs no network or AI calls. Safe mode emits only the permitted sentinel; leaky mode emits a forbidden marker in a base64 attachment and a trace field. Use fresh directories because fixture generation refuses overwrite.
