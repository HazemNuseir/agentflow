-- ============================================================
-- DME AgentFlow V2 — PostgreSQL Initial Schema
-- Migration: 001_initial_schema.sql
-- Target: PostgreSQL 15+ with pgvector extension
-- ============================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================
-- Table: organizations
-- Tenant root; every resource belongs to one organization.
-- ============================================================
CREATE TABLE IF NOT EXISTS organizations (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    name            VARCHAR(128)  NOT NULL,
    industry        VARCHAR(64)   NOT NULL DEFAULT 'General',
    country         VARCHAR(64)   NOT NULL DEFAULT 'Jordan',
    language        VARCHAR(16)   NOT NULL DEFAULT 'en',
    timezone        VARCHAR(64)   NOT NULL DEFAULT 'Asia/Amman',
    deployment_profile VARCHAR(64) NOT NULL DEFAULT 'FULLY_PRIVATE_AIRGAPPED',
    edition         VARCHAR(32)   NOT NULL DEFAULT 'ENTERPRISE_PRIVATE',
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE organizations IS 'Top-level tenant entity; all resources are scoped to an organization.';

-- ============================================================
-- Table: users
-- Platform users; linked to organizations via organization_members.
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    email           VARCHAR(128)  NOT NULL UNIQUE,
    hashed_password VARCHAR(256)  NOT NULL,
    full_name       VARCHAR(128)  NOT NULL,
    is_active       BOOLEAN       NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);

COMMENT ON TABLE users IS 'Platform user accounts; authentication credentials stored as bcrypt hashes.';

