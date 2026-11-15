# DME AgentFlow Implementation Audit

Windows source and local verification | 13 November 2026

## Release assessment

The project supports a local API-based prototype. It does not satisfy the master requirements for commercial deployment. The highest-priority blockers are unauthenticated administrator access, incomplete approval and execution controls, simulated behavior reported as live, and an unverified native model and deployment path.

Scope: `C:\Users\USER\Desktop\Multi agent\agentflow`. Evidence paths below are relative to that root. The ChatGPT reference exposed the master prompt through section 22, truncated during the customer-support demo. This report uses the visible requirements and the scope in the current request. The source has no Git metadata at the inspected root. Existing databases and customer data were excluded from testing.

## What was verified

- **Passed, direct Python handlers on a fresh SQLite database.** Health response, registration and login, rules-based generation, eight templates, manufacturing RFQ install and pause, approval and completion of the same execution, successful-run analytics count, and in-process TXT indexing/search. The harness passed the returned user context directly and did not exercise HTTP authorization, upload handling, browser behavior or no-egress.
- **Passed, static frontend checks.** TypeScript `--noEmit --incremental false` exited 0. ESLint on `src` exited 0 with three unused-state warnings in `apps/web/src/app/dashboard/page.tsx:16-17`.
- **Incomplete, supplied HTTP tests.** `tests/unit/test_api_endpoints.py` and `tests/run_tests.py` stalled without results. A separate timed probe imported the application and then stalled in Windows asyncio's socket-pair initialization. This blocked HTTP-level verification in the observed environment. The tests assume anonymous access, and some assert static compliance flags or accept fallback output as inference.
- **Unverified.** Browser rendering/build, pinned fresh install, PostgreSQL, Docker, CUDA, native GGUF generation, cross-tenant enforcement, concurrent execution, and disconnected operation. Python 3.14.8, FastAPI 0.162.5 and SQLAlchemy 2.1.8 were used for runtime checks. The installed environment lacked `llama_cpp`, and the project tree had no GGUF file.

Evidence: `tests/unit/test_api_endpoints.py:13-107`; `tests/run_tests.py:11-99`; `apps/api/requirements.txt:1-30`; `apps/api/inference/backend.py:71-107,124-162`.

## P0 | Block exposure and enforce approvals

### P0-1. Anonymous platform owner and incomplete authorization

The shared authentication dependency returns `PLATFORM_OWNER` for missing credentials. JWT verification returns claims without checking current account or membership. A known fallback signing secret ships in code. Role hierarchy exists but approval, workflow mutation and model activation do not enforce role permissions. Model registry queries and model state are global. Tenant filters on some routes therefore provide only partial protection.

Fix authentication first. Require a valid session on protected routes, require a deployment-generated secret, resolve current membership server-side and enforce an explicit permission matrix for writes and sensitive reads. Decide which model configuration is platform-wide and enforce that scope. Gate release on anonymous, expired, revoked, insufficient-role and cross-tenant negative tests across data and files.

Evidence: `apps/api/core/security.py:31-74`; `apps/api/core/config.py:8-10`; `apps/api/routers/approvals.py:49-74`; `apps/api/routers/workflows.py:77-158`; `apps/api/routers/inference.py:28-32,99-141`.

### P0-2. Approval decisions and execution transitions can diverge

Decision accepts any string and ignores assigned role. Approval commits before execution resumes. Clarification can leave a nonpending approval and a waiting execution. A persisted approval decision can satisfy later approval nodes. Triggers accept inactive or unpublished workflows. Cancellation changes a status field without cooperative cancellation or guarding terminal transitions. Approval resumption reads the current graph, which may have changed since the pause.

Validate the decision enum and approver permission. Bind decisions to a specific node and immutable snapshot, make the pending transition atomic, and persist a recoverable resume job. Test competing decisions, multiple approvals, clarification, retry after failure, cancellation and draft execution policy.

Evidence: `apps/api/routers/approvals.py:13-15,49-100`; `apps/api/routers/executions.py:71-110`; `apps/api/engine/executor.py:38-47,75-89,409-433`.

## P1 | Close core product and deployment gaps

### P1-1. Native Gemma 4 and model management

The llama-cpp-python adapter exists, but startup passes an empty path and model activation ignores load failure. Generation runs synchronously in API and workflow handlers. There is no separate inference worker, bounded queue, timeout or proven compatibility. The registry seeds model metadata and nominal states. Agent test uses a shared backend and structured generation parses JSON or supplies fallback content without validating it against the requested schema.

Require explicit native load/readiness state and label emulation at every entry point. Pin a compatible runtime and GGUF checksum, validate CPU first and CUDA separately, then move inference to a bounded worker. Verify model selection and schema failures per agent.

Evidence: `apps/api/inference/backend.py:71-107,124-189,245-290`; `apps/api/routers/inference.py:28-96,118-160`; `apps/api/routers/agents.py:122-146`; `docker-compose.yml:114-127`.

### P1-2. Visual authoring and durable graph execution

There are only landing and dashboard pages, with no React Flow dependency or editor route. Shared node definitions do not enforce the backend graph. Publish increments a mutable row version and checks only that nodes exist. Execution queues downstream nodes without waiting for all dependencies, unsupported nodes return generic output, and a failure completion node can reach the engine's completed state. No durable scheduling, retries, timeout, recovery or idempotency path was found.

Implement server-side graph validation and immutable version snapshots before connecting a visual builder. Then add durable job dispatch, dependency-aware scheduling and idempotent side effects. Test joins, cycles, unsupported nodes, failure completion, version stability, restart and replay.

