from app.runtime.agentos import developer

def search(text):
    return developer.search(text)

def read(path):
    return developer.read(path)

def write(path, content):
    return developer.write(path, content)

def patch(path, old, new):
    return developer.patch(path, old, new)

def compile():
    return developer.compile()

def validate():
    return developer.validate()

def rollback():
    return developer.rollback()
