# DME AgentFlow — Architecture & Setup Guide

**Digital Mind Engineering (DME)**, Jordan  
**Platform**: Intelligent Business Automation  

---

## 1. System Requirements & Prerequisites

- **Python**: 3.12+ (Python 3.14 compatible)
- **Node.js**: v20+ or v24+
- **Database**: SQLite (built-in default) or PostgreSQL 16 with `pgvector`
- **Memory**: Minimum 8 GB RAM (16 GB recommended for Gemma 4 12B/26B models)

---

## 2. Environment Configuration (`.env`)

Configure the following environment parameters:

```env
# Application
PROJECT_NAME="DME AgentFlow"
SECRET_KEY="<GENERATE_RANDOM_64_CHAR_HEX>"
DEPLOYMENT_PROFILE="FULLY_PRIVATE_AIRGAPPED"

# Database
DATABASE_URL="sqlite+aiosqlite:///./agentflow.db"

# Storage
DATA_DIR="./data"
MODELS_DIR="./models"
UPLOADS_DIR="./data/uploads"
DOCUMENTS_DIR="./data/documents"

# AI Inference (Gemma 4)
DEFAULT_MODEL_NAME="gemma-4-e4b-instruct.Q4_K_M.gguf"
DEFAULT_CONTEXT_LENGTH=4096
DEFAULT_CPU_THREADS=4
DEFAULT_GPU_LAYERS=0

# Security & Network Policies
ALLOW_OUTBOUND_NETWORK=false
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

---

## 3. Database Schema Migrations

The database models are managed via SQLAlchemy 2. The initial schema and subsequent remediation columns can be synchronized using SQLite or Alembic:

### Remediation Columns Added:
- `workflows.published_snapshot_json`: Stores immutable snapshot of published node graph.
- `workflow_executions.is_draft_test`: Separates evaluation runs from production triggers.
- `workflow_executions.workflow_version`: Tracks exact workflow version executed.
- `knowledge_documents.storage_key`: Unique generated object storage identifier.
- `knowledge_documents.error_message`: Explicit capture of document parsing failures.
- `crm_leads.contact_id`: Foreign key linking leads to CRM contacts.

### Manual SQL Migration Commands (for existing SQLite databases):
```sql
ALTER TABLE workflows ADD COLUMN published_snapshot_json JSON;
ALTER TABLE workflow_executions ADD COLUMN is_draft_test BOOLEAN DEFAULT 0;
ALTER TABLE workflow_executions ADD COLUMN workflow_version INTEGER DEFAULT 1;
ALTER TABLE knowledge_documents ADD COLUMN storage_key VARCHAR(256);
ALTER TABLE knowledge_documents ADD COLUMN error_message TEXT;
ALTER TABLE crm_leads ADD COLUMN contact_id VARCHAR(64);
```

---

## 4. Running the Platform

### Backend Service:
```bash
cd agentflow/apps/api
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Verification Suite:
```bash
python agentflow/tests/verify_remediation.py
python agentflow/tests/verify_backend.py
```
