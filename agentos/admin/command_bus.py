from agentos.admin.registry import COMMANDS

import agentos.admin.commands.cleanup_project
import agentos.admin.commands.compile_project
import agentos.admin.commands.restart_worker
import agentos.admin.commands.validate_project


class CommandBus:

    @staticmethod
    def execute(operation, payload=None):
        if operation not in COMMANDS:
            raise ValueError(f"Operação '{operation}' não registrada.")

        return COMMANDS[operation](payload or {})
