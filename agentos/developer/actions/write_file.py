from __future__ import annotations

from agentos.developer.security import safe_project_path, validate_content


def execute(path: str, content: str, overwrite: bool = False) -> dict:
    target = safe_project_path(path)
    validate_content(content)

    if target.exists() and not overwrite:
        raise FileExistsError(
            f"O arquivo {path} já existe. Use overwrite=true explicitamente."
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

    return {
        "path": path,
        "bytes": len(content.encode("utf-8")),
        "created": True,
    }
