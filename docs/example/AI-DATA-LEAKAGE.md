# AI Data Leakage Guardian
Scoped AI data-leakage assessment. Not a guarantee of confidentiality, a production DLP gateway or compliance certification.

Product: Synthetic AI capture demonstration
Environment: local
Assessor: Automated offline synthetic demonstration; no customer application, provider or human approval was assessed
Data-handling model: Synthetic restricted inputs are intended to be redacted before request and telemetry capture
Systems: Owned offline payload and trace fixture
Exclusions: No real AI providers, production services or customer data
Scope unknowns: Live SDK interception, retained provider copies, semantic leakage and unobserved stages are untested.

## Source-to-destination register
Sink model_request | model_provider | approved | Synthetic request creation only | Retention evidence: Unknown | Training-use evidence: Unknown
Sink telemetry | observability | approved | Synthetic trace creation only | Retention evidence: Unknown | Training-use evidence: Unknown
FLOW-MODEL | synthetic user input -> intended sensitive-field redaction -> model_request | Data classes: restricted_synthetic, public_synthetic | Evidence: assets/demo_pipeline.py
FLOW-TRACE | synthetic pipeline context -> intended trace-field minimization -> telemetry | Data classes: restricted_synthetic, public_synthetic | Evidence: skills/ai-data-leakage-guardian/assets/demo_pipeline.py

## Confirmed findings and suspected gaps
PROMPT-003 | confirmed_gap | high | Apply redaction before external transmission | Remove the restricted fixture field before constructing the model-bound payload, including encoded attachments.
OBS-001 | confirmed_gap | high | Minimize or redact prompt and input logs | Allowlist trace fields and redact the restricted fixture field before trace export.

## Assessment matrix

### MAP-001 | Classify AI inputs and derived data
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Trace a synthetic confidential document and its derived fields through the AI pipeline.

### MAP-002 | Inventory model and non-model destinations
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Reconcile SDK/configuration paths with a reviewed sink register.

### MAP-003 | Map transformations and intermediate copies
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Trace a seeded canary through intermediate stages and inventory every copy.

### MAP-004 | Approve data classes per destination and purpose
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Review each source-transform-sink edge against a named approval and its evidence.

### PROMPT-001 | Keep credentials and protected configuration out of prompts
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Inspect prompt construction by reference and use synthetic secret-like markers to test exclusion.

### PROMPT-002 | Minimize sensitive input before model submission
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Seed a protected field beside an allowed control and inspect the outbound payload capture.

### PROMPT-003 | Apply redaction before external transmission
Status: confirmed_gap
Rationale: Only the deliberately leaky offline fixture violates the supplied synthetic policy; no real model or telemetry service was called.
Verified scope: None
Evidence: MODEL-LEAK
Reviewer: Automated synthetic demonstration; Owner: Synthetic fixture owner
Next action: Remove the restricted fixture field before constructing the model-bound payload, including encoded attachments.
Retest: Repeat the approved synthetic capture with valid receipts, complete detector-positive controls and an allowed execution sentinel; verify the forbidden canary is absent at this exact sink.

### PROMPT-004 | Bound conversation history and inherited context
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Seed an earlier synthetic restricted turn and examine a later request to another workflow.

### PROMPT-005 | Treat prompt confidentiality as insufficient authorization
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Test a synthetic instruction requesting a restricted field and inspect independent enforcement.

### RAG-001 | Authorize documents before retrieval or context assembly
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Index authorized and restricted synthetic documents and inspect retrieval plus final context.

### RAG-002 | Review embedding data and provider egress
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Trace a synthetic restricted marker into embedding requests and retained vector metadata.

### RAG-003 | Protect conversation and semantic caches
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Warm a synthetic cache under one identity and retrieve under another.

### RAG-004 | Constrain citations previews and source downloads
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Review synthetic citation metadata and attempt the source-download path through authorized tests.

### RAG-005 | Recheck preprocessing chunking and reranking
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Track an independently seeded marker through chunks, reranking and context trimming.

### EGRESS-001 | Inventory and constrain external endpoints
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Review configured endpoints and synthetic outbound captures for unregistered sinks.

