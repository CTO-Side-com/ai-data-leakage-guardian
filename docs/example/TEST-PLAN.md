# AI data leakage regression plan
Scoped AI data-leakage assessment. Not a guarantee of confidentiality, a production DLP gateway or compliance certification.

Use only independently seeded synthetic canaries and approved offline captures. Do not send real sensitive data to any model, tool, telemetry service or scanner.
Product: Synthetic AI capture demonstration
Environment: local
Data-handling model: Synthetic restricted inputs are intended to be redacted before request and telemetry capture
Systems: Owned offline payload and trace fixture
Exclusions: No real AI providers, production services or customer data
Unknowns: Live SDK interception, retained provider copies, semantic leakage and unobserved stages are untested.
Catalog prompts require adaptation to actual source/transform/sink flows. No endpoints or provider settings are inferred.

## MAP-001 | Classify AI inputs and derived data
Expected boundary: Data classes and allowed purposes must be explicit for each source.
Suggested test: Trace a synthetic confidential document and its derived fields through the AI pipeline.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## MAP-002 | Inventory model and non-model destinations
Expected boundary: Prompts, embeddings, telemetry, tools and user output are distinct sinks.
Suggested test: Reconcile SDK/configuration paths with a reviewed sink register.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## MAP-003 | Map transformations and intermediate copies
Expected boundary: Chunking, redaction, summaries and retries can create retained copies.
Suggested test: Trace a seeded canary through intermediate stages and inventory every copy.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## MAP-004 | Approve data classes per destination and purpose
Expected boundary: A destination being trusted does not authorize every data class or use.
Suggested test: Review each source-transform-sink edge against a named approval and its evidence.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## PROMPT-001 | Keep credentials and protected configuration out of prompts
Expected boundary: Model instructions must not contain operational secrets.
Suggested test: Inspect prompt construction by reference and use synthetic secret-like markers to test exclusion.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## PROMPT-002 | Minimize sensitive input before model submission
Expected boundary: Only data required for the approved purpose should enter the prompt.
Suggested test: Seed a protected field beside an allowed control and inspect the outbound payload capture.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## PROMPT-003 | Apply redaction before external transmission
Expected boundary: Post-response masking cannot undo a disclosure to a provider.
Suggested test: Compare captures before and after the actual outbound boundary using synthetic markers.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## PROMPT-004 | Bound conversation history and inherited context
Expected boundary: Prior turns and hidden context must follow current authorization and minimization.
Suggested test: Seed an earlier synthetic restricted turn and examine a later request to another workflow.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## PROMPT-005 | Treat prompt confidentiality as insufficient authorization
Expected boundary: Prompts cannot enforce access control or tool privileges alone.
Suggested test: Test a synthetic instruction requesting a restricted field and inspect independent enforcement.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## RAG-001 | Authorize documents before retrieval or context assembly
Expected boundary: Retrieval must respect actor, tenant, document and purpose boundaries.
Suggested test: Index authorized and restricted synthetic documents and inspect retrieval plus final context.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## RAG-002 | Review embedding data and provider egress
Expected boundary: Embedding inputs and vector stores can retain sensitive information.
Suggested test: Trace a synthetic restricted marker into embedding requests and retained vector metadata.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## RAG-003 | Protect conversation and semantic caches
Expected boundary: Cached context and answers must not cross user, tenant or policy scope.
Suggested test: Warm a synthetic cache under one identity and retrieve under another.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## RAG-004 | Constrain citations previews and source downloads
Expected boundary: A safe answer can still link to an unauthorized source.
Suggested test: Review synthetic citation metadata and attempt the source-download path through authorized tests.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## RAG-005 | Recheck preprocessing chunking and reranking
Expected boundary: Derived text and reranker inputs need the same data-flow review.
Suggested test: Track an independently seeded marker through chunks, reranking and context trimming.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## EGRESS-001 | Inventory and constrain external endpoints
Expected boundary: Dynamic destinations and proxies must remain within approved policy.
Suggested test: Review configured endpoints and synthetic outbound captures for unregistered sinks.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## EGRESS-002 | Authorize tool and agent egress independently
Expected boundary: Model-generated arguments cannot override destination and data-class policy.
Suggested test: Use a synthetic injection requesting export to an unapproved sink and inspect the tool gate.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## EGRESS-003 | Protect transmission and provider routing configuration
Expected boundary: Outbound transport and routing must preserve the approved boundary.
Suggested test: Review TLS verification, custom base URLs, gateways and environment-specific routes.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## EGRESS-004 | Exclude sensitive material from URLs headers and metadata
Expected boundary: Content can escape through request metadata as well as bodies.
Suggested test: Seed a synthetic marker and inspect body, query, headers and correlation metadata separately.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## EGRESS-005 | Review fallback retry batch and failover paths
Expected boundary: Fallback and error handling must retain the original data policy.
Suggested test: Force a synthetic primary failure and inspect all retry and fallback captures.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## OBS-001 | Minimize or redact prompt and input logs
Expected boundary: Diagnostic logging must not become an unauthorized sensitive-data sink.
Suggested test: Capture a synthetic request and verify the log payload and its access boundary.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## OBS-002 | Review model outputs and raw tool traces
Expected boundary: Generated text and intermediate tool results may contain protected data.
Suggested test: Seed a restricted synthetic tool response and inspect debug and completion captures.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## OBS-003 | Review SDK tracing and debug configuration
Expected boundary: SDK defaults and debug switches need environment-specific verification.
Suggested test: Inspect actual approved configuration and synthetic traces for the deployed mode.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## OBS-004 | Constrain analytics and error-reporting payloads
Expected boundary: User analytics and error tools should receive only approved fields.
Suggested test: Trigger a synthetic exception and inspect analytics events, breadcrumbs and attachments.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## OBS-005 | Apply access retention and deletion to observability stores
Expected boundary: Redacted application output does not govern trace-store access or retention.
Suggested test: Review provider settings by dated evidence and exercise synthetic deletion where authorized.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## PROVIDER-001 | Confirm approved service model and account scope
Expected boundary: Approval must apply to the exact service, deployment and data use.
Suggested test: Reconcile configured service/model/account references with a reviewed approval record.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## PROVIDER-002 | Verify retention and training-use statements separately
Expected boundary: Training exclusion and retention are distinct claims requiring current evidence.
Suggested test: Record current service-specific documentation and configuration without inferring defaults.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## PROVIDER-003 | Review regional routing and subprocessors
Expected boundary: Residency and processing locations require evidence for the actual setup.
Suggested test: Review configured regions, routing layers and relevant subprocessor records.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## PROVIDER-004 | Review agreements access roles and shared responsibilities
Expected boundary: Technical settings and contractual approval support different conclusions.
Suggested test: Request the responsible owner's approved evidence for the exact provider and service.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## PROVIDER-005 | Reassess provider configuration and policy changes
Expected boundary: A prior approval may not cover a new model, feature or fallback provider.
Suggested test: Trace a synthetic configuration change to a renewed scoped review.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## TOOL-001 | Authorize final responses for the actual recipient
Expected boundary: Answers and summaries must follow the recipient's access and purpose.
Suggested test: Seed authorized and restricted records and inspect the recipient-visible output.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## TOOL-002 | Minimize tool results before model context
Expected boundary: An authorized tool can still return excessive protected fields.
Suggested test: Inspect synthetic raw and minimized tool captures before context assembly.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## TOOL-003 | Constrain streamed output attachments and previews
Expected boundary: Partial streams and nontext outputs have separate disclosure paths.
Suggested test: Use synthetic markers in streamed chunks, files and previews; document unsupported media.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## TOOL-004 | Protect generated exports and shared conversation links
Expected boundary: Persisted outputs and links need recipient-specific access boundaries.
Suggested test: Review synthetic export/share creation and retrieval through an approved fixture.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## LIFE-001 | Apply retention to inputs outputs caches and captures
Expected boundary: Deletion and legal retention must cover derived and intermediate artifacts.
Suggested test: Map a synthetic record to retained copies and test approved disposal paths.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## LIFE-002 | Review training evaluation and fine-tuning datasets
Expected boundary: Operational data cannot enter datasets without its own approved purpose.
Suggested test: Trace synthetic restricted markers through dataset creation and file-upload paths.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## LIFE-003 | Review support incident and human-review access
Expected boundary: Human review and incident workflows can create new recipients and copies.
Suggested test: Follow a synthetic support case and inspect approved exports and access records.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.

## LIFE-004 | Track regressions after prompt model and integration changes
Expected boundary: Data policy should survive changes to prompts, retrieval, tools and providers.
Suggested test: Run scoped synthetic captures after a reviewed change and retain prior evidence.
Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.
