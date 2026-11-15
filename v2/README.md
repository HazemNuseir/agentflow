# DME AgentFlow V2 LAN Edition

Run V2 from this folder. Workstations use a browser and individual accounts. The central server runs the frontend, API and database. Use a fresh V2 database and volumes.

## Shared server with Docker Compose

1. Install Docker with Compose on the server. From this directory, create V2 secrets in PowerShell.

   ```powershell
   $dbPassword = [guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N')
   $secretKey = [guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N')
   @("V2_DB_PASSWORD=$dbPassword", "V2_SECRET_KEY=$secretKey", "V2_BIND_ADDRESS=127.0.0.1", "V2_WEB_PORT=3001") | Set-Content .env
   docker compose up --build -d
   docker compose ps
   ```

   Generate secrets once. Keep the .env file private and retain it across restarts. For an existing V2 PostgreSQL volume, use the database password already associated with it or rotate it in PostgreSQL before updating .env.

2. For a shared LAN, put an HTTPS reverse proxy on the same host in front of http://127.0.0.1:3001. Forward all paths, including /api/v1 and /health. Use a server name and certificate that client machines trust. Allow inbound TCP 443 from the intended subnet in the server firewall. Use the same https://SERVER-NAME address on every workstation. The V2 API and PostgreSQL have no published host ports.
3. Open the web address, register the organization owner, then use **Team** to provision members and assign roles. Give each member a unique initial password through a private channel. A workflow editor can install a template, publish it, and run it on **Workflows**. An approver can open **Approvals** in another session. Return to **Workflows** to refresh run status and inspect node output.

## Local evaluation on Windows

From this V2 directory in PowerShell, create an API environment and start the API with its own SQLite database and data directories.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r apps/api/requirements.txt
$env:SECRET_KEY = [guid]::NewGuid().ToString('N')
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir apps/api --host 127.0.0.1 --port 8080
```

In a second terminal, change to this V2 directory and run:

```powershell
Set-Location apps/web
npm ci
npm run dev -- --hostname 127.0.0.1 --port 3001
```

Open http://127.0.0.1:3001. For this local layout the web server proxies to http://127.0.0.1:8080. SQLite files and storage defaults are relative to the API working directory. Starting from different directories can create separate V2 databases.

## Data and verification

Startup creates missing tables and adds the per-execution graph snapshot column to an existing V2 schema. Back up an existing V2 database before upgrading. For PostgreSQL use pg_dump and test pg_restore to a fresh database or deployment. Back up the V2 data volume alongside the database. For SQLite stop the API before copying the V2 database and data directories. V1 data migration is a separate operation.

Run python -m pytest -q tests/test_concurrent_approvals.py with V2 dependencies installed. The regression test uses a disposable SQLite database. It exercises the approval handler with two threads, checks one continuation and one CRM record, and checks viewer and tenant denial. Also verify separate sign-ins, the same-origin proxy, PostgreSQL approvals, and two physical LAN clients before a shared rollout.

The compose topology does not demonstrate denied egress. Native Gemma requires a compatible runtime and a registered GGUF model. Document generation currently returns simulated output. Approval claiming prevents a repeat decision from starting another continuation. Recovery after a process interruption between saving a decision and resuming a run is not implemented.


## Verification on this Windows host

The development HTTP proxy served the login, workflow, approvals and team pages. A two-account HTTP smoke test passed from owner registration and approver provisioning through RFQ template publication, execution, approval and completion. The SQLite concurrency regression passed. Docker, PostgreSQL, native Gemma, and two separate physical LAN workstations still need deployment verification.
