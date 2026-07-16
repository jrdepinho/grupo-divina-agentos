from app.runtime.agentos.runtime.engine_v2 import run

def test_chat():
    r = run(
        goal="Explique IA",
        mode="execute",
        approval="auto",
    )
    assert r["ok"] is True
    assert r["executed"] is True

def test_search():
    r = run(
        goal="buscar planner",
        mode="execute",
        approval="auto",
    )
    assert r["ok"] is True

def test_compile():
    r = run(
        goal="compile",
        mode="execute",
        approval="auto",
    )
    assert r["executed_steps"] >= 2
