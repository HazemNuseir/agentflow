/**
 * DME AgentFlow - Workflow Schemas and Node Specifications
 * Digital Mind Engineering (DME), Jordan
 */

export interface NodeDefinitionMeta {
  type: string;
  category: 'TRIGGER' | 'LOGIC' | 'AI' | 'ACTION' | 'HUMAN' | 'COMPLETION';
  label: string;
  labelAr: string;
  description: string;
  icon: string;
  defaultConfig: Record<string, any>;
  inputs: Array<{ name: string; type: string; required?: boolean }>;
  outputs: Array<{ name: string; type: string }>;
}

export const NODE_CATALOG: Record<string, NodeDefinitionMeta> = {
  // --- TRIGGERS ---
  manual_trigger: {
    type: 'manual_trigger',
    category: 'TRIGGER',
    label: 'Manual Trigger',
    labelAr: 'تشغيل يدوي',
    description: 'Trigger workflow manually via button or API test payload',
    icon: 'PlayCircle',
    defaultConfig: { initialPayload: {} },
    inputs: [],
    outputs: [{ name: 'payload', type: 'object' }]
  },
  form_submission: {
    type: 'form_submission',
    category: 'TRIGGER',
    label: 'Form Submission',
    labelAr: 'إرسال نموذج',
    description: 'Triggers when a web intake form or lead form is submitted',
    icon: 'FileText',
    defaultConfig: { formId: 'default_lead_form' },
    inputs: [],
    outputs: [{ name: 'formData', type: 'object' }]
  },
  webhook: {
    type: 'webhook',
    category: 'TRIGGER',
    label: 'Inbound Webhook',
    labelAr: 'ويب هوك وارد',
    description: 'Triggers when an external HTTP POST request is received',
    icon: 'Globe',
    defaultConfig: { path: '/webhook/v1', secretToken: '' },
    inputs: [],
    outputs: [{ name: 'headers', type: 'object' }, { name: 'body', type: 'object' }]
  },
  scheduled_trigger: {
    type: 'scheduled_trigger',
    category: 'TRIGGER',
    label: 'Schedule Trigger',
    labelAr: 'تشغيل مجدول',
    description: 'Runs on a defined recurring cron or interval pattern',
    icon: 'Clock',
    defaultConfig: { cronExpression: '0 9 * * 1-5', timezone: 'Asia/Amman' },
    inputs: [],
    outputs: [{ name: 'timestamp', type: 'string' }]
  },
  email_received: {
    type: 'email_received',
    category: 'TRIGGER',
    label: 'Email Ingestion',
    labelAr: 'استلام بريد إلكتروني',
    description: 'Triggers upon receiving customer email via IMAP/SMTP gateway',
    icon: 'Mail',
    defaultConfig: { mailbox: 'inbox', filterSubject: '' },
    inputs: [],
    outputs: [{ name: 'sender', type: 'string' }, { name: 'subject', type: 'string' }, { name: 'body', type: 'string' }]
  },

  // --- LOGIC ---
  condition: {
    type: 'condition',
    category: 'LOGIC',
    label: 'Condition (If/Else)',
    labelAr: 'شرط منطقي',
    description: 'Evaluates expressions and routes to True or False branches',
    icon: 'GitFork',
    defaultConfig: { field: 'score', operator: 'gte', value: 70 },
    inputs: [{ name: 'input', type: 'any', required: true }],
    outputs: [{ name: 'true', type: 'any' }, { name: 'false', type: 'any' }]
  },
  branching: {
    type: 'branching',
    category: 'LOGIC',
    label: 'Multi-Branch',
    labelAr: 'تفرع متعدد',
    description: 'Evaluates multiple condition sets to determine flow',
    icon: 'Split',
    defaultConfig: { branches: [] },
    inputs: [{ name: 'input', type: 'any', required: true }],
    outputs: [{ name: 'matched', type: 'any' }, { name: 'default', type: 'any' }]
  },
  switch_router: {
    type: 'switch_router',
    category: 'LOGIC',
    label: 'Switch Router',
    labelAr: 'موجّه المسارات',
    description: 'Matches a specific key or classification to designated branches',
    icon: 'Layers',
    defaultConfig: { targetKey: 'category', cases: ['Support', 'Sales', 'General'] },
    inputs: [{ name: 'input', type: 'object', required: true }],
    outputs: [{ name: 'out', type: 'any' }]
  },
  data_transformation: {
    type: 'data_transformation',
    category: 'LOGIC',
    label: 'Transform Data',
    labelAr: 'تحويل البيانات',
    description: 'Map, reshape, and clean JSON payloads',
    icon: 'Cpu',
    defaultConfig: { mappingRules: {} },
    inputs: [{ name: 'source', type: 'object', required: true }],
    outputs: [{ name: 'result', type: 'object' }]
  },
  validation: {
    type: 'validation',
    category: 'LOGIC',
    label: 'Schema Validation',
    labelAr: 'التحقق من البيانات',
    description: 'Validates structure against required fields and types',
    icon: 'ShieldCheck',
    defaultConfig: { requiredFields: ['email', 'requirements'] },
    inputs: [{ name: 'data', type: 'object', required: true }],
    outputs: [{ name: 'valid', type: 'object' }, { name: 'invalid', type: 'object' }]
  },
  delay: {
    type: 'delay',
    category: 'LOGIC',
    label: 'Execution Delay',
    labelAr: 'تأخير التنفيذ',
    description: 'Pauses workflow execution for a designated interval',
    icon: 'Timer',
    defaultConfig: { seconds: 5 },
    inputs: [{ name: 'in', type: 'any' }],
    outputs: [{ name: 'out', type: 'any' }]
  },
  bounded_loop: {
    type: 'bounded_loop',
    category: 'LOGIC',
    label: 'Bounded Loop',
    labelAr: 'تكرار محدد',
    description: 'Iterates through an array with strict upper bounds to prevent runaway loops',
    icon: 'Repeat',
    defaultConfig: { arrayField: 'items', maxIterations: 50 },
    inputs: [{ name: 'items', type: 'array', required: true }],
    outputs: [{ name: 'item', type: 'any' }, { name: 'done', type: 'array' }]
  },
  parallel_execution: {
    type: 'parallel_execution',
    category: 'LOGIC',
    label: 'Parallel Fork',
    labelAr: 'تنفيذ متزامن',
    description: 'Dispatches multiple tasks simultaneously and awaits resolution',
    icon: 'Share2',
    defaultConfig: { waitAll: true },
    inputs: [{ name: 'input', type: 'any' }],
    outputs: [{ name: 'fork1', type: 'any' }, { name: 'fork2', type: 'any' }]
  },

  // --- AI NODES ---
  classify_text: {
    type: 'classify_text',
    category: 'AI',
    label: 'Classify Text',
    labelAr: 'تصنيف النص',
    description: 'Local Gemma classifies text into predefined operational categories',
    icon: 'Tag',
    defaultConfig: {
      categories: ['Sales Inquiry', 'Technical Support', 'Billing', 'Urgent Request'],
      inputField: 'inquiry_text'
    },
    inputs: [{ name: 'text', type: 'string', required: true }],
    outputs: [{ name: 'category', type: 'string' }, { name: 'confidence', type: 'number' }]
  },
  extract_structured: {
    type: 'extract_structured',
    category: 'AI',
    label: 'Extract Structured Data',
    labelAr: 'استخراج بيانات مهيكلة',
    description: 'Uses local Gemma to extract key-value JSON entities from freeform text',
    icon: 'Table',
    defaultConfig: {
      targetSchema: {
        client_name: 'string',
        budget: 'number',
        timeline: 'string',
        urgency: 'string'
      }
    },
    inputs: [{ name: 'text', type: 'string', required: true }],
    outputs: [{ name: 'extracted', type: 'object' }]
  },
  summarize_text: {
    type: 'summarize_text',
    category: 'AI',
    label: 'Summarize Text',
    labelAr: 'تلخيص النص',
    description: 'Produces concise bullet points or summaries of lengthy documents',
    icon: 'FileText',
    defaultConfig: { maxBulletPoints: 5, tone: 'professional' },
    inputs: [{ name: 'content', type: 'string', required: true }],
    outputs: [{ name: 'summary', type: 'string' }]
  },
  generate_response: {
    type: 'generate_response',
    category: 'AI',
    label: 'Generate Response',
    labelAr: 'توليد الرد',
    description: 'Drafts contextual communications, email replies, or advice',
    icon: 'MessageSquare',
    defaultConfig: {
      promptTemplate: 'Draft a professional response addressing the client inquiry.',
      temperature: 0.3
    },
    inputs: [{ name: 'context', type: 'any' }],
    outputs: [{ name: 'response_text', type: 'string' }]
  },
  retrieve_knowledge: {
    type: 'retrieve_knowledge',
    category: 'AI',
    label: 'Knowledge Retrieval (RAG)',
    labelAr: 'استرجاع المعرفة المؤسسية',
    description: 'Performs local semantic vector search across organization documents',
    icon: 'BookOpen',
    defaultConfig: { collection: 'default', topK: 3, scoreThreshold: 0.65 },
    inputs: [{ name: 'query', type: 'string', required: true }],
    outputs: [{ name: 'passages', type: 'array' }, { name: 'context_snippet', type: 'string' }]
  },
  invoke_agent: {
    type: 'invoke_agent',
    category: 'AI',
    label: 'Invoke Configured AI Agent',
    labelAr: 'استدعاء وكيل ذكاء اصطناعي',
    description: 'Delegates task to an autonomous agent defined in Agent Studio',
    icon: 'Bot',
    defaultConfig: { agentId: '', passFullContext: true },
    inputs: [{ name: 'task_input', type: 'any' }],
    outputs: [{ name: 'agent_output', type: 'any' }]
  },
  interpret_document: {
    type: 'interpret_document',
    category: 'AI',
    label: 'Interpret Document / RFQ',
    labelAr: 'تحليل مستند / طلب تسعير',
    description: 'Extracts technical specs, bill of materials, and compliance items from documents',
    icon: 'FileSearch',
    defaultConfig: { extractionType: 'rfq_specifications' },
    inputs: [{ name: 'document_text', type: 'string', required: true }],
    outputs: [{ name: 'parsed_specs', type: 'object' }, { name: 'line_items', type: 'array' }]
  },

  // --- ACTION NODES ---
  create_crm_contact: {
    type: 'create_crm_contact',
    category: 'ACTION',
    label: 'Create CRM Contact',
    labelAr: 'إنشاء جهة اتصال',
    description: 'Inserts or updates contact in internal tenant CRM',
    icon: 'UserPlus',
    defaultConfig: {},
    inputs: [{ name: 'contact', type: 'object', required: true }],
    outputs: [{ name: 'contactId', type: 'string' }]
  },
  create_crm_lead: {
    type: 'create_crm_lead',
    category: 'ACTION',
    label: 'Create CRM Lead',
    labelAr: 'إنشاء فرصة جديدة (Lead)',
    description: 'Creates lead with score, notes, and requirements',
    icon: 'TrendingUp',
    defaultConfig: {},
    inputs: [{ name: 'lead', type: 'object', required: true }],
    outputs: [{ name: 'leadId', type: 'string' }]
  },
  update_crm_opportunity: {
    type: 'update_crm_opportunity',
    category: 'ACTION',
    label: 'Update CRM Opportunity',
    labelAr: 'تحديث فرصة البيع',
    description: 'Updates deal stage, amount, probability, and activity log',
    icon: 'Briefcase',
    defaultConfig: { stage: 'PROPOSAL' },
    inputs: [{ name: 'opportunity', type: 'object', required: true }],
    outputs: [{ name: 'opportunityId', type: 'string' }]
  },
  create_internal_task: {
    type: 'create_internal_task',
    category: 'ACTION',
    label: 'Create Internal Task',
    labelAr: 'إنشاء مهمة داخلية',
    description: 'Creates an operational task assigned to team members',
    icon: 'CheckSquare',
    defaultConfig: { priority: 'NORMAL' },
    inputs: [{ name: 'task', type: 'object', required: true }],
    outputs: [{ name: 'taskId', type: 'string' }]
  },
  send_email: {
    type: 'send_email',
    category: 'ACTION',
    label: 'Send Email Notification',
    labelAr: 'إرسال بريد إلكتروني',
    description: 'Dispatches internal or external email via configured SMTP',
    icon: 'Send',
    defaultConfig: { toField: 'email', subject: 'DME AgentFlow Notification' },
    inputs: [{ name: 'message', type: 'object', required: true }],
    outputs: [{ name: 'status', type: 'string' }]
  },
  http_request: {
    type: 'http_request',
    category: 'ACTION',
    label: 'HTTP Request (REST API)',
    labelAr: 'طلب HTTP خارجي',
    description: 'Dispatches controlled REST API request with SSRF protection',
    icon: 'ExternalLink',
    defaultConfig: { method: 'POST', timeoutSeconds: 15 },
    inputs: [{ name: 'url', type: 'string', required: true }, { name: 'body', type: 'object' }],
    outputs: [{ name: 'response', type: 'object' }]
  },
  generate_document: {
    type: 'generate_document',
    category: 'ACTION',
    label: 'Generate Document (PDF/Quote)',
    labelAr: 'إنشاء مستند / عرض أسعار',
    description: 'Renders formal quotation, invoice draft, or report',
    icon: 'Printer',
    defaultConfig: { templateType: 'quotation_standard' },
    inputs: [{ name: 'data', type: 'object', required: true }],
    outputs: [{ name: 'documentUrl', type: 'string' }, { name: 'documentId', type: 'string' }]
  },
  create_notification: {
    type: 'create_notification',
    category: 'ACTION',
    label: 'Create In-App Notification',
    labelAr: 'إنشاء إشعار في النظام',
    description: 'Alerts organization members in the notification bell',
    icon: 'Bell',
    defaultConfig: { severity: 'INFO' },
    inputs: [{ name: 'notification', type: 'object', required: true }],
    outputs: [{ name: 'id', type: 'string' }]
  },
  save_business_record: {
    type: 'save_business_record',
    category: 'ACTION',
    label: 'Save Business Record',
    labelAr: 'حفظ سجل تجاري',
    description: 'Stores custom domain records or operational history',
    icon: 'Database',
    defaultConfig: { tableName: 'custom_records' },
    inputs: [{ name: 'record', type: 'object', required: true }],
    outputs: [{ name: 'recordId', type: 'string' }]
  },

  // --- HUMAN NODES ---
  request_approval: {
    type: 'request_approval',
    category: 'HUMAN',
    label: 'Request Approval',
    labelAr: 'طلب موافقة بشرية',
    description: 'Pauses workflow execution until authorized approver reviews details',
    icon: 'UserCheck',
    defaultConfig: {
      assignedRole: 'APPROVER',
      requireComments: true,
      timeoutHours: 48
    },
    inputs: [{ name: 'payload', type: 'object', required: true }],
    outputs: [{ name: 'decision', type: 'string' }, { name: 'approverNotes', type: 'string' }]
  },
  approve_reject: {
    type: 'approve_reject',
    category: 'HUMAN',
    label: 'Approve / Reject Gate',
    labelAr: 'بوابة الموافقة أو الرفض',
    description: 'Routes workflow based on explicit human decision',
    icon: 'CheckCircle',
    defaultConfig: {},
    inputs: [{ name: 'approvalState', type: 'object', required: true }],
    outputs: [{ name: 'approved', type: 'any' }, { name: 'rejected', type: 'any' }]
  },
  request_clarification: {
    type: 'request_clarification',
    category: 'HUMAN',
    label: 'Request Clarification',
    labelAr: 'طلب توضيح',
    description: 'Requests missing details from operator or customer',
    icon: 'HelpCircle',
    defaultConfig: {},
    inputs: [{ name: 'inquiry', type: 'object' }],
    outputs: [{ name: 'clarification', type: 'string' }]
  },
  manual_intervention: {
    type: 'manual_intervention',
    category: 'HUMAN',
    label: 'Manual Intervention',
    labelAr: 'تدخل يدوي',
    description: 'Requires human operator to inspect and edit state before resuming',
    icon: 'Wrench',
    defaultConfig: {},
    inputs: [{ name: 'state', type: 'object' }],
    outputs: [{ name: 'modifiedState', type: 'object' }]
  },

  // --- COMPLETION NODES ---
  success: {
    type: 'success',
    category: 'COMPLETION',
    label: 'Workflow Success',
    labelAr: 'اكتمال ناجح',
    description: 'Marks workflow execution as successfully resolved',
    icon: 'Check',
    defaultConfig: { message: 'Workflow completed successfully.' },
    inputs: [{ name: 'finalData', type: 'any' }],
    outputs: []
  },
  failure: {
    type: 'failure',
    category: 'COMPLETION',
    label: 'Workflow Terminated / Failed',
    labelAr: 'إنهاء أو فشل الإجراء',
    description: 'Terminates workflow with error diagnostics or rejection reason',
    icon: 'XCircle',
    defaultConfig: { reason: 'Process rejected or error encountered.' },
    inputs: [{ name: 'errorDetails', type: 'any' }],
    outputs: []
  }
};
