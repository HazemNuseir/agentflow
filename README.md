# DME AgentFlow — Intelligent Business Automation Platform

> **"Your Business. Your Data. Your AI."**  
> Developed by **Digital Mind Engineering (DME)**, Jordan.

---

## 🌟 Executive Summary

**DME AgentFlow** is an enterprise-grade AI workflow automation platform tailored for businesses requiring **100% sovereign, private, on-premise execution**. Powered by local **Google Gemma 4** models running through `llama.cpp` / `llama-cpp-python`, AgentFlow allows organizations to automate multi-step business logic across CRM, ERP, and internal systems without ever transmitting confidential corporate data to third-party cloud APIs.

---

## 🚀 Key Platform Capabilities

1. **Local Sovereign AI Inference**: Direct execution of Google Gemma 4 (E4B Instruct, 12B, 26B, 31B) via GGUF quantization. Zero third-party telemetry or remote data transmission.
2. **Visual Flow Studio**: Drag-and-drop workflow authoring with 29 enterprise-grade node types across Triggers, Logic, AI, Actions, Human Approvals, and Completion nodes.
3. **Multi-Tenant Isolation**: Hard boundary organization workspaces with strict tenant-scoped query execution and RBAC (`PLATFORM_OWNER`, `ORGANIZATION_OWNER`, `ORGANIZATION_ADMIN`, `WORKFLOW_EDITOR`, `APPROVER`, `VIEWER`).
4. **Local Knowledge Hub**: Air-gapped document intelligence (PDF, Word, TXT, CSV) utilizing local chunking, deterministic word-hash vectorization, and cosine similarity ranking.
5. **Human-in-the-Loop Governance**: Pauses live workflow executions for designated manager approvals, rejections, or clarification requests, resuming deterministically upon decision.
6. **Built-in CRM & Operations**: Native management for Contacts, Leads, Opportunities, and Task orchestration.
7. **8 Industry-Specific Workflow Packs**:
   - Manufacturing (Automated RFQ Processing & Dispatch)
   - Logistics & Supply Chain (Delivery Exception & Rerouting)
   - Retail & E-Commerce (VIP Escalation & Returns Automation)
   - Professional Services (Client Intake & Scope Estimation)
   - IT Services (Incident Triage & Tier-1 Escalation)
   - Hospitality & Tourism (VIP Guest Preference Routing)
   - Education & Training (Student Inquiry & Enrollment Triaging)
   - Engineering & Construction (Submittal Review & Compliance Tracking)

---

## 🏗 Monorepo Architecture

```text
agentflow/
├── apps/
│   ├── api/             # FastAPI Backend, SQLAlchemy 2, SQLite/PostgreSQL
│   ├── web/             # Next.js 15, React 19, Tailwind CSS, React Flow
│   ├── worker/          # Background task execution & schedule polling
│   └── inference/       # Local Gemma GGUF runtime worker
├── packages/
│   ├── shared-types/    # Monorepo TypeScript domain definitions
│   ├── workflow-schemas/# Node catalog & schema validators
│   └── ui/              # Reusable enterprise UI primitives
├── infrastructure/
│   ├── docker/          # Multi-stage Dockerfiles (CPU & CUDA GPU)
│   ├── deployment/      # Production systemd & compose profiles
│   └── offline/         # Air-gapped tarball bundling manifests
├── models/              # Local GGUF Gemma model storage
├── docs/                # Comprehensive engineering specifications
└── tests/               # Unit, integration, security & verification suites
```

---

## ⚡ Quick Start (Local Development)

### 1. Prerequisites
- **Python**: 3.12+
- **Node.js**: v20+ or v24+
- **Docker** (Optional for containerized setup)

### 2. Backend Setup
```bash
cd agentflow/apps/api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup
```bash
cd agentflow/apps/web
npm install
npm run dev
```

Visit `http://localhost:3000` to access the DME AgentFlow Dashboard.

---

## 🛡 Security & Sovereign Air-Gap Compliance

DME AgentFlow defaults to `DEPLOYMENT_PROFILE=FULLY_PRIVATE_AIRGAPPED`:
- **Outbound Network Calls**: Hard disabled at engine level (`ALLOW_EXTERNAL_CALLS=false`).
- **Telemetry**: Hard disabled (`TELEMETRY_ENABLED=false`).
- **Licensing**: Cryptographic Ed25519 offline token validation.

---

## 🏢 About Digital Mind Engineering (DME)

**Digital Mind Engineering** is an applied artificial intelligence firm headquartered in **Amman, Jordan**. DME delivers robust software engineering, private language models, and high-security enterprise workflow automation across MENA and international markets.

**Contact**: info@digitalmind.jo | Amman, Jordan
