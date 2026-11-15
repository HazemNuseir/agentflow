# DME AgentFlow — Complete Installation Manual

**Platform:** DME AgentFlow — Intelligent Business Automation Platform  
**Developer:** Digital Mind Engineering (DME), Amman, Jordan  
**Tagline:** *Your Business. Your Data. Your AI.*  
**Document Version:** 1.0 (Production / Air-Gap Certified)  
**Target Audience:** DevOps Engineers, System Administrators, Security Officers, Infrastructure Leads  

---

## Table of Contents
1. [Overview & Deployment Profiles](#1-overview--deployment-profiles)
2. [Hardware & Software Prerequisites](#2-hardware--software-prerequisites)
3. [Profile A: Local Developer Installation (Windows / Linux / macOS)](#3-profile-a-local-developer-installation)
4. [Profile B: Production Docker Deployment (Cloud & On-Premise)](#4-profile-b-production-docker-deployment)
5. [Profile C: High-Performance GPU Acceleration (NVIDIA CUDA)](#5-profile-c-high-performance-gpu-acceleration)
6. [Profile D: 100% Disconnected Air-Gapped Installation](#6-profile-d-100-disconnected-air-gapped-installation)
7. [Google Gemma 4 Model Acquisition & Verification](#7-google-gemma-4-model-acquisition--verification)
8. [Database Schema Migrations & Storage Setup](#8-database-schema-migrations--storage-setup)
9. [Post-Installation Health Checks & Acceptance Testing](#9-post-installation-health-checks--acceptance-testing)
10. [Troubleshooting & Maintenance Runbook](#10-troubleshooting--maintenance-runbook)

---

## 1. Overview & Deployment Profiles

DME AgentFlow supports three operational deployment profiles configured via environment variables:

| Profile Code | Description | Network Policy | Typical Target |
|---|---|---|---|
| `FULLY_PRIVATE_AIRGAPPED` | Default sovereign deployment. Zero telemetry, zero external model calls, local GGUF Gemma inference, cryptographic license tokens. | Outbound blocked | Defense, government, critical manufacturing, sovereign enterprise |
| `CUSTOMER_HOSTED_HYBRID` | On-premise core with optional external outbound connectors (e.g., enterprise SMTP, approved SaaS REST webhooks). | Outbound selective | Private cloud (AWS, Azure, GCP VPCs), on-premise data centers |
| `CLOUD_SAAS` | Multi-tenant cloud SaaS deployment hosted by DME or enterprise service provider. | Outbound enabled | Multi-company cloud automation |

---

## 2. Hardware & Software Prerequisites

### Compute & Memory Sizing
- **Minimum (Evaluation / CPU Inference):**
  - CPU: 4 cores (x86_64 or ARM64)
  - RAM: 16 GB DDR4/DDR5
  - Storage: 30 GB available SSD space
  - Model: Google Gemma 4 E4B Instruct (Q4_K_M quantization ~3.2 GB footprint)
- **Recommended (Production / Multi-Tenant):**
  - CPU: 8–16 cores
  - RAM: 32–64 GB
  - Storage: 100 GB NVMe SSD
  - Model: Google Gemma 4 12B Instruct or 26B A4B
- **High-Throughput Enterprise (NVIDIA GPU):**
  - GPU: 1x NVIDIA RTX 4090 (24 GB VRAM) or NVIDIA A10G / L4 / A100 (24–80 GB VRAM)
  - CUDA: 12.2+ with matching NVIDIA drivers (>= 535.xx)

### Software Dependencies
- **Python:** 3.12+ (tested through 3.14)
- **Node.js:** v20.x or v22.x LTS, with npm v10+
- **Database:** SQLite 3.38+ (built-in development) or PostgreSQL 15+ with `pgvector`
- **Containerization (Optional):** Docker 24+ and Docker Compose v2.20+

---

## 3. Profile A: Local Developer Installation

### Step 1: Repository Clone & Workspace Setup
```bash
git clone https://github.com/digitalmind-engineering/agentflow.git
cd agentflow
```

### Step 2: Backend Configuration & Virtual Environment
```bash
# Navigate to API app
cd apps/api

# Create and activate Python virtual environment
python -m venv .venv

# On Linux/macOS:
source .venv/bin/activate
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Windows (cmd.exe):
.\.venv\Scripts\activate.bat

# Install backend dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Environment Setup
Copy the sample environment file to the project root:
```bash
cp ../../.env.example ../../.env
```
Key development settings in `.env`:
```env
PROJECT_NAME="DME AgentFlow"
SECRET_KEY=<GENERATE_RANDOM_64_CHAR_HEX>
DEPLOYMENT_PROFILE="FULLY_PRIVATE_AIRGAPPED"
DATABASE_URL="sqlite+aiosqlite:///./agentflow.db"
ALLOW_OUTBOUND_NETWORK=false
DEFAULT_MODEL_NAME="gemma-4-e4b-instruct.Q4_K_M.gguf"
```

### Step 4: Database Table Initialization
```bash
# From apps/api directory with virtual environment active:
python -c "from database.session import engine, Base; import database.models; Base.metadata.create_all(engine); print('Database initialized successfully.')"
```

### Step 5: Start Backend Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The interactive Swagger API documentation will be available at: `http://localhost:8000/docs`

### Step 6: Frontend Setup & Launch
Open a separate terminal window:
```bash
cd agentflow/apps/web
npm install
npm run dev
```
Access the AgentFlow Mission Control console at: `http://localhost:3000`

---

## 4. Profile B: Production Docker Deployment

Production containerization isolates services across four network segments using Docker Compose.

### Step 1: Prepare `.env`
Ensure your `.env` contains production database credentials:
```env
APP_ENV=production
DEPLOYMENT_PROFILE=CUSTOMER_HOSTED_HYBRID
SECRET_KEY=<GENERATE_RANDOM_64_CHAR_HEX>
DATABASE_URL=postgresql+asyncpg://agentflow_user:<YOUR_POSTGRES_PASSWORD>@postgres:5432/agentflow_db
REDIS_URL=redis://redis:6379/0
ALLOW_OUTBOUND_NETWORK=true
```

### Step 2: Build & Start Services
From the `agentflow/` repository root:
```bash
docker compose up -d --build
```

### Step 3: Verify Container Health
```bash
docker compose ps
```
Expected output:
```text
NAME                     IMAGE                       STATUS                   PORTS
agentflow-postgres-1     pgvector/pgvector:pg16      Up (healthy)             5432/tcp
agentflow-redis-1        redis:7-alpine              Up (healthy)             6379/tcp
agentflow-api-1          agentflow-api:latest        Up (healthy)             0.0.0.0:8000->8000/tcp
agentflow-web-1          agentflow-web:latest        Up (healthy)             0.0.0.0:3000->3000/tcp
```

### Step 4: Apply Database Migrations inside API Container
```bash
docker compose exec api alembic upgrade head
```

---

## 5. Profile C: High-Performance GPU Acceleration

To run Google Gemma 4 models at sub-100ms latency, compile `llama-cpp-python` with CUDA GGML support.

### Step 1: Host Driver Verification
```bash
nvidia-smi
nvcc --version
```

### Step 2: Build with CUDA Flags (Native Python)
On Windows (with Visual Studio Build Tools & CUDA Toolkit installed):
```cmd
set CMAKE_ARGS=-DGGML_CUDA=on
set FORCE_CMAKE=1
pip install --upgrade --force-reinstall --no-cache-dir llama-cpp-python
```
On Linux (Ubuntu/Debian):
```bash
CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 pip install --upgrade --force-reinstall --no-cache-dir llama-cpp-python
```

### Step 3: GPU Docker Compose Deployment
```bash
docker compose -f docker-compose.yml -f infrastructure/docker/docker-compose.gpu.yml up -d --build
```
Verify GPU memory offloading in the inference logs:
```bash
docker compose logs -f api | grep -i "cuda"
```

---

## 6. Profile D: 100% Disconnected Air-Gapped Installation

For installations with zero internet access, prepare a release package on a staging machine.

### Stage 1: Export Package on Internet-Connected Staging Machine
1. **Download Wheel Dependencies:**
   ```bash
   pip download -r agentflow/apps/api/requirements.txt -d ./offline-wheels
   ```
2. **Download Gemma 4 GGUF Model Weights:**
   Download `gemma-4-e4b-instruct.Q4_K_M.gguf` from approved repository into `./offline-models/`.
3. **Export Pre-built Container Images:**
   ```bash
   docker save -o agentflow-images.tar \
     pgvector/pgvector:pg16 \
     redis:7-alpine \
     agentflow-api:latest \
     agentflow-web:latest
   ```
4. **Archive Offline Package:**
   ```bash
   tar -czvf dme-agentflow-airgap-v1.0.tar.gz agentflow/ offline-wheels/ offline-models/ agentflow-images.tar
   ```

### Stage 2: Deploy on Air-Gapped Target Server
1. Mount verified external storage medium.
2. Extract archive:
   ```bash
   tar -xzvf dme-agentflow-airgap-v1.0.tar.gz -C /opt/dme/
   cd /opt/dme/agentflow
   ```
3. Load Docker images:
   ```bash
   docker load -i ../agentflow-images.tar
   ```
4. Copy weights into models directory:
   ```bash
   mkdir -p models
   cp ../offline-models/*.gguf models/
   ```
5. Enforce air-gap profile in `/opt/dme/agentflow/.env`:
   ```env
   DEPLOYMENT_PROFILE=FULLY_PRIVATE_AIRGAPPED
   ALLOW_OUTBOUND_NETWORK=false
   AIRGAP_MODE=true
   ```
6. Start system:
   ```bash
   docker compose up -d
   ```

---

## 7. Google Gemma 4 Model Acquisition & Verification

DME AgentFlow requires compatible GGUF quantizations of the Google Gemma 4 family.

### Model Matrix

| Model Identifier | Parameter Count | Quantization | File Size | Recommended Hardware |
|---|---|---|---|---|
| `gemma-4-e4b-instruct.Q4_K_M.gguf` | 4 Billion (Effective) | Q4_K_M | 3.2 GB | 16 GB RAM (CPU) or 6 GB VRAM |
| `gemma-4-12b-instruct.Q4_K_M.gguf` | 12 Billion | Q4_K_M | 7.6 GB | 32 GB RAM (CPU) or 12 GB VRAM |
| `gemma-4-26b-a4b.Q4_K_M.gguf` | 26 Billion (MoE) | Q4_K_M | 16.2 GB | 64 GB RAM (CPU) or 24 GB VRAM |
| `gemma-4-31b-instruct.Q4_K_M.gguf` | 31 Billion | Q4_K_M | 19.5 GB | 64 GB RAM (CPU) or 24 GB VRAM |

### Model Placement
Place all downloaded GGUF files directly inside the `agentflow/models/` folder:
```text
agentflow/models/
├── gemma-4-e4b-instruct.Q4_K_M.gguf
└── README.md
```

### Windows Path Length Warning
On Windows 10/11, enable Win32 Long Paths to prevent GGUF loading errors:
```powershell
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1
```

---

## 8. Database Schema Migrations & Storage Setup

### Required Table Schema
The platform manages 17 core domain entities:
- `organizations`, `users`, `organization_members` (Tenancy & RBAC)
- `workflows`, `workflow_executions`, `approval_requests` (Execution Engine)
- `ai_models`, `ai_agents` (Sovereign AI Registry)
- `knowledge_documents`, `knowledge_chunks` (Local Knowledge Hub)
- `crm_contacts`, `crm_leads`, `crm_opportunities`, `crm_tasks` (CRM Module)
- `integration_configs`, `audit_logs`, `license_records` (Security & Governance)

### Adding New Columns to Existing SQLite Database
If upgrading from an earlier snapshot, run:
```sql
ALTER TABLE workflows ADD COLUMN published_snapshot_json JSON;
ALTER TABLE workflow_executions ADD COLUMN is_draft_test BOOLEAN DEFAULT 0;
ALTER TABLE workflow_executions ADD COLUMN workflow_version INTEGER DEFAULT 1;
ALTER TABLE knowledge_documents ADD COLUMN storage_key VARCHAR(256);
ALTER TABLE knowledge_documents ADD COLUMN error_message TEXT;
ALTER TABLE crm_leads ADD COLUMN contact_id VARCHAR(64);
```

---

## 9. Post-Installation Health Checks & Acceptance Testing

Verify that all components are functioning before opening access to end users.

### Step 1: Run Backend Synchronous Verification
```bash
python agentflow/tests/verify_backend.py
```
Expected output:
```text
==================================================
   DME AGENTFLOW - BACKEND SYNCHRONOUS VERIFICATION
==================================================
--- 1. Testing Inference Backend --- => Inference Backend PASS
--- 2. Testing Templates Catalog --- => Templates Catalog PASS
--- 3. Testing Local Knowledge Engine --- => Knowledge Engine PASS
--- 4. Testing AI Models Registry --- => AI Models Registry PASS
--- 5. Testing Database Tables & Models --- => Database Verification PASS
==================================================
   ALL VERIFICATION CHECKS PASSED (5/5) SUCCESS
==================================================
```

### Step 2: Run Security & Execution Remediation Test Suite
```bash
python agentflow/tests/verify_remediation.py
```
Expected output:
```text
--- TEST: Authentication & Tenant Isolation --- [PASS]
--- TEST: Workflow Versioning & Snapshot Execution --- [PASS]
--- TEST: Atomic Approval Lifecycle & Decision Safety --- [PASS]
--- TEST: Honest Operational Status & Air-Gap Compliance --- [PASS]
ALL REMEDIATION CHECKS PASSED (4/4) SUCCESSFUL
```

### Step 3: Probe Health Endpoint via HTTP
```bash
curl -s http://localhost:8000/health
```
Expected JSON response:
```json
{
  "status": "healthy",
  "service": "DME AgentFlow API Engine",
  "company": "Digital Mind Engineering (DME), Jordan",
  "tagline": "Your Business. Your Data. Your AI.",
  "deployment_profile": "FULLY_PRIVATE_AIRGAPPED",
  "airgapped_verified": true,
  "local_ai_inference": "ACTIVE"
}
```

---

## 10. Troubleshooting & Maintenance Runbook

| Symptom | Probable Cause | Corrective Action |
|---|---|---|
| `HTTP 401 Unauthorized` on `/api/v1/...` routes | Anonymous request without Bearer token | Include `Authorization: Bearer <valid_jwt>` obtained from `/api/v1/auth/login`. |
| `HTTP 403 Forbidden` on valid token | User lacks role privilege or cross-tenant org ID mismatch | Verify user's assigned role in `organization_members`. Ensure token claims match requested organization. |
| `HTTP 409 Conflict` during approval | Competing approver or repeated decision | Request was already decided. Refresh the Approvals page to view decider name and timestamp. |
| `HTTP 400 Edge references non-existent node` | Disconnected or orphaned node in React Flow canvas | Ensure all node blocks have connected inputs/outputs before publishing. |
| `Inference Backend using emulation engine` | `llama-cpp-python` wheel missing or C++ build failed | Reinstall pre-compiled wheel or check `AI_INFERENCE.md` for compiler requirements. Emulation mode remains fully functional for business logic evaluation. |
| Database lock on SQLite (`OperationalError: database is locked`) | High concurrent write contention | Switch to PostgreSQL in production via `DATABASE_URL=postgresql+asyncpg://...`. |
