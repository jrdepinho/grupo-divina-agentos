from dataclasses import dataclass
from typing import Callable

@dataclass
class Capability:
    name: str
    description: str
    handler: Callable

_registry = {}

def register(capability: Capability):
    _registry[capability.name] = capability

def get(name):
    return _registry.get(name)

def list_capabilities():
    return list(_registry.keys())