-- ============================================================
-- Table: organization_members
-- Many-to-many join between users and organizations, with RBAC role.
-- Roles: VIEWER, APPROVER, WORKFLOW_EDITOR, ORGANIZATION_ADMIN
-- ============================================================
CREATE TABLE IF NOT EXISTS organization_members (
    id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    org_id      TEXT        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id     TEXT        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role        VARCHAR(32) NOT NULL DEFAULT 'ORGANIZATION_ADMIN',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (org_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_org_members_org_id  ON organization_members (org_id);
CREATE INDEX IF NOT EXISTS idx_org_members_user_id ON organization_members (user_id);

COMMENT ON TABLE organization_members IS 'RBAC membership table; a user can belong to multiple organizations with different roles.';

-- ============================================================
-- Table: ai_models
-- Registry of GGUF model files available for local inference.
-- ============================================================
CREATE TABLE IF NOT EXISTS ai_models (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    name            VARCHAR(128)  NOT NULL,
    family          VARCHAR(64)   NOT NULL DEFAULT 'Google Gemma 4',
    file_path       VARCHAR(256)  NOT NULL,
    quantization    VARCHAR(32)   NOT NULL DEFAULT 'Q4_K_M',
    context_length  INTEGER       NOT NULL DEFAULT 4096,
    cpu_threads     INTEGER       NOT NULL DEFAULT 4,
    gpu_layers      INTEGER       NOT NULL DEFAULT 0,
    is_active       BOOLEAN       NOT NULL DEFAULT FALSE,
    status          VARCHAR(32)   NOT NULL DEFAULT 'UNLOADED',
    memory_bytes    BIGINT        NOT NULL DEFAULT 0,
    latency_ms      DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE ai_models IS 'Registry of local GGUF model files; only one model active at a time per deployment.';

-- ============================================================
-- Table: workflows
-- Workflow definitions with version history and published snapshots.
-- published_snapshot_json is the immutable graph used by in-progress runs.
-- ============================================================
CREATE TABLE IF NOT EXISTS workflows (
    id                      TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    org_id                  TEXT        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name                    VARCHAR(128) NOT NULL,
    description             TEXT         NOT NULL DEFAULT '',
    category                VARCHAR(64)  NOT NULL DEFAULT 'General',
    version                 INTEGER      NOT NULL DEFAULT 1,
    is_published            BOOLEAN      NOT NULL DEFAULT FALSE,
    is_active               BOOLEAN      NOT NULL DEFAULT TRUE,
    nodes_json              JSONB        NOT NULL DEFAULT '[]',
    edges_json              JSONB        NOT NULL DEFAULT '[]',
    published_snapshot_json JSONB,
    metadata_json           JSONB        NOT NULL DEFAULT '{}',
    created_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workflows_org_id     ON workflows (org_id);
CREATE INDEX IF NOT EXISTS idx_workflows_is_active  ON workflows (is_active);
CREATE INDEX IF NOT EXISTS idx_workflows_category   ON workflows (category);

COMMENT ON TABLE workflows IS 'Workflow graph definitions; published_snapshot_json is the immutable version used by running executions.';

-- ============================================================
-- Table: workflow_executions
-- Runtime state for each workflow run.
-- ============================================================
CREATE TABLE IF NOT EXISTS workflow_executions (
    id                      TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    org_id                  TEXT        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    workflow_id             TEXT        NOT NULL REFERENCES workflows(id),
    workflow_version        INTEGER     NOT NULL DEFAULT 1,
    status                  VARCHAR(32) NOT NULL DEFAULT 'QUEUED',
    is_draft_test           BOOLEAN     NOT NULL DEFAULT FALSE,
    started_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at            TIMESTAMPTZ,
    duration_ms             INTEGER     NOT NULL DEFAULT 0,
    trigger_type            VARCHAR(64) NOT NULL DEFAULT 'manual_trigger',
    trigger_payload_json    JSONB       NOT NULL DEFAULT '{}',
    current_node_id         TEXT,
    node_records_json       JSONB       NOT NULL DEFAULT '{}',
    context_data_json       JSONB       NOT NULL DEFAULT '{}',
    error_message           TEXT,
    approval_request_id     TEXT
);

CREATE INDEX IF NOT EXISTS idx_executions_org_id      ON workflow_executions (org_id);
CREATE INDEX IF NOT EXISTS idx_executions_workflow_id ON workflow_executions (workflow_id);
CREATE INDEX IF NOT EXISTS idx_executions_status      ON workflow_executions (status);
CREATE INDEX IF NOT EXISTS idx_executions_started_at  ON workflow_executions (started_at DESC);

COMMENT ON TABLE workflow_executions IS 'Live and historical execution records; status transitions: QUEUED→RUNNING→AWAITING_APPROVAL→COMPLETED/FAILED/CANCELLED.';

-- ============================================================
-- Table: approval_requests
-- Human-in-the-loop decision records; atomic status transitions enforced at application layer.
-- ============================================================
CREATE TABLE IF NOT EXISTS approval_requests (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    org_id          TEXT        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    workflow_id     TEXT        NOT NULL,
    execution_id    TEXT        NOT NULL,
    node_id         TEXT        NOT NULL,
    title           VARCHAR(128) NOT NULL,
    description     TEXT         NOT NULL DEFAULT '',
    action_type     VARCHAR(64)  NOT NULL DEFAULT 'QUOTATION_DISPATCH',
    payload_json    JSONB        NOT NULL DEFAULT '{}',
    status          VARCHAR(32)  NOT NULL DEFAULT 'PENDING',
    assigned_role   VARCHAR(32)  NOT NULL DEFAULT 'APPROVER',
    requested_by    VARCHAR(64)  NOT NULL DEFAULT 'system',
    decided_by      TEXT,
    decided_at      TIMESTAMPTZ,
    comments        TEXT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_approvals_org_id       ON approval_requests (org_id);
CREATE INDEX IF NOT EXISTS idx_approvals_execution_id ON approval_requests (execution_id);
CREATE INDEX IF NOT EXISTS idx_approvals_status       ON approval_requests (status);
CREATE INDEX IF NOT EXISTS idx_approvals_created_at   ON approval_requests (created_at DESC);

COMMENT ON TABLE approval_requests IS 'Human approval checkpoints; status transitions from PENDING are made atomic via SELECT FOR UPDATE in the application layer.';

-- ============================================================
-- Table: ai_agents
-- Configured AI agents with their prompts, model, and tool bindings.
-- ============================================================
CREATE TABLE IF NOT EXISTS ai_agents (
    id                      TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    org_id                  TEXT        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name                    VARCHAR(128) NOT NULL,
    description             TEXT         NOT NULL DEFAULT '',
    instructions            TEXT         NOT NULL,
    model_id                VARCHAR(64)  NOT NULL DEFAULT 'gemma-4-e4b-instruct',
    temperature             DOUBLE PRECISION NOT NULL DEFAULT 0.2,
    max_tokens              INTEGER      NOT NULL DEFAULT 1024,
    output_schema_json      JSONB        NOT NULL DEFAULT '{}',
    knowledge_base_ids_json JSONB        NOT NULL DEFAULT '[]',
    tools_json              JSONB        NOT NULL DEFAULT '[]',
    budget_tokens           INTEGER      NOT NULL DEFAULT 50000,
    approval_required       BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_agents_org_id ON ai_agents (org_id);

COMMENT ON TABLE ai_agents IS 'AI agent configurations; bound to local inference models and optional knowledge bases.';

-- ============================================================
-- Table: knowledge_documents
-- Uploaded documents ingested into the local knowledge base.
-- ============================================================
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    org_id          TEXT        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    title           VARCHAR(256) NOT NULL,
    file_name       VARCHAR(256) NOT NULL,
    file_type       VARCHAR(32)  NOT NULL,
    file_size       INTEGER      NOT NULL DEFAULT 0,
    storage_key     VARCHAR(256),
    chunk_count     INTEGER      NOT NULL DEFAULT 0,
    status          VARCHAR(32)  NOT NULL DEFAULT 'READY',
    error_message   TEXT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_docs_org_id ON knowledge_documents (org_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_docs_status ON knowledge_documents (status);

COMMENT ON TABLE knowledge_documents IS 'Document metadata for the private knowledge base; content stored as chunks in knowledge_chunks.';

-- ============================================================
-- Table: knowledge_chunks
-- Text chunks with local vector embeddings for semantic search.
-- Uses pgvector for cosine similarity search.
-- ============================================================
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    org_id          TEXT        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    document_id     TEXT        NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    chunk_index     INTEGER     NOT NULL,
    content         TEXT        NOT NULL,
    embedding       vector(768),
    embedding_json  JSONB       NOT NULL DEFAULT '[]',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_org_id      ON knowledge_chunks (org_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_document_id ON knowledge_chunks (document_id);

-- pgvector cosine similarity index for semantic search
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_embedding
    ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

COMMENT ON TABLE knowledge_chunks IS 'Text chunks with 768-dim local vector embeddings; uses pgvector ivfflat index for semantic search.';

-- ============================================================
-- Table: crm_contacts
-- ============================================================
CREATE TABLE IF NOT EXISTS crm_contacts (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    org_id          TEXT        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    first_name      VARCHAR(64)  NOT NULL,
    last_name       VARCHAR(64)  NOT NULL DEFAULT '',
    email           VARCHAR(128) NOT NULL,
    phone           VARCHAR(64)  NOT NULL DEFAULT '',
    company_name    VARCHAR(128) NOT NULL DEFAULT '',
    status          VARCHAR(32)  NOT NULL DEFAULT 'LEAD',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_crm_contacts_org_id ON crm_contacts (org_id);

COMMENT ON TABLE crm_contacts IS 'Internal CRM contact records; scoped to organization.';

-- ============================================================
-- Table: crm_leads
-- ============================================================
CREATE TABLE IF NOT EXISTS crm_leads (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    org_id          TEXT        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    contact_id      TEXT        REFERENCES crm_contacts(id),
    title           VARCHAR(128) NOT NULL,
    source          VARCHAR(64)  NOT NULL DEFAULT 'Inbound Web',
    score           INTEGER      NOT NULL DEFAULT 50,
    estimated_value DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    notes           TEXT         NOT NULL DEFAULT '',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_crm_leads_org_id ON crm_leads (org_id);

COMMENT ON TABLE crm_leads IS 'CRM lead tracking with AI-scored qualification.';

-- ============================================================
-- Table: crm_opportunities
-- ============================================================
CREATE TABLE IF NOT EXISTS crm_opportunities (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    org_id          TEXT        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    lead_id         TEXT        REFERENCES crm_leads(id),
    title           VARCHAR(128) NOT NULL,
    stage           VARCHAR(32)  NOT NULL DEFAULT 'DISCOVERY',
    amount          DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    probability     INTEGER      NOT NULL DEFAULT 50,
    close_date      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_crm_opportunities_org_id ON crm_opportunities (org_id);
CREATE INDEX IF NOT EXISTS idx_crm_opportunities_stage  ON crm_opportunities (stage);

COMMENT ON TABLE crm_opportunities IS 'Sales pipeline opportunities linked to leads.';

-- ============================================================
-- Table: crm_tasks
-- ============================================================
CREATE TABLE IF NOT EXISTS crm_tasks (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    org_id          TEXT        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    title           VARCHAR(128) NOT NULL,
    description     TEXT         NOT NULL DEFAULT '',
    priority        VARCHAR(32)  NOT NULL DEFAULT 'NORMAL',
    assigned_to     VARCHAR(128) NOT NULL DEFAULT 'AgentFlow Operator',
    is_completed    BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_crm_tasks_org_id ON crm_tasks (org_id);

COMMENT ON TABLE crm_tasks IS 'CRM task tracking; can be auto-created by workflow executions.';

-- ============================================================
-- Table: integration_configs
-- ============================================================
CREATE TABLE IF NOT EXISTS integration_configs (
    id                      TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    org_id                  TEXT        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name                    VARCHAR(128) NOT NULL,
    type                    VARCHAR(32)  NOT NULL,
    config_json             JSONB        NOT NULL DEFAULT '{}',
    encrypted_credentials   TEXT         NOT NULL DEFAULT '',
    is_active               BOOLEAN      NOT NULL DEFAULT TRUE,
    status                  VARCHAR(32)  NOT NULL DEFAULT 'UNCONFIGURED',
    created_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_integration_configs_org_id ON integration_configs (org_id);

COMMENT ON TABLE integration_configs IS 'Business integration configurations (email, ERP, webhook, etc.); credentials stored encrypted.';

-- ============================================================
-- Table: audit_logs
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    org_id          TEXT        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    actor_email     VARCHAR(128) NOT NULL,
    action          VARCHAR(64)  NOT NULL,
    resource_type   VARCHAR(64)  NOT NULL,
    resource_id     TEXT,
    details_json    JSONB        NOT NULL DEFAULT '{}',
    ip_address      VARCHAR(64)  NOT NULL DEFAULT '127.0.0.1',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_org_id     ON audit_logs (org_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_actor      ON audit_logs (actor_email);

COMMENT ON TABLE audit_logs IS 'Immutable audit trail for all significant system actions; append-only by convention.';

-- ============================================================
-- Table: license_records
-- ============================================================
CREATE TABLE IF NOT EXISTS license_records (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    org_id          TEXT        NOT NULL UNIQUE REFERENCES organizations(id) ON DELETE CASCADE,
    edition         VARCHAR(32)  NOT NULL DEFAULT 'ENTERPRISE_PRIVATE',
    license_key     TEXT         NOT NULL,
    is_valid        BOOLEAN      NOT NULL DEFAULT TRUE,
    issued_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ,
    limits_json     JSONB        NOT NULL DEFAULT '{}'
);

COMMENT ON TABLE license_records IS 'Commercial license records; one per organization.';

-- ============================================================
-- Done
-- ============================================================
SELECT 'DME AgentFlow V2 — Initial Schema Applied' AS status,
       COUNT(*) AS table_count
FROM   information_schema.tables
WHERE  table_schema = 'public'
  AND  table_type   = 'BASE TABLE';
