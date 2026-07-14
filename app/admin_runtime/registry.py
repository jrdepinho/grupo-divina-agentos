_HANDLERS = {}

def register(name):
    def decorator(fn):
        _HANDLERS[name] = fn
        return fn
    return decorator

def runtime_catalog():
    return sorted(_HANDLERS.keys())

def dispatch_runtime(req):
    operation = getattr(req, "operation", None)

    if operation is None and isinstance(req, dict):
        operation = req.get("operation")

    handler = _HANDLERS.get(operation)

    if handler is None:
        return None

    return handler(req)

def has_operation(name):
    return name in _HANDLERS

def get_handler(name):
    return _HANDLERS.get(name)
