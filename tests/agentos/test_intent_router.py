from app.runtime.agentos.router.intent_router import IntentRouter

router = IntentRouter()

def test_chat():
    assert router.detect("Explique IA").name == "chat"

def test_search():
    assert router.detect("buscar planner").name == "search"

def test_read():
    assert router.detect("ler app/runtime/agentos/registry.py").name == "read"

def test_compile():
    assert router.detect("compile").name == "compile"

def test_capabilities():
    assert router.detect("listar capabilities").name == "capabilities"

def test_developer():
    assert router.detect("corrigir bug").name == "developer"