### EGRESS-002 | Authorize tool and agent egress independently
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Use a synthetic injection requesting export to an unapproved sink and inspect the tool gate.

### EGRESS-003 | Protect transmission and provider routing configuration
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Review TLS verification, custom base URLs, gateways and environment-specific routes.

### EGRESS-004 | Exclude sensitive material from URLs headers and metadata
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Seed a synthetic marker and inspect body, query, headers and correlation metadata separately.

### EGRESS-005 | Review fallback retry batch and failover paths
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Force a synthetic primary failure and inspect all retry and fallback captures.

### OBS-001 | Minimize or redact prompt and input logs
Status: confirmed_gap
Rationale: Only the deliberately leaky offline fixture violates the supplied synthetic policy; no real model or telemetry service was called.
Verified scope: None
Evidence: TRACE-LEAK
Reviewer: Automated synthetic demonstration; Owner: Synthetic fixture owner
Next action: Allowlist trace fields and redact the restricted fixture field before trace export.
Retest: Repeat the approved synthetic capture with valid receipts, complete detector-positive controls and an allowed execution sentinel; verify the forbidden canary is absent at this exact sink.

### OBS-002 | Review model outputs and raw tool traces
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Seed a restricted synthetic tool response and inspect debug and completion captures.

### OBS-003 | Review SDK tracing and debug configuration
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Inspect actual approved configuration and synthetic traces for the deployed mode.

### OBS-004 | Constrain analytics and error-reporting payloads
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Trigger a synthetic exception and inspect analytics events, breadcrumbs and attachments.

### OBS-005 | Apply access retention and deletion to observability stores
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Review provider settings by dated evidence and exercise synthetic deletion where authorized.

### PROVIDER-001 | Confirm approved service model and account scope
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Reconcile configured service/model/account references with a reviewed approval record.

### PROVIDER-002 | Verify retention and training-use statements separately
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Record current service-specific documentation and configuration without inferring defaults.

### PROVIDER-003 | Review regional routing and subprocessors
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Review configured regions, routing layers and relevant subprocessor records.

### PROVIDER-004 | Review agreements access roles and shared responsibilities
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Request the responsible owner's approved evidence for the exact provider and service.

### PROVIDER-005 | Reassess provider configuration and policy changes
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Trace a synthetic configuration change to a renewed scoped review.

### TOOL-001 | Authorize final responses for the actual recipient
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Seed authorized and restricted records and inspect the recipient-visible output.

### TOOL-002 | Minimize tool results before model context
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Inspect synthetic raw and minimized tool captures before context assembly.

### TOOL-003 | Constrain streamed output attachments and previews
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Use synthetic markers in streamed chunks, files and previews; document unsupported media.

### TOOL-004 | Protect generated exports and shared conversation links
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Review synthetic export/share creation and retrieval through an approved fixture.

### LIFE-001 | Apply retention to inputs outputs caches and captures
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Map a synthetic record to retained copies and test approved disposal paths.

### LIFE-002 | Review training evaluation and fine-tuning datasets
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Trace synthetic restricted markers through dataset creation and file-upload paths.

### LIFE-003 | Review support incident and human-review access
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Follow a synthetic support case and inspect approved exports and access records.

### LIFE-004 | Track regressions after prompt model and integration changes
Status: insufficient_evidence
Rationale: No supported conclusion recorded.
Verified scope: None
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Next action: Collect scoped evidence and execute an authorized negative test.
Retest: Run scoped synthetic captures after a reviewed change and retain prior evidence.

## Evidence index
MODEL-LEAK | test | docs/example/leaky-observations.json | Synthetic model_request capture only | 2026-11-20
TRACE-LEAK | test | docs/example/leaky-observations.json | Synthetic telemetry capture only | 2026-11-20

Counts describe reviewed evidence states, not a confidentiality score. A clean capture does not verify unobserved stages, other providers, retention or future model behavior.
PDF uses built-in Western fonts. Use Markdown for full Unicode. Review all outputs before sharing; redaction is limited.
