from app.runtime.agentos.developer_engine import DeveloperEngine

_engine = DeveloperEngine()


def search(text):
    from app.runtime.agentos import developer_legacy
    return developer_legacy.search(text)


def read(path):
    from app.runtime.agentos import developer_legacy
    return developer_legacy.read(path)


def write(path, content):
    return _engine.write(path, content)


def compile():
    return _engine.compile()


def validate():
    return _engine.validate()


def rollback(path, backup):
    _engine.restore(path, backup)
    return {"ok": True}
