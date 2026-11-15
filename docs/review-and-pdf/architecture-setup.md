# DME AgentFlow Architecture and Setup

Windows local evaluation | 13 November 2026

## Runtime architecture

The repository is the `agentflow` subdirectory under `C:\Users\USER\Desktop\Multi agent`. Next.js provides a landing page and dashboard. FastAPI mounts domain routers under `/api/v1`. The dashboard's only fetch uses an unprefixed health URL and falls back to static content. Most functions are accessed directly through the API.

The API uses synchronous SQLAlchemy sessions behind an async-shaped shim. Table creation runs at import. Workflows, executions, approvals, agent settings, CRM data and knowledge chunks live in the relational database. Documents also exist in local folders. The default database is SQLite and the path is relative to the process working directory.

A trigger inserts a queued execution and calls the graph interpreter within the same request. The interpreter reads the mutable workflow graph, traverses outgoing edges and stores execution context. An approval can pause the run and a separate decision request resumes it. CRM side effects, approval creation and execution state commit separately. Redis, a durable worker, immutable snapshots and recovery are missing from the active execution path.

The inference backend is a process-wide singleton imported by the API. It initializes with an empty model path. Native inference requires successful activation of a readable GGUF with a compatible llama-cpp-python build. Generation is synchronous and the fallback uses rules and canned responses. Knowledge search scans tenant-filtered chunks in SQL and scores 64-element token-hash vectors locally.

Evidence: `apps/web/src/app/dashboard/page.tsx:14-37`; `apps/api/main.py:12-60`; `apps/api/database/session.py:7-54`; `apps/api/database/models.py:42-155`; `apps/api/routers/executions.py:71-95`; `apps/api/engine/executor.py:20-202,337-433`; `apps/api/inference/backend.py:71-107,124-162,289-290`; `apps/api/knowledge/engine.py:67-142`.

## Start the API in an isolated Windows workspace

Use a separate writable run directory. The backend creates database tables and storage directories at import. Installing dependencies requires a package source or a prepared wheelhouse. The Dockerfile targets Python 3.12. This review used already installed Python 3.14 packages for checks, with FastAPI 0.162.5 and SQLAlchemy 2.1.8, which differ from the pins. A fresh pinned install was not verified. Use an available Python 3.12 environment for a pinned trial.

```powershell
$repo = 'C:\Users\USER\Desktop\Multi agent\agentflow'
$run = Join-Path (Get-Location) 'agentflow-local-eval'
New-Item -ItemType Directory -Path $run -Force | Out-Null
Set-Location -LiteralPath $run
py -3.12 -m venv .venv
$python = Join-Path $run '.venv\Scripts\python.exe'
& $python -m pip install -r (Join-Path $repo 'apps\api\requirements.txt')
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:SECRET_KEY = [guid]::NewGuid().ToString('N')
$env:DATABASE_URL = 'sqlite+aiosqlite:///./agentflow.db'
$env:DATA_DIR = './data'
$env:MODELS_DIR = './models'
$env:UPLOADS_DIR = './data/uploads'
$env:DOCUMENTS_DIR = './data/documents'
$env:DEPLOYMENT_PROFILE = 'FULLY_PRIVATE_AIRGAPPED'
$env:ALLOW_OUTBOUND_NETWORK = 'false'
& $python -m uvicorn main:app --app-dir (Join-Path $repo 'apps\api') --host 127.0.0.1 --port 8000
```

Use `http://127.0.0.1:8000/openapi.json` to verify routes and `/api/v1/inference/health` for the backend's report. The top-level health flags are constants. Configuration uses process environment variables. The settings class does not load a local `.env` on its own. The profile and outbound flag are configuration values, and network isolation must be enforced externally.

Evidence: `apps/api/core/config.py:4-40`; `apps/api/main.py:12-43`; `apps/api/requirements.txt:1-30`; `infrastructure/docker/Dockerfile.api:1-24`.

## Start the optional browser preview

In a second terminal, work from a disposable copy of `apps/web` if preserving the source tree matters. The npm commands write local dependencies and Next build output. Use the supplied lockfile with `npm ci`, then run `npm run dev -- --hostname 127.0.0.1`. Open port 3000 on loopback. The manifest lists Next.js 16.4.6 and React 19.3.0. The preview hardcodes localhost for the API and does not use the Compose `NEXT_PUBLIC_API_URL` setting.

Evidence: `apps/web/package.json:5-24`; `apps/web/next.config.ts:1-10`; `apps/web/src/app/dashboard/page.tsx:20-34,179`; `docker-compose.yml:141-152`.

## Evaluate a real model

The local native path is an integration point that requires separate acceptance. Install a compatible llama-cpp-python build and supply a known-good Gemma 4 GGUF from controlled storage. Restart after installing the Python module. Register the absolute path and context/thread/GPU settings through `POST /api/v1/inference/models/register`, then activate by ID. Compare runtime health and a short generation result. A registry entry, nominal activation and a model name in a response can all exist without successful native inference. The native response must report `llama.cpp`. Record model checksum, runtime build, hardware and output before qualifying CPU or CUDA. Use the emulation path only for synthetic evaluation.

Evidence: `apps/api/routers/inference.py:13-25,99-160`; `apps/api/inference/backend.py:71-107,124-162,245-290`; `apps/api/requirements.txt`.

## Deployment status and data handling

- **Local SQLite evaluation.** Data is stored in the run directory, with uploads and sample documents in configured local directories. Keep the API bound to loopback because the missing-token path grants administrator privileges.
- **Compose SaaS and hybrid.** Compose describes PostgreSQL/pgvector, Redis, API, worker, inference and web containers. The SQLite-specific database adapter conflicts with its async PostgreSQL URL. Worker commands point to modules absent from the source. The API image defaults to two workers, which would each have separate inference state. Container builds and migrations were not verified.
- **Air-gapped and GPU.** The profile does not enforce network policy, the Compose bridge is not internal, Swagger uses CDN assets, and build stages use online dependency sources. The offline and deployment directories contain no runnable packaging. The GPU override sets `AI_N_GPU_LAYERS`, while the app settings read `DEFAULT_GPU_LAYERS` and registry activation passes its own value. Validate offline media, local assets, no-egress policy, recovery and CUDA independently.
- **Backups.** For evaluation, stop the API before copying its SQLite database and configured file directories to a protected location. Verify restoration in a separate run directory. The application does not provide an audited backup, retention or secure deletion procedure.

Evidence: `docker-compose.yml:3-5,24-74,92-152`; `infrastructure/docker/Dockerfile.api:10-44`; `infrastructure/docker/Dockerfile.gpu:11-64`; `infrastructure/docker/docker-compose.gpu.yml:9-36`; `apps/api/database/session.py:7-16`; `apps/api/core/config.py:16-30`; `apps/api/routers/inference.py:135-139`.

