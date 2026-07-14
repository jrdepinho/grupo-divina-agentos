COMMANDS = {}

def register(name):
    def decorator(func):
        COMMANDS[name] = func
        return func
    return decorator
