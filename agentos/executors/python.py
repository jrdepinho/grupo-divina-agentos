import importlib

from .base import BaseExecutor


class PythonExecutor(BaseExecutor):

    def execute(self, mission):

        payload = mission.get("payload") or {}

        module_name = payload["module"]
        function_name = payload["function"]

        args = payload.get("args", {})

        module = importlib.import_module(
            f"agentos.functions.{module_name}"
        )

        function = getattr(module, function_name)

        return function(**args)
