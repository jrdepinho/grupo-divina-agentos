from agentos.admin.registry import register
from agentos.admin.shell import run_command


@register("compile_project")
def compile_project(payload):
    timeout = int(payload.get("timeout", 180))

    return run_command(
        [
            "python3",
            "-m",
            "compileall",
            "-q",
            "agentos",
        ],
        timeout=timeout,
    )
