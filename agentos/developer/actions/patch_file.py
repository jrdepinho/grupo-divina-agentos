from __future__ import annotations

from agentos.developer.security import safe_project_path, validate_content


def execute(path: str, search: str, replace: str) -> dict:
    target = safe_project_path(path)

    if not target.exists() or not target.is_file():
        raise FileNotFoundError(path)

    original = target.read_text(encoding="utf-8")

    occurrences = original.count(search)

    if occurrences != 1:
        raise ValueError(
            f"O trecho de busca deve ocorrer exatamente uma vez; encontrado: {occurrences}."
        )

    updated = original.replace(search, replace, 1)
    validate_content(updated)
    target.write_text(updated, encoding="utf-8")

    return {
        "path": path,
        "replacements": 1,
        "changed": original != updated,
    }
