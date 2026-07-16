from app.runtime.agentos.bootstrap import initialize
from app.runtime.agentos.registry import list_capabilities

def test_registry_has_capabilities():
    initialize()
    caps = list_capabilities()

    assert "chat.complete" in caps
    assert "developer.search" in caps
    assert "developer.read" in caps
    assert "developer.compile" in caps
    assert "service.restart" in caps
