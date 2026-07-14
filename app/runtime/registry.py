CAPABILITIES = {}

def register(name, fn):
    CAPABILITIES[name] = fn

def get(name):
    return CAPABILITIES.get(name)

def list_capabilities():
    return sorted(CAPABILITIES.keys())
