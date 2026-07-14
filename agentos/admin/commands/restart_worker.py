import uuid

from agentos.admin.registry import register
from agentos.admin.shell import run_command


@register("restart_worker")
def restart_worker(payload):
    delay = int(payload.get("delay", 3))

    if delay < 1:
        delay = 1

    if delay > 60:
        delay = 60

    unit_name = f"agentos-worker-restart-{uuid.uuid4().hex[:12]}"

    result = run_command(
        [
            "systemd-run",
            "--quiet",
            f"--unit={unit_name}",
            f"--on-active={delay}s",
            "/bin/systemctl",
            "restart",
            "agentos-worker.service",
        ],
        timeout=30,
    )

    return {
        "success": result["success"],
        "scheduled": result["success"],
        "delay_seconds": delay,
        "transient_unit": unit_name,
        "command_result": result,
    }
