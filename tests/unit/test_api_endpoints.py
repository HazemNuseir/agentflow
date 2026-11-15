import pytest
import sys
import os

# Add apps/api to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../apps/api")))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Digital Mind Engineering" in data["company"]
    assert data["airgapped_verified"] is True

def test_inference_health_and_generate():
    health_res = client.get("/api/v1/inference/health")
    assert health_res.status_code == 200
    h_data = health_res.json()
    assert h_data["airgapped_compliant"] is True

    test_res = client.post("/api/v1/inference/test", json={
        "prompt": "Classify incoming inquiry: I need pricing for 1000 valves."
    })
    assert test_res.status_code == 200
    t_data = test_res.json()
    assert "text" in t_data
    assert "latency_ms" in t_data
    assert "tokens_generated" in t_data

def test_industry_templates():
    res = client.get("/api/v1/templates/")
    assert res.status_code == 200
    templates = res.json()
    assert len(templates) >= 6
    industries = {t["industry"] for t in templates}
    assert "Manufacturing" in industries
    assert "IT Services" in industries
    assert "Retail" in industries

def test_template_installation_and_workflow_execution():
    # Install RFQ Extraction template
    inst_res = client.post("/api/v1/templates/tpl_rfq_extraction/install")
    assert inst_res.status_code == 200
    wf_id = inst_res.json()["workflow_id"]

    # Trigger workflow execution
    exec_res = client.post("/api/v1/executions/trigger", json={
        "workflow_id": wf_id,
        "trigger_type": "manual_trigger",
        "payload": {
            "inquiry_text": "Request quotation for 5,000 Grade 6061-T6 valve units.",
            "contact_email": "tariq@client.jo"
        }
    })
    assert exec_res.status_code == 200
    e_data = exec_res.json()
    # It pauses for human approval
    assert e_data["status"] == "WAITING_APPROVAL"
    appr_id = e_data["approval_request_id"]
    assert appr_id is not None

    # Verify approval is listed
    appr_list_res = client.get("/api/v1/approvals/?status=PENDING")
    assert appr_list_res.status_code == 200
    approvals = appr_list_res.json()
    assert any(a["id"] == appr_id for a in approvals)

    # Approve the request
    dec_res = client.post(f"/api/v1/approvals/{appr_id}/decision", json={
        "decision": "APPROVED",
        "comments": "Commercial terms verified and authorized."
    })
    assert dec_res.status_code == 200
    assert dec_res.json()["status"] == "APPROVED"
    assert dec_res.json()["execution_status"] == "COMPLETED"

def test_working_demos():
    # Demo 1: Sales Automation
    d1 = client.post("/api/v1/demos/run/demo_sales_automation", json={"auto_approve": True})
    assert d1.status_code == 200
    assert d1.json()["status"] == "COMPLETED"
    assert len(d1.json()["trace"]) >= 6

    # Demo 2: Manufacturing RFQ
    d2 = client.post("/api/v1/demos/run/demo_manufacturing_rfq", json={"auto_approve": True})
    assert d2.status_code == 200
    assert d2.json()["status"] == "COMPLETED"
    assert len(d2.json()["trace"]) >= 5

    # Demo 3: Customer Support
    d3 = client.post("/api/v1/demos/run/demo_customer_support", json={})
    assert d3.status_code == 200
    assert d3.json()["status"] == "COMPLETED"
    assert len(d3.json()["trace"]) >= 4

    # Demo 4: Predictive Maintenance
    d4 = client.post("/api/v1/demos/run/demo_predictive_maintenance", json={})
    assert d4.status_code == 200
    assert d4.json()["status"] == "COMPLETED"
    assert len(d4.json()["trace"]) >= 4

def test_analytics_and_licensing():
    ana_res = client.get("/api/v1/analytics/summary")
    assert ana_res.status_code == 200
    ana = ana_res.json()
    assert "metrics" in ana
    assert ana["metrics"]["total_workflows"] >= 1

    lic_res = client.get("/api/v1/licensing/status")
    assert lic_res.status_code == 200
    lic = lic_res.json()
    assert lic["edition"] == "ENTERPRISE_PRIVATE"
    assert lic["is_airgapped_verified"] is True
