/**
 * DME AgentFlow - Shared TypeScript Definitions
 * Digital Mind Engineering (DME), Jordan
 * "Your Business. Your Data. Your AI."
 */

export type UserRole =
  | 'PLATFORM_OWNER'
  | 'ORGANIZATION_OWNER'
  | 'ORGANIZATION_ADMIN'
  | 'WORKFLOW_EDITOR'
  | 'APPROVER'
  | 'VIEWER';

export type DeploymentProfile =
  | 'CLOUD_SAAS'
  | 'CUSTOMER_HOSTED_HYBRID'
  | 'FULLY_PRIVATE_AIRGAPPED';

export type CommercialEdition =
  | 'STARTER'
  | 'PROFESSIONAL'
  | 'ENTERPRISE_PRIVATE';

export type ExecutionStatus =
  | 'QUEUED'
  | 'RUNNING'
  | 'WAITING_APPROVAL'
  | 'WAITING_RETRY'
  | 'COMPLETED'
  | 'FAILED'
  | 'CANCELLED';

export type NodeCategory =
  | 'TRIGGER'
  | 'LOGIC'
  | 'AI'
  | 'ACTION'
  | 'HUMAN'
  | 'COMPLETION';

export type TriggerNodeType =
  | 'manual_trigger'
  | 'form_submission'
  | 'webhook'
  | 'scheduled_trigger'
  | 'email_received';

export type LogicNodeType =
  | 'condition'
  | 'branching'
  | 'switch_router'
  | 'data_transformation'
  | 'validation'
  | 'delay'
  | 'bounded_loop'
  | 'parallel_execution';

export type AINodeType =
  | 'classify_text'
  | 'extract_structured'
  | 'summarize_text'
  | 'generate_response'
  | 'retrieve_knowledge'
  | 'invoke_agent'
  | 'interpret_document';

export type ActionNodeType =
  | 'create_crm_contact'
  | 'create_crm_lead'
  | 'update_crm_opportunity'
  | 'create_internal_task'
  | 'send_email'
  | 'http_request'
  | 'generate_document'
  | 'create_notification'
  | 'save_business_record';

export type HumanNodeType =
  | 'request_approval'
  | 'approve_reject'
  | 'request_clarification'
  | 'manual_intervention';

export type CompletionNodeType = 'success' | 'failure';

export interface WorkflowNode {
  id: string;
  name: string;
  category: NodeCategory;
  type: string;
  position: { x: number; y: number };
  config: Record<string, any>;
  inputs?: Record<string, any>;
  outputs?: Record<string, any>;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
  condition?: string;
}

export interface WorkflowDefinition {
  id?: string;
  orgId: string;
  name: string;
  description?: string;
  version: number;
  isPublished: boolean;
  isActive: boolean;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  metadata?: Record<string, any>;
  createdAt?: string;
  updatedAt?: string;
}

export interface NodeExecutionRecord {
  nodeId: string;
  nodeName: string;
  nodeType: string;
  category: NodeCategory;
  status: ExecutionStatus;
  startedAt?: string;
  completedAt?: string;
  durationMs?: number;
  inputs?: Record<string, any>;
  outputs?: Record<string, any>;
  errorMessage?: string;
}

export interface WorkflowExecution {
  id: string;
  workflowId: string;
  orgId: string;
  status: ExecutionStatus;
  startedAt: string;
  completedAt?: string;
  durationMs?: number;
  triggerType: string;
  triggerPayload: Record<string, any>;
  currentNodeId?: string;
  nodeRecords: Record<string, NodeExecutionRecord>;
  contextData: Record<string, any>;
  error?: string;
  approvalRequestId?: string;
}

export interface ApprovalRequest {
  id: string;
  orgId: string;
  workflowId: string;
  executionId: string;
  nodeId: string;
  title: string;
  description: string;
  actionType: string;
  payload: Record<string, any>;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'CLARIFICATION_REQUESTED';
  assignedRole: UserRole;
  requestedBy: string;
  decidedBy?: string;
  decidedAt?: string;
  comments?: string;
  createdAt: string;
}

export interface AIAgent {
  id: string;
  orgId: string;
  name: string;
  description: string;
  instructions: string;
  modelId: string;
  temperature: number;
  maxTokens: number;
  outputSchema?: Record<string, any>;
  knowledgeBaseIds: string[];
  tools: string[];
  executionBudgetTokens: number;
  approvalRequired: boolean;
  version: number;
}

export interface AIModelRecord {
  id: string;
  name: string;
  family: string;
  filePath: string;
  quantization: string;
  contextLength: number;
  cpuThreads: number;
  gpuLayers: number;
  temperature: number;
  isActive: boolean;
  isLoaded: boolean;
  status: 'UNLOADED' | 'LOADING' | 'READY' | 'ERROR';
  memoryBytesUsage: number;
  lastLatencyMs: number;
  detectionMetadata?: Record<string, any>;
}

export interface KnowledgeDocument {
  id: string;
  orgId: string;
  title: string;
  fileName: string;
  fileType: 'pdf' | 'docx' | 'txt' | 'md' | 'csv';
  fileSize: number;
  chunkCount: number;
  status: 'PROCESSING' | 'INDEXED' | 'FAILED';
  createdAt: string;
}

export interface CRMContact {
  id: string;
  orgId: string;
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  companyName?: string;
  status: 'LEAD' | 'OPPORTUNITY' | 'CUSTOMER' | 'INACTIVE';
  createdAt: string;
}

export interface CRMLead {
  id: string;
  orgId: string;
  title: string;
  contactName: string;
  contactEmail: string;
  source: string;
  score: number;
  status: 'NEW' | 'QUALIFIED' | 'DISQUALIFIED' | 'CONVERTED';
  estimatedValue?: number;
  notes?: string;
  createdAt: string;
}

export interface CRMOpportunity {
  id: string;
  orgId: string;
  title: string;
  contactId?: string;
  leadId?: string;
  stage: 'DISCOVERY' | 'PROPOSAL' | 'NEGOTIATION' | 'WON' | 'LOST';
  amount: number;
  probability: number;
  closeDate?: string;
  createdAt: string;
}

export interface LicenseInfo {
  edition: CommercialEdition;
  organizationId: string;
  organizationName: string;
  validUntil: string;
  maxUsers: number;
  maxWorkflows: number;
  maxExecutionsPerMonth: number;
  features: string[];
  isAirgappedValid: boolean;
  signature: string;
}
