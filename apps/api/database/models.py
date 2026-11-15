from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    name = Column(String(128), nullable=False)
    industry = Column(String(64), default="General")
    country = Column(String(64), default="Jordan")
    language = Column(String(16), default="en")
    timezone = Column(String(64), default="Asia/Amman")
    deployment_profile = Column(String(64), default="FULLY_PRIVATE_AIRGAPPED")
    edition = Column(String(32), default="ENTERPRISE_PRIVATE")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    full_name = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    org_id = Column(String(64), ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(32), default="ORGANIZATION_ADMIN")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    org_id = Column(String(64), ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, default="")
    category = Column(String(64), default="General")
    version = Column(Integer, default=1)
    is_published = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    nodes_json = Column(JSON, default=list)
    edges_json = Column(JSON, default=list)
    # Stored immutable snapshot of published graph definition
    published_snapshot_json = Column(JSON, nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    org_id = Column(String(64), ForeignKey("organizations.id"), nullable=False, index=True)
    workflow_id = Column(String(64), ForeignKey("workflows.id"), nullable=False, index=True)
    workflow_version = Column(Integer, default=1)
    status = Column(String(32), default="QUEUED", index=True)
    is_draft_test = Column(Boolean, default=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, default=0)
    trigger_type = Column(String(64), default="manual_trigger")
    trigger_payload_json = Column(JSON, default=dict)
    current_node_id = Column(String(64), nullable=True)
    node_records_json = Column(JSON, default=dict)
    context_data_json = Column(JSON, default=dict)
    error_message = Column(Text, nullable=True)
    approval_request_id = Column(String(64), nullable=True)

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    org_id = Column(String(64), ForeignKey("organizations.id"), nullable=False, index=True)
    workflow_id = Column(String(64), nullable=False)
    execution_id = Column(String(64), nullable=False, index=True)
    node_id = Column(String(64), nullable=False)
    title = Column(String(128), nullable=False)
    description = Column(Text, default="")
    action_type = Column(String(64), default="QUOTATION_DISPATCH")
    payload_json = Column(JSON, default=dict)
    status = Column(String(32), default="PENDING", index=True)
    assigned_role = Column(String(32), default="APPROVER")
    requested_by = Column(String(64), default="system")
    decided_by = Column(String(64), nullable=True)
    decided_at = Column(DateTime, nullable=True)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AIAgent(Base):
    __tablename__ = "ai_agents"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    org_id = Column(String(64), ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, default="")
    instructions = Column(Text, nullable=False)
    model_id = Column(String(64), default="gemma-4-e4b-instruct")
    temperature = Column(Float, default=0.2)
    max_tokens = Column(Integer, default=1024)
    output_schema_json = Column(JSON, default=dict)
    knowledge_base_ids_json = Column(JSON, default=list)
    tools_json = Column(JSON, default=list)
    budget_tokens = Column(Integer, default=50000)
    approval_required = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AIModelRegistry(Base):
    __tablename__ = "ai_models"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    name = Column(String(128), nullable=False)
    family = Column(String(64), default="Google Gemma 4")
    file_path = Column(String(256), nullable=False)
    quantization = Column(String(32), default="Q4_K_M")
    context_length = Column(Integer, default=4096)
    cpu_threads = Column(Integer, default=4)
    gpu_layers = Column(Integer, default=0)
    is_active = Column(Boolean, default=False)
    status = Column(String(32), default="UNLOADED")
    memory_bytes = Column(Integer, default=0)
    latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    org_id = Column(String(64), ForeignKey("organizations.id"), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    file_name = Column(String(256), nullable=False)
    file_type = Column(String(32), nullable=False)
    file_size = Column(Integer, default=0)
    storage_key = Column(String(256), nullable=True)
    chunk_count = Column(Integer, default=0)
    status = Column(String(32), default="READY")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    org_id = Column(String(64), ForeignKey("organizations.id"), nullable=False, index=True)
    document_id = Column(String(64), ForeignKey("knowledge_documents.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding_json = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class CRMContact(Base):
    __tablename__ = "crm_contacts"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    org_id = Column(String(64), ForeignKey("organizations.id"), nullable=False, index=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), default="")
    email = Column(String(128), nullable=False)
    phone = Column(String(64), default="")
    company_name = Column(String(128), default="")
    status = Column(String(32), default="LEAD")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class CRMLead(Base):
    __tablename__ = "crm_leads"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    org_id = Column(String(64), ForeignKey("organizations.id"), nullable=False, index=True)
    contact_id = Column(String(64), nullable=True)
    title = Column(String(128), nullable=False)
    source = Column(String(64), default="Inbound Web")
    score = Column(Integer, default=50)
    estimated_value = Column(Float, default=0.0)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class CRMOpportunity(Base):
    __tablename__ = "crm_opportunities"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    org_id = Column(String(64), ForeignKey("organizations.id"), nullable=False, index=True)
    lead_id = Column(String(64), nullable=True)
    title = Column(String(128), nullable=False)
    stage = Column(String(32), default="DISCOVERY")
    amount = Column(Float, default=0.0)
    probability = Column(Integer, default=50)
    close_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class CRMTask(Base):
    __tablename__ = "crm_tasks"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    org_id = Column(String(64), ForeignKey("organizations.id"), nullable=False, index=True)
    title = Column(String(128), nullable=False)
    description = Column(Text, default="")
    priority = Column(String(32), default="NORMAL")
    assigned_to = Column(String(128), default="AgentFlow Operator")
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class IntegrationConfig(Base):
    __tablename__ = "integration_configs"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    org_id = Column(String(64), ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    type = Column(String(32), nullable=False)
    config_json = Column(JSON, default=dict)
    encrypted_credentials = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    status = Column(String(32), default="UNCONFIGURED")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    org_id = Column(String(64), ForeignKey("organizations.id"), nullable=False, index=True)
    actor_email = Column(String(128), nullable=False)
    action = Column(String(64), nullable=False)
    resource_type = Column(String(64), nullable=False)
    resource_id = Column(String(64), nullable=True)
    details_json = Column(JSON, default=dict)
    ip_address = Column(String(64), default="127.0.0.1")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class LicenseRecord(Base):
    __tablename__ = "license_records"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    org_id = Column(String(64), ForeignKey("organizations.id"), nullable=False, unique=True)
    edition = Column(String(32), default="ENTERPRISE_PRIVATE")
    license_key = Column(Text, nullable=False)
    is_valid = Column(Boolean, default=True)
    issued_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    limits_json = Column(JSON, default=dict)
