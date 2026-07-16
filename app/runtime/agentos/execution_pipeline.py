from app.runtime.agentos.developer_engine import DeveloperEngine


class ExecutionPipeline:

    def __init__(self):

        self.dev = DeveloperEngine()

    def execute(
        self,
        path: str,
        content: str,
    ):

        backup = self.dev.backup(path)

        try:

            self.dev.write(
                path,
                content,
            )

            compile_result = self.dev.compile()

            if not compile_result["ok"]:

                self.dev.restore(
                    path,
                    backup,
                )

                return {
                    "ok": False,
                    "stage": "compile",
                    "rollback": True,
                    "result": compile_result,
                }

            validate_result = self.dev.validate()

            if not validate_result["ok"]:

                self.dev.restore(
                    path,
                    backup,
                )

                return {
                    "ok": False,
                    "stage": "validate",
                    "rollback": True,
                    "result": validate_result,
                }

            return {
                "ok": True,
                "backup": str(backup),
                "compile": compile_result,
                "validate": validate_result,
            }

        except Exception as exc:

            self.dev.restore(
                path,
                backup,
            )

            return {
                "ok": False,
                "rollback": True,
                "exception": str(exc),
            }
