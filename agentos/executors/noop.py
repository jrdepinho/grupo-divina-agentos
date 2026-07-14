import time

from .base import BaseExecutor


class NoopExecutor(BaseExecutor):

    def execute(self, mission):

        time.sleep(3)

        return {
            "success": True,
            "message": "Missão executada com sucesso.",
            "data": {}
        }
