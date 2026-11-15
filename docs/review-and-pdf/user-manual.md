# DME AgentFlow User Manual

Local evaluation edition | 13 November 2026

## What you can use today

AgentFlow has a landing page and dashboard at `/` and `/dashboard`. The dashboard is a preview with static cards, tabs and an unwired template button. Its health request uses the wrong API path and falls back to sample values. Treat its approval count, integration readiness and air-gap claims as display text. Use the backend API for evaluation.

Use synthetic inputs on a local, isolated instance. The API grants a platform-owner identity to requests without a token. Keep the service private and avoid customer records, credentials, production quotations and real operational decisions.

Evidence: `apps/web/src/app/dashboard/page.tsx:14-37,72-98,105-159`; `apps/api/core/security.py:60-74`.

## Start a local session

Follow the companion Architecture and Setup guide to start the API on loopback. The API description is available from `GET /openapi.json`. Interactive Swagger documentation is at `/docs` when its browser assets are reachable. The default Swagger assets are served from a CDN, so use the raw schema or an HTTP client in a disconnected environment.

1. Send `POST /api/v1/auth/register` with `email`, `password`, `full_name` and optionally `organization_name`. Registration creates an organization and an owner membership.
2. Save the returned `access_token` for the session. Send `Authorization: Bearer <access_token>` for subsequent requests. In Swagger, use Authorize with the token.
3. To start another session, send `POST /api/v1/auth/login` with the same email and password. `GET /api/v1/auth/me` returns the token context. Organization list, current organization and member-list endpoints are available. There is no browser sign-in, invitation or organization-switching workflow.

Evidence: `apps/api/routers/auth.py:10-106`; `apps/api/routers/organizations.py:21-123`; `apps/api/main.py:17-21,45-60`.

## Run the manufacturing RFQ template

1. Open `GET /api/v1/templates/` to see the catalog. Install the draft with `POST /api/v1/templates/tpl_rfq_extraction/install`. Save the returned `workflow_id`.
2. Send the JSON below to `POST /api/v1/executions/trigger`. The API currently accepts the installed draft directly. This walkthrough uses the backend graph and synthetic document content.
3. Inspect `GET /api/v1/executions/{execution_id}`. If the trigger returns `WAITING_APPROVAL`, use its `approval_request_id` or find the request in `GET /api/v1/approvals/?status=PENDING`.
4. To approve the synthetic run, send `{"decision":"APPROVED","comments":"Reviewed sample terms"}` to `POST /api/v1/approvals/{approval_id}/decision`. Reopen the execution detail to inspect the resumed run and node records. `REJECTED` cancels it. Clarification can strand a run, so use approve or reject for evaluation.
5. The quotation node returns sample document metadata. The PDF filename and download URL in its response are placeholders.

```json
{
  "workflow_id": "<workflow_id>",
  "trigger_type": "manual_trigger",
  "payload": {
    "inquiry_text": "Sample RFQ for 5,000 grade 6061-T6 valve bodies.",
    "contact_email": "buyer@example.invalid"
  }
}
```

Evidence: `apps/api/routers/templates.py:35-57,184-213`; `apps/api/routers/executions.py:44-95`; `apps/api/routers/approvals.py:49-100`; `apps/api/engine/executor.py:399-433`.

## Use the API modules

All paths below are relative to `/api/v1`. The OpenAPI schema lists request fields and exact methods.

- **Workflows.** Use `/workflows/` and `/workflows/{id}` to create, inspect, edit or delete JSON definitions. `POST /workflows/{id}/publish` marks a nonempty workflow published and increments its version. The stored graph remains editable. Use simple, acyclic graphs and inspect actual execution output. There is no browser workflow editor.
- **AI and agents.** Use `POST /inference/test` with a `prompt`. Check the response backend. `llama.cpp` identifies the native generation path, while `local_gemma_engine` identifies the rules-based fallback in this source. List or create agent records at `/agents/` and send a `message` to `POST /agents/{agent_id}/test` using the schema. Agent tests use the process-wide backend. Treat any structured output as unvalidated.
- **Knowledge.** Use `POST /knowledge/upload` with multipart fields `title` and `file`. Start with a short TXT file. The upload accepts PDF, DOCX, TXT, MD and CSV extensions, with limited document extraction. Send `{"query":"your sample terms","top_k":3}` to `POST /knowledge/search` and inspect returned passages and scores. `DELETE /knowledge/documents/{doc_id}` removes index records. The upload remains on disk. An empty document listing seeds a synthetic operations document.
- **CRM.** Use `/crm/contacts`, `/crm/leads`, `/crm/opportunities` and `/crm/tasks` for the available API operations. Contacts, leads and opportunities have list and create actions. Tasks can be listed and a workflow node creates sample tasks. Workflow-created records can contain fixed sample values.
- **Integrations and demos.** The integration list seeds example connectors and connection tests return simulated results. The four demonstration routes under `/demos` exercise scripted scenarios. Keep any emails or PDFs reported by the demos within the demo context.
- **Analytics and licensing.** `GET /analytics/summary` reads stored execution and workflow counts. Timing fallbacks, inference totals and savings assumptions limit how the response can be used. `GET /licensing/status` contains fixed usage and validity values. License install does not persist activation.

Evidence: `apps/api/routers/workflows.py:77-158`; `apps/api/routers/agents.py:100-146`; `apps/api/inference/backend.py:124-162`; `apps/api/routers/knowledge.py:19-113`; `apps/api/routers/crm.py:42-186`; `apps/api/routers/integrations.py:40-120`; `apps/api/routers/demos.py:84-290`; `apps/api/routers/analytics.py:14-84`; `apps/api/routers/licensing.py:77-107`.

## Troubleshooting

- **Dashboard looks healthy while the API is unavailable.** Check the API response directly. The dashboard displays fallback data, and `/health` itself contains static flags.
- **An inference request succeeds with no GGUF file.** Check the generation response backend and runtime state. The fallback can produce plausible-looking prices and classifications.
- **An execution finishes without an expected artifact.** Inspect per-node output. Unsupported nodes can return a generic success-like result, and document and email actions are simulated.
- **A document has irrelevant or empty results.** Check extraction using a short plain-text file. Search uses token hashing, and vectors may become incompatible after restart.