Evidence: `apps/web/package.json:5-25`; `apps/web/src/app/dashboard/page.tsx:72-98,139-159`; `packages/workflow-schemas/index.ts`; `apps/api/routers/workflows.py:96-143`; `apps/api/engine/executor.py:46-96,154-202,435-442`.

### P1-3. Deployment and offline operation

Compose points to missing Celery and inference modules. Its async PostgreSQL URL is passed to a synchronous adapter with SQLite-specific arguments. The bridge does not enforce egress denial and service ports are published. There is no runnable offline package. Default Swagger browser assets come from a CDN. Health endpoints claim air-gap status without performing a network test.

Ship one reproducible deployment first. Implement PostgreSQL migrations and working worker entry points, private service networking, TLS and secret management. Build offline media with local assets, images, dependencies and a manifest. Require successful fresh install, restore and operation under denied egress before claiming offline support. Verify Linux, Windows and CUDA separately.

Evidence: `docker-compose.yml:3-5,24-74,92-152`; `apps/api/database/session.py:7-16,60-62`; `apps/api/main.py:17-43`; `infrastructure/docker/Dockerfile.api:10-44`; `infrastructure/docker/docker-compose.gpu.yml:9-36`; `infrastructure/offline/`.

### P1-4. Knowledge ingestion and persistence

The filename is used in the upload path with extension-only validation and no application-level size cap. Repeated filenames can overwrite uploads. Deleting index entries leaves the original file. PDF extraction uses raw pattern matching and may index unrelated text. Extraction failures can become generic content marked indexed. Python's randomized token hashes can invalidate stored vectors after restart. Search scans tenant-filtered JSON vectors in memory.

Use generated storage keys and bounded, validated parsing. Track extraction failures, store ownership, remove originals according to policy, and test limits and isolation. Replace process-randomized vectors with a validated local embedding pipeline and versioned pgvector indexing.

Evidence: `apps/api/routers/knowledge.py:62-113`; `apps/api/knowledge/engine.py:18-53,67-142`; `apps/api/database/models.py:134-155`.

### P1-5. Integrations, artifacts and claims of success

Integration listing seeds connected or ready statuses. The test endpoint returns a fixed latency and handshake success without making a connection. Its hostname denylist is insufficient for any future outbound client. Workflow email returns simulated dispatch, and PDF generation returns a synthetic URL with no corresponding download route. The browser, health and licensing interfaces also display static operational claims.

Show explicit simulation and unknown states. Implement real connector lifecycle, encrypted secrets, restricted egress and verified result reporting before enabling outbound actions. Tie sensitive actions to authorization and persisted approval. Require a real artifact and audit event before reporting success.

Evidence: `apps/api/routers/integrations.py:25-38,40-120`; `apps/api/engine/executor.py:390-406`; `apps/api/main.py:33-60`; `apps/web/src/app/dashboard/page.tsx:20-34,112-131`.

## P2 | Complete business capabilities and acceptance coverage

- **Organizations and onboarding.** Registration creates owner membership. Organization reads, creation and an onboarding submission API exist. Login selects a membership rather than offering a workspace picker. Invitations, removal, reset, verification, session revocation and Arabic/RTL remain absent from inspected routes and UI. Evidence: `apps/api/routers/auth.py:25-106`; `apps/api/routers/organizations.py:17-123`; `apps/api/routers/onboarding.py:10-55`; `apps/web/src/app/layout.tsx:13-17`.
- **Agents.** List, create and test endpoints exist. Complete version history, model binding, knowledge/tool authorization, execution budgets and approval policies are missing from the active test path. Evidence: `apps/api/routers/agents.py:12-29,30-97,100-146`.
- **CRM.** Contacts, leads and opportunities expose create/list. Tasks expose list, and workflow actions write sample CRM data. The opportunity update node inserts a new fixed record. Complete company, note, activity, edit and delete flows are missing. Evidence: `apps/api/routers/crm.py:42-186`; `apps/api/engine/executor.py:337-388`.
- **Templates and demos.** Eight templates install as drafts; the full twelve-scenario catalog and per-template contracts are incomplete. Four scripted demo routes exist. Their synthetic inputs, inline approvals and outputs are distinct from durable workflow execution and delivery. Verify every shipped template with positive and failure cases. Evidence: `apps/api/routers/templates.py:11-180,184-213`; `apps/api/routers/demos.py:84-290`.
- **Analytics.** Tenant workflow/execution/approval counts query SQLite. Model information is hardcoded and inference counters are process-wide. Timing fallbacks and fixed ROI assumptions limit interpretation, and filters are missing. Use tenant-level events and configurable assumptions, and distinguish zero or unavailable data. Evidence: `apps/api/routers/analytics.py:10-84`.
- **Licensing.** Edition definitions and local HMAC verification exist. Installation does not persist, usage and expiry are fixed, and the HMAC shares the JWT secret. Use independent asymmetric signing, organization and expiration validation, persisted state and enforced limits. Evidence: `apps/api/routers/licensing.py:15-107`.
- **Security operations and tests.** Add audit coverage, rate limiting, retention, backups and restore tests, webhook verification, upload hardening, AI tool permissions and prompt-injection controls before commercial acceptance. Replace order-dependent smoke expectations with isolated fixtures and add API integration, browser, security, real-model and denied-egress suites. Evidence: `apps/api/main.py:23-30,45-60`; `apps/api/database/models.py`; `tests/unit/test_api_endpoints.py`; `tests/run_tests.py`; `apps/web/package.json:5-10`.

