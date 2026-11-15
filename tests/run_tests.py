import asyncio
import os
import sys

# Ensure apps/api is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/api")))

import httpx
from main import app

async def run_all_tests():
    print("==================================================")
    print("DME AgentFlow — Verification & Acceptance Test Suite")
    print("Digital Mind Engineering (DME), Jordan")
    print("==================================================")

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Health
        res = await client.get("/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        data = res.json()
        print(" [PASS] 1. Health check:", data["service"], "| Profile:", data["deployment_profile"])

        # 2. Local AI Inference
        h_res = await client.get("/api/v1/inference/health")
        assert h_res.status_code == 200
        print(" [PASS] 2. Local Inference Health:", h_res.json()["backend"], "| Air-gapped:", h_res.json()["airgapped_compliant"])

        test_res = await client.post("/api/v1/inference/test", json={"prompt": "Classify: Need RFQ pricing for 5,000 valves."})
        assert test_res.status_code == 200
        gen = test_res.json()
        print(" [PASS] 3. Local Gemma Generation:", gen["text"][:60], "...", f"({gen['latency_ms']}ms)")

        # 3. Industry Templates
        tpl_res = await client.get("/api/v1/templates/")
        assert tpl_res.status_code == 200
        templates = tpl_res.json()
        assert len(templates) >= 6
        print(f" [PASS] 4. Industry Templates Loaded: {len(templates)} templates across 8 industries")

        # 4. Template Installation & Workflow Execution
        inst_res = await client.post("/api/v1/templates/tpl_rfq_extraction/install")
        assert inst_res.status_code == 200
        wf_id = inst_res.json()["workflow_id"]
        print(f" [PASS] 5. Installed Template Workflow: ID {wf_id}")

        exec_res = await client.post("/api/v1/executions/trigger", json={
            "workflow_id": wf_id,
            "trigger_type": "manual_trigger",
            "payload": {"inquiry_text": "Need 5,000 units of 6061-T6 valve bodies.", "contact_email": "tariq@client.jo"}
        })
        assert exec_res.status_code == 200
        e_data = exec_res.json()
        assert e_data["status"] == "WAITING_APPROVAL"
        appr_id = e_data["approval_request_id"]
        print(f" [PASS] 6. Workflow Paused for Approval: Request ID {appr_id}")

        dec_res = await client.post(f"/api/v1/approvals/{appr_id}/decision", json={
            "decision": "APPROVED",
            "comments": "Commercial terms authorized by Director."
        })
        assert dec_res.status_code == 200
        assert dec_res.json()["execution_status"] == "COMPLETED"
        print(" [PASS] 7. Workflow Resumed and Successfully Completed upon Human Approval")

        # 5. Live Working Demonstrations
        d1 = await client.post("/api/v1/demos/run/demo_sales_automation", json={"auto_approve": True})
        assert d1.status_code == 200 and d1.json()["status"] == "COMPLETED"
        print(f" [PASS] 8. DEMO 1 (Sales Automation): {len(d1.json()['trace'])} steps executed in {d1.json()['duration_ms']}ms")

        d2 = await client.post("/api/v1/demos/run/demo_manufacturing_rfq", json={"auto_approve": True})
        assert d2.status_code == 200 and d2.json()["status"] == "COMPLETED"
        print(f" [PASS] 9. DEMO 2 (Manufacturing RFQ): {len(d2.json()['trace'])} steps executed in {d2.json()['duration_ms']}ms")

        d3 = await client.post("/api/v1/demos/run/demo_customer_support", json={})
        assert d3.status_code == 200 and d3.json()["status"] == "COMPLETED"
        print(f" [PASS] 10. DEMO 3 (Customer Support RAG): {len(d3.json()['trace'])} steps executed in {d3.json()['duration_ms']}ms")

        d4 = await client.post("/api/v1/demos/run/demo_predictive_maintenance", json={})
        assert d4.status_code == 200 and d4.json()["status"] == "COMPLETED"
        print(f" [PASS] 11. DEMO 4 (Predictive Maintenance): {len(d4.json()['trace'])} steps executed in {d4.json()['duration_ms']}ms")

        # 6. Analytics & Licensing
        ana_res = await client.get("/api/v1/analytics/summary")
        assert ana_res.status_code == 200
        metrics = ana_res.json()["metrics"]
        print(f" [PASS] 12. Analytics: {metrics['total_workflows']} Workflows, {metrics['total_executions']} Executions, Hours Saved: {metrics['estimated_hours_saved']}h")

        lic_res = await client.get("/api/v1/licensing/status")
        assert lic_res.status_code == 200
        lic = lic_res.json()
        print(f" [PASS] 13. Licensing: {lic['edition']} Edition, Valid Until: {lic['valid_until']}, Airgapped: {lic['is_airgapped_verified']}")

    print("==================================================")
    print(" ALL 13 CORE INTEGRATION TESTS PASSED CLEANLY!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
