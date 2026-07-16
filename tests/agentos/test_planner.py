from app.runtime.agentos.planner.planner import Planner

planner = Planner()

def test_chat_plan():
    plan = planner.build("Explique IA")
    assert plan[0]["action"] == "chat.complete"

def test_search_plan():
    plan = planner.build("buscar planner")
    assert plan[0]["action"] == "developer.search"

def test_compile_plan():
    plan = planner.build("compile")
    assert len(plan) == 2
