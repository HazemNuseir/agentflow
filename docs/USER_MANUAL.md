# DME AgentFlow — Complete User & Operations Manual

**Platform:** DME AgentFlow — Intelligent Business Automation Platform  
**Developer:** Digital Mind Engineering (DME), Amman, Jordan  
**Tagline:** *Your Business. Your Data. Your AI.*  
**Document Version:** 1.0  
**Target Audience:** Business Analysts, Department Managers, Operations Leads, Workflow Authors, Compliance Officers  

---

## Table of Contents
1. [Platform Introduction & Core Concepts](#1-platform-introduction--core-concepts)
2. [Getting Started & Authentication](#2-getting-started--authentication)
3. [User Roles & Permissions (RBAC)](#3-user-roles--permissions-rbac)
4. [Organization Onboarding Wizard](#4-organization-onboarding-wizard)
5. [Visual Workflow Studio (React Flow)](#5-visual-workflow-studio-react-flow)
6. [The 29 Standard Workflow Nodes Catalog](#6-the-29-standard-workflow-nodes-catalog)
7. [Workflow Versioning, Draft Testing & Publishing](#7-workflow-versioning-draft-testing--publishing)
8. [Human-in-the-Loop Approval Center](#8-human-in-the-loop-approval-center)
9. [AI Agent Studio & Google Gemma 4 Configuration](#9-ai-agent-studio--google-gemma-4-configuration)
10. [Local Private Knowledge Hub (Document Intelligence)](#10-local-private-knowledge-hub-document-intelligence)
11. [Embedded Enterprise CRM & Account Management](#11-embedded-enterprise-crm--account-management)
12. [8 Industry Automation Packs & Blueprints](#12-8-industry-automation-packs--blueprints)
13. [Operations Monitor & Execution Analytics](#13-operations-monitor--execution-analytics)
14. [Arabic & Bilingual Localization Support](#14-arabic--bilingual-localization-support)
15. [Commercial Licensing & Edition Gating](#15-commercial-licensing--edition-gating)

---

## 1. Platform Introduction & Core Concepts

**DME AgentFlow** is an enterprise-grade sovereign business automation platform. Developed in Amman, Jordan by Digital Mind Engineering (DME), AgentFlow solves a primary challenge faced by modern enterprises: **how to deploy intelligent AI automation without leaking proprietary corporate data to external cloud providers.**

### Key Principles
- **100% Data Sovereignty:** Models run on local customer compute using Google Gemma 4 architecture via `llama.cpp` GGUF.
- **Visual Drag-and-Drop:** Business teams design complex workflows with zero programming using visual blocks.
- **Deterministic Business Execution:** Workflow branches and business decisions are enforced by rigorous server-side engines, not unpredictable generative hallucinations.
- **Human Governance:** Sensitive commercial commitments (pricing discounts, supplier dispatches, contract submittals) require signed human approvals.

---

## 2. Getting Started & Authentication

### Registering Your Account and Workspace
1. Direct your browser to `http://localhost:3000` (or your company's internal AgentFlow domain).
2. Click **Register** on the top navigation bar.
3. Fill in your full name, official corporate email, secure password, and organization name.
4. Upon submission, your organization workspace is created, and your account is automatically designated as `ORGANIZATION_ADMIN`.

### Logging In
1. Navigate to `/login`.
2. Enter your email address and password.
3. Upon authentication, a secure JWT Bearer token is issued and stored in browser session storage.
4. You will be redirected to the **Operations Mission Control Dashboard** (`/dashboard`).

---

## 3. User Roles & Permissions (RBAC)

AgentFlow enforces strict role hierarchy boundaries across all endpoints:

```text
PLATFORM_OWNER (100)
    │
    ▼
ORGANIZATION_OWNER (80)
    │
    ▼
ORGANIZATION_ADMIN (60)
    │
    ▼
WORKFLOW_EDITOR (40)
    │
    ▼
APPROVER (30)
    │
    ▼
VIEWER (10)
```

### Permissions Matrix

| Capability | VIEWER | APPROVER | WORKFLOW_EDITOR | ORG_ADMIN | ORG_OWNER |
|---|:---:|:---:|:---:|:---:|:---:|
| View Dashboard & Reports | ✅ | ✅ | ✅ | ✅ | ✅ |
| Inspect Completed Executions | ✅ | ✅ | ✅ | ✅ | ✅ |
| Decide Approval Requests (Approve/Reject) | ❌ | ✅ | ✅ | ✅ | ✅ |
| Create & Edit Workflow Drafts | ❌ | ❌ | ✅ | ✅ | ✅ |
| Publish Workflow Versions | ❌ | ❌ | ✅ | ✅ | ✅ |
| Configure AI Agents & Prompts | ❌ | ❌ | ✅ | ✅ | ✅ |
| Manage CRM Contacts & Leads | ❌ | ❌ | ✅ | ✅ | ✅ |
| Configure Integration Connectors | ❌ | ❌ | ❌ | ✅ | ✅ |
| Manage Team Members & Roles | ❌ | ❌ | ❌ | ✅ | ✅ |
| Billing & License Management | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 4. Organization Onboarding Wizard

First-time administrators are guided through a 5-step configuration wizard:
1. **Organization Profile:** Set company name, industry sector, country (default: Jordan), and timezone (`Asia/Amman`).
2. **Language Preferences:** Choose interface language (English or Arabic with automatic RTL layout).
3. **Infrastructure Declaration:** Declare host environment (e.g., *Local CPU 8-Core, 32GB RAM* or *NVIDIA RTX 4090 GPU*).
4. **Business Objectives:** Select primary automation targets (e.g., *Automate Supplier RFQ*, *Proactive Logistics Tracking*, *Customer Inquiry Triage*).
5. **Blueprint Recommendation:** AgentFlow automatically recommends relevant pre-built industry templates tailored to your operational profile.

---

## 5. Visual Workflow Studio (React Flow)

The Visual Workflow Studio provides a drag-and-drop canvas for authoring end-to-end automation pipelines.

### Working with the Canvas
- **Add Nodes:** Drag any of the 29 node types from the left-hand palette onto the grid canvas.
- **Connect Nodes:** Click and drag an output handle (circle on right) of a node to the input handle (circle on left) of the successor node.
- **Conditional Branching:** For decision nodes, connect the `approved` handle or set a `condition` filter on the connecting edge.
- **Configure Parameters:** Click any node on the canvas to open its right-side configuration drawer.
- **Canvas Controls:** Pan by dragging the canvas background; zoom with mouse wheel or bottom-left zoom controls.

---

## 6. The 29 Standard Workflow Nodes Catalog

Nodes are categorized into six functional groups:

### 1. Trigger Nodes (Green Accent)
- **`manual_trigger`:** Invoked on-demand by users from the UI or testing console.
- **`form_submission`:** Triggered when an internal or external web form is submitted.
- **`webhook`:** Ingests incoming HTTP POST payloads from third-party enterprise systems.
- **`schedule`:** Cron-based recurring trigger (e.g., daily at 08:00 AM).
- **`email_received`:** Fires upon receipt of an inbound email message via local IMAP/POP3.

### 2. Logic Nodes (Amber Accent)
- **`condition`:** Evaluates binary boolean expressions (e.g., `order_total > 5000`).
- **`branch`:** Splits execution flow into multiple distinct downstream paths.
- **`switch`:** Multi-case value router (e.g., route by department or region).
- **`data_transform`:** Maps, filters, or transforms JSON payload properties.
- **`validation`:** Enforces schema rules; halts with error if constraints fail.
- **`delay`:** Suspends execution for a designated duration (seconds/minutes).
- **`loop`:** Iterates over arrays with bounded safety limits.
- **`parallel`:** Executes concurrent sibling tasks with fan-in join completion.

### 3. AI Intelligence Nodes (Purple Accent)
- **`classify_text`:** Classifies unstructured text into defined business categories using local Gemma 4.
- **`extract_structured`:** Extracts type-safe JSON entities matching a target schema.
- **`summarize_text`:** Generates concise executive summaries of lengthy documents.
- **`generate_response`:** Generates context-aware business correspondence.
- **`retrieve_knowledge`:** Performs semantic vector search against the local Knowledge Hub.
- **`invoke_agent`:** Dispatches context to a specialized, pre-configured AI Agent persona.
- **`interpret_document`:** Analyzes technical specifications, RFQs, invoices, or delivery receipts.

### 4. Action Nodes (Blue Accent)
- **`create_crm_contact`:** Records a new contact record in the internal database.
- **`create_crm_lead`:** Captures an evaluated commercial lead.
- **`update_crm_opportunity`:** Updates deal stage, value, or probability.
- **`create_crm_task`:** Assigns an operational task to a team member.
- **`send_email`:** Dispatches outbound email notification via configured SMTP.
- **`http_request`:** Executes outbound REST calls (governed by air-gap policy).
- **`generate_document`:** Compiles PDF quotes, receipts, or work orders.
- **`create_notification`:** Emits in-app alerts to users or roles.
- **`save_business_record`:** Persists generic JSON records to enterprise storage.

### 5. Human Control Nodes (Orange Accent)
- **`request_approval`:** Suspends execution until authorized human review.
- **`approve_reject`:** Binary pass/fail gateway for managers.
- **`request_clarification`:** Solicits additional information from the requester.
- **`manual_intervention`:** Requests operator data correction before proceeding.

### 6. Completion Nodes (Emerald / Red Accent)
- **`success`:** Marks workflow execution as successfully finished with final output payload.
- **`failure`:** Terminates execution, records diagnostic error message, and alerts admins.

---

## 7. Workflow Versioning, Draft Testing & Publishing

To guarantee zero production disruptions, AgentFlow strictly isolates drafts from live triggers.

```text
[ Draft Editor (v1) ] ──────────────► [ Test Draft Run (/test-draft) ]
        │                                        ▲
        │ Click "Publish"                        │ (Inspect outputs & debug)
        ▼                                        │
[ Immutable Snapshot v2 ] ◄──────────────────────┘
        │
        ▼
[ Production Trigger (/trigger) ] ──► (Guaranteed Stable Execution)
```

### Step-by-Step Publishing Lifecycle
1. **Design in Draft:** Add and configure nodes on the canvas. Auto-saves as working draft.
2. **Draft Testing:** Click **Test Draft** on the top toolbar. Enter sample payload data. AgentFlow executes the draft without publishing, allowing you to review per-node outputs and timing.
3. **Graph Validation:** When clicking **Publish**, the server performs rigorous validation:
   - Validates node IDs and schema configurations.
   - Rejects missing connections or disconnected edges.
   - Enforces valid node categories.
4. **Immutable Snapshot:** Once validated, the server freezes an exact JSON snapshot of the nodes and edges, increments the workflow version number, and marks it `is_published: true`.
5. **Safe Editing:** If you edit the workflow again, your changes remain in a working draft. All active production triggers continue running the published snapshot until you explicitly publish again.

---

## 8. Human-in-the-Loop Approval Center

When a workflow hits an approval node (e.g. Director Sign-off on an RFQ quote), it securely pauses.

### Reviewing Pending Approvals
1. Open the **Approvals** tab from the main navigation.
2. The table displays all pending requests with:
   - Workflow name & Execution ID
   - Context payload (e.g., Client Name, Extracted Alloy Specs, Quoted Price)
   - Assigned Role required to decide (e.g., `APPROVER` or `ORGANIZATION_ADMIN`)
   - Submission timestamp

### Decision Actions
- **Approve:** Clicking **Approve** commits the approval record and deterministically resumes the execution from the paused node along the `approved` conditional edge.
- **Reject:** Clicking **Reject** terminates the execution, records the decision comments, and transitions the execution state to `CANCELLED`.
- **Request Clarification:** Keeps the execution paused, notes the clarification request in the audit trail, and notifies the initiator.

### Anti-Race Condition Safety
AgentFlow's approval engine enforces atomic database locking. If two managers attempt to decide the same request simultaneously, the first request succeeds and the second is safely rejected with `HTTP 409 Conflict`, preventing duplicate actions or conflicting state transitions.

---

## 9. AI Agent Studio & Google Gemma 4 Configuration

The **AI Agent Studio** allows teams to create specialized autonomous agents without writing code.

### Creating an Agent
1. Navigate to **AI Agents** and click **New Agent**.
2. Configure parameters:
   - **Name:** e.g., *RFQ Technical Classifier*
   - **Role / Persona:** e.g., *Senior Industrial Procurement Engineer*
   - **System Instructions:** Specific guidelines on how to analyze text and make recommendations.
   - **Model Selection:** Choose active model (e.g., *Google Gemma 4 E4B Instruct*).
   - **Temperature:** Set between `0.1` (deterministic/analytical) and `0.7` (creative).
   - **Structured Schema (JSON):** Declare expected output fields (e.g., `{"lead_score": "number", "recommended_product": "string"}`).
   - **Attached Knowledge Bases:** Select documents the agent is authorized to reference.
   - **Approval Required:** Flag whether the agent's recommended action requires human confirmation.

### Testing an Agent
Use the **Agent Sandbox** panel on the right side of the screen. Enter a sample customer prompt (e.g., *"Need 5,000 units of 6061-T6 aluminum valves by next month"*) and verify the structured output returned by the local model.

---

## 10. Local Private Knowledge Hub (Document Intelligence)

The **Knowledge Hub** provides air-gapped Retrieval-Augmented Generation (RAG) without external API dependencies.

### Ingesting Documents
1. Navigate to **Knowledge Hub**.
2. Click **Upload Document** (Supported: `.pdf`, `.docx`, `.txt`, `.md`, `.csv`).
3. Enter a descriptive title (e.g., *2026 Material Pricing Matrix*).
4. The engine automatically:
   - Extracts plain text locally.
   - Chunks content with configurable overlap (default 400 words, 50-word overlap).
   - Computes local 64-dimensional vector embeddings.
   - Stores chunk vectors scoped strictly to your organization tenant.

### Semantic Search Verification
Use the search bar at the top of the Knowledge Hub to enter questions in natural language. The engine computes cosine similarity across your organization's indexed chunks and displays matching excerpts ranked by confidence score.

---

## 11. Embedded Enterprise CRM & Account Management

AgentFlow includes an internal relational CRM designed for automated workflow interaction.

### CRM Modules
- **Contacts:** Tracks customers, procurement leads, and partner representatives.
- **Leads:** Captures inbound inquiries evaluated by AI agents, including score (0–100), estimated deal value, and source channel.
- **Opportunities:** Pipeline tracker managing deal stages (`DISCOVERY`, `QUOTATION`, `PROPOSAL`, `NEGOTIATION`, `WON`, `LOST`).
- **Tasks:** Operational to-do items assigned automatically by workflows to team members.

Workflows can read from and write to CRM tables via native `create_crm_lead`, `create_crm_contact`, and `update_crm_opportunity` nodes.

---

## 12. 8 Industry Automation Packs & Blueprints

AgentFlow ships with eight pre-configured, tested industry automation blueprints:

| Industry | Blueprint Title | Workflow Flow | Business Outcome |
|---|---|---|---|
| **Manufacturing** | RFQ Extraction & Quotation Dispatch | RFQ Upload → AI Specs Extraction → Knowledge Pricing Match → Director Approval → Quotation PDF | 80% faster supplier turnaround with zero human calculation errors |
| **Logistics** | Real-Time Delivery Exception Triage | Shipment Webhook → Delay Threshold Check → Impact Classification → Driver Notification → Customer CRM Task | Proactive SLA delay mitigation and automated customer notifications |
| **Retail & E-Commerce** | VIP Returns & Escalation Management | Customer Form → VIP Order Value Check → AI Return Validation → Auto-Generate RMA → Email Confirmation | Instant return processing for VIP shoppers while filtering fraudulent claims |
| **Professional Services** | Client Intake & Scope Assessment | Client Intake Form → AI Project Summary → Practice Group Routing → Partner Signoff → Engagement Doc | Standardized onboarding with structured scope estimates |
| **IT Services** | Incident Triage & Tier-1 Escalation | Server Alert Webhook → Severity AI Classification → Priority Branching → Auto-Create Task → Slack/Email Alert | Sub-minute incident routing and automated SLA tier escalation |
| **Hospitality** | VIP Guest Preference Routing | Reservation Webhook → Preference Extraction → VIP Condition Check → Concierge Task Creation | Personalized guest amenity preparation prior to arrival |
| **Education** | Student Inquiry & Advising Triage | Prospect Web Form → Academic Interest Classification → Program Advisor Routing → Personalized Prospectus Email | 24/7 immediate student response and admissions lead tracking |
| **Engineering** | Submittal Compliance Verification | Engineering Drawing Upload → Knowledge Specification Search → AI Compliance Analysis → Lead Engineer Signoff | Rapid compliance audits against municipal building codes |

To deploy a blueprint, navigate to **Industry Templates**, select your industry, and click **Install Template**. It immediately creates a ready-to-test workflow draft in your workspace.

---

## 13. Operations Monitor & Execution Analytics

### Real-Time Monitoring
The **Executions Monitor** (`/executions`) lists every active, paused, completed, and failed execution. Clicking any row opens a visual audit trace showing:
- Execution timeline (start, duration in milliseconds, completion time).
- Per-node execution cards with input data, duration, and output payloads.
- Paused nodes waiting for approval, highlighted in amber.
- Failed nodes with full exception stack traces for rapid debugging.

### Truthful Analytics & ROI Modeling
The **Analytics Dashboard** (`/analytics`) displays:
- **Recorded Database Metrics:** Verified counts of total workflows, completed runs, failure rate, pending approval queue depth, and local AI inference latency.
- **Configurable ROI Model:** Projected operational savings clearly marked with an `is_estimate: true` banner. Administrators can configure:
  - *Assumed Operator Hourly Rate* (Default: $35.00/hour)
  - *Estimated Time Saved per Automated Execution* (Default: 25 minutes)
  - The system projects cumulative labor hours saved and dollar ROI based solely on actual completed runs.

---

## 14. Arabic & Bilingual Localization Support

DME AgentFlow features native bilingual support designed for the Middle East & North Africa (MENA) region.

### Switching Interface Language
1. Click the language toggle button located on the top navigation bar.
2. Select **العربية (Arabic)** or **English**.
3. When Arabic is active:
   - The HTML document direction updates to `dir="rtl"`.
   - The navigation sidebar smoothly relocates to the right side of the screen.
   - Text alignment, tables, and badge components adapt to natural Arabic reading flow.

---

## 15. Commercial Licensing & Edition Gating

AgentFlow operates under three commercial editions enforced via cryptographic license keys:

| Feature / Limit | STARTER | PROFESSIONAL | ENTERPRISE PRIVATE |
|---|:---:|:---:|:---:|
| Maximum Users | 5 | 25 | Unlimited |
| Active Workflows | 10 | 50 | Unlimited |
| Monthly Executions | 1,000 | 10,000 | Unlimited |
| Local Gemma 4 Inference | CPU Only | CPU + GPU | High-Performance GPU Cluster |
| Human Approvals | ❌ | ✅ | ✅ |
| Private Knowledge Hub | Basic | Full RAG | Multi-Document RAG |
| Air-Gap Cryptographic Enforcement | ❌ | ❌ | ✅ |
| Custom Connectors & SSRF Defense | ❌ | Basic | Advanced |

To apply a license, navigate to **Settings > Billing & Licensing**, paste your cryptographic Ed25519 license key, and click **Validate License**. The server validates the signature and expiration offline without connecting to any external license server.
