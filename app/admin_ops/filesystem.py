from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, Callable

from fastapi import HTTPException


def handle_filesystem_op(req: Any, safe_path: Callable[[str], Path]) -> dict[str, Any] | None:
    op = req.operation

    if op in {"list", "list_dir", "file_list", "project_list"}:
        p = safe_path(req.path or ".")
        items = []
        iterator = p.rglob("*") if req.recursive else p.iterdir()
        for item in list(iterator)[: req.limit or 200]:
            items.append({"path": str(item), "type": "dir" if item.is_dir() else "file"})
        return {"ok": True, "items": items}

    if op in {"read", "read_file", "file_read", "project_read_file"}:
        p = safe_path(req.path)
        return {"ok": True, "path": str(p), "content": p.read_text(errors="replace")}

    if op in {"write", "write_file", "file_write", "project_create_file", "project_write_file"}:
        p = safe_path(req.path)
        p.parent.mkdir(parents=True, exist_ok=True)
        backup = None
        if p.exists():
            backup = p.with_suffix(p.suffix + f".bak-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
            backup.write_text(p.read_text(errors="replace"))
        p.write_text(req.content or "")
        return {"ok": True, "path": str(p), "backup": str(backup) if backup else None}

    if op in {"patch", "patch_file", "file_patch", "project_patch_file"}:
        p = safe_path(req.path)
        text = p.read_text(errors="replace")
        if req.find not in text:
            raise HTTPException(404, "trecho find não encontrado")
        backup = p.with_suffix(p.suffix + f".bak-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
        backup.write_text(text)
        p.write_text(text.replace(req.find, req.replace or "", 1))
        return {"ok": True, "path": str(p), "backup": str(backup)}

    if op in {"delete_file", "project_delete_file"}:
        p = safe_path(req.path)
        backup = None
        if p.exists():
            backup = p.with_suffix(p.suffix + f".bak-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
            backup.write_bytes(p.read_bytes())
            p.unlink()
        return {"ok": True, "path": str(p), "backup": str(backup) if backup else None}

    if op == "search_text":
        root = safe_path(req.path or ".")
        found = []
        for f in root.rglob("*"):
            if f.is_file() and len(found) < (req.limit or 200):
                try:
                    txt = f.read_text(errors="ignore")
                    if req.find and req.find in txt:
                        found.append(str(f))
                except Exception:
                    pass
        return {"ok": True, "found": found}

    return None
