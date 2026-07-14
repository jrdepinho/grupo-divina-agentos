import subprocess

from agentos.admin.context import PROJECT_ROOT


def run_command(command, timeout=120):
    if not isinstance(command, list) or not command:
        raise ValueError("O comando deve ser uma lista não vazia.")

    try:
        process = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        return {
            "success": process.returncode == 0,
            "command": command,
            "returncode": process.returncode,
            "stdout": process.stdout.strip(),
            "stderr": process.stderr.strip(),
        }

    except subprocess.TimeoutExpired as exc:
        return {
            "success": False,
            "command": command,
            "error": "timeout",
            "timeout": timeout,
            "stdout": (exc.stdout or "").strip()
            if isinstance(exc.stdout, str)
            else "",
            "stderr": (exc.stderr or "").strip()
            if isinstance(exc.stderr, str)
            else "",
        }
