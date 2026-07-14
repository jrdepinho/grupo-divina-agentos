from agentos.admin.command_bus import CommandBus

class AdminExecutor:

    def execute(self, mission):

        payload = mission.get("payload", {}) or {}

        operation = payload.get("operation")

        if not operation:
            raise ValueError("Campo 'operation' não informado.")

        return CommandBus.execute(operation, payload)
