"""
Bootstrap do AgentOS.

Responsável por inicializar o runtime exatamente uma vez.
"""

from __future__ import annotations

import threading

_initialized = False
_lock = threading.Lock()


def initialize() -> bool:
    """
    Inicializa o runtime apenas uma vez.

    Pode ser chamado livremente por:
      - FastAPI
      - CLI
      - engine_v2
      - testes
      - scripts
    """

    global _initialized

    if _initialized:
        return False

    with _lock:

        if _initialized:
            return False

        # registra todas as capabilities
        import app.runtime.agentos.capabilities

        _initialized = True

    return True


def initialized() -> bool:
    return _initialized
