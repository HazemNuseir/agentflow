"""Exercise actual V2 approval handlers concurrently against a disposable database."""
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest
from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))


def resolve(coro):
    try:
        coro.send(None)
    except StopIteration as result:
        return result.value
    finally:
        coro.close()
    raise RuntimeError("Unexpected suspended coroutine")


def test_one_decision_and_one_continuation(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///" + (tmp_path / "test.db").as_posix())
    for key in ("DATA_DIR", "MODELS_DIR", "UPLOADS_DIR", "DOCUMENTS_DIR"):
        monkeypatch.setenv(key, str(tmp_path / key))

    from database.session import Base, engine, SyncSessionLocal
    from database.models import Workflow, WorkflowExecution, CRMContact
    from routers.approvals import ApprovalDecisionRequest, decide_approval
    from engine.executor import execution_engine

    Base.metadata.create_all(engine)
    graph = {
        "nodes": [
            {"id": "start", "type": "manual_trigger", "category": "TRIGGER"},
            {"id": "review", "type": "request_approval", "category": "HUMAN"},
            {"id": "contact", "type": "create_crm_contact", "category": "ACTION"},
        ],
        "edges": [{"source": "start", "target": "review"}, {"source": "review", "target": "contact"}],
    }
    with SyncSessionLocal() as db:
        flow = Workflow(org_id="org-a", name="Approval test", is_published=True, published_snapshot_json=graph)
        db.add(flow)
        db.flush()
        run = WorkflowExecution(org_id="org-a", workflow_id=flow.id, graph_snapshot_json=graph)
        db.add(run)
        db.commit()
    started = resolve(execution_engine.execute_workflow(run.id))
    approval = started["approval_request_id"]
    assert started["status"] == "WAITING_APPROVAL"

    def decide(org, role, email):
        try:
            result = resolve(decide_approval(
                approval, ApprovalDecisionRequest(decision="APPROVED"),
                {"org_id": org, "role": role, "email": email},
            ))
            return 200, result["execution_status"]
        except HTTPException as error:
            return error.status_code, None

    assert decide("org-a", "VIEWER", "viewer@example.invalid")[0] == 403
    assert decide("org-b", "APPROVER", "outsider@example.invalid")[0] == 404
    with SyncSessionLocal() as db:
        current = db.get(Workflow, flow.id)
        current.published_snapshot_json = {"nodes": [], "edges": []}
        db.commit()

    start = Barrier(2)
    def race(email):
        start.wait(timeout=5)
        return decide("org-a", "APPROVER", email)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(race, ["a@example.invalid", "b@example.invalid"]))
    assert sorted(results) == [(200, "COMPLETED"), (409, None)]
    with SyncSessionLocal() as db:
        assert db.query(CRMContact).filter_by(org_id="org-a").count() == 1
        assert db.get(WorkflowExecution, run.id).status == "COMPLETED"
    engine.dispose()
