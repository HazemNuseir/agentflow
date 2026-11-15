import os
import sys

# Ensure backend root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "api")))

def test_inference_engine():
    print("--- 1. Testing Inference Backend ---")
    from inference.backend import inference_backend
    health = inference_backend.get_health()
    print("Inference Backend Health:", health)
    assert health["status"] in ["healthy", "available"]
    
    prompt = "Classify: Need RFQ pricing for 5000 industrial valves"
    res = inference_backend.generate(prompt)
    print("Inference Prompt Result:", res.get("text", "")[:80])
    assert "Quotation" in res.get("text", "") or len(res.get("text", "")) > 0
    print("=> Inference Backend PASS\n")

def test_templates_catalog():
    print("--- 2. Testing Templates Catalog ---")
    from routers.templates import TEMPLATES_CATALOG
    print(f"Total Industry Templates Registered: {len(TEMPLATES_CATALOG)}")
    industries = set(t["industry"] for t in TEMPLATES_CATALOG)
    print("Industries Covered:", ", ".join(industries))
    assert len(TEMPLATES_CATALOG) >= 8
    print("=> Templates Catalog PASS\n")

def test_knowledge_engine():
    print("--- 3. Testing Local Knowledge Engine ---")
    from knowledge.engine import knowledge_engine
    text = "Digital Mind Engineering (DME) provides private AI workflow automation for Jordan and regional enterprises."
    chunks = knowledge_engine.chunk_text(text, chunk_size=100, overlap=20)
    print(f"Text Chunking Result: {len(chunks)} chunks produced")
    assert len(chunks) > 0
    
    emb = knowledge_engine.compute_local_embedding("enterprise workflow automation")
    print(f"Local Embedding Dimension: {len(emb)}")
    assert len(emb) == 64
    print("=> Knowledge Engine PASS\n")

def test_models_registry():
    print("--- 4. Testing AI Models Registry ---")
    from database.models import AIModelRegistry
    from inference.backend import inference_backend
    info = inference_backend.get_model_info()
    print("Default Backend Model Info:", info)
    assert "gemma" in info.get("name", "").lower()
    print("=> AI Models Registry PASS\n")

def test_database_tables():
    print("--- 5. Testing Database Tables & Models ---")
    from database.session import engine
    from database.models import Base
    import sqlite3
    
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "api", "agentflow.db"))
    print("Database file path:", db_path)
    assert os.path.exists(db_path), "Database file does not exist!"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    print(f"Total SQLite Tables ({len(tables)}):", ", ".join(tables))
    expected_tables = ["organizations", "users", "workflows", "workflow_executions", "approval_requests", "crm_contacts"]
    for t in expected_tables:
        assert t in tables, f"Missing expected table {t}"
    print("=> Database Verification PASS\n")

def main():
    print("==================================================")
    print("   DME AGENTFLOW - BACKEND SYNCHRONOUS VERIFICATION")
    print("==================================================\n")
    test_inference_engine()
    test_templates_catalog()
    test_knowledge_engine()
    test_models_registry()
    test_database_tables()
    print("==================================================")
    print("   ALL VERIFICATION CHECKS PASSED (5/5) SUCCESS")
    print("==================================================")

if __name__ == "__main__":
    main()
