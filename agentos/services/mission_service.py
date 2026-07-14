import traceback

from agentos.executors.dispatcher import dispatch
from agentos.repositories.mission_repository import MissionRepository


class MissionService:

    def __init__(self):
        self.repository = MissionRepository()

    def execute(self, mission):

        try:

            result = dispatch(mission)

            self.repository.save_result(
                mission["id"],
                result,
            )

            self.repository.finish(
                mission["id"],
            )

            return result

        except Exception as e:

            payload = {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
            }

            self.repository.fail(
                mission["id"],
                payload,
            )

            return payload
