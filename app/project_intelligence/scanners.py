from __future__ import annotations

import json
import re
import subprocess
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_PROJECT_ROOTS = (
    Path("/opt/agente-divina-v2"),
    Path("/opt/agente-divina"),
)

IGNORED_DIRS = {
    ".git",
    "backup",
    "backups",
    ".idea",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "htmlcov",
    "node_modules",
    "test-deps",
    "vendor",
    "venv",
}

TEXT_EXTENSIONS = {
    ".css",
    ".env",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".mjs",
    ".py",
    ".rb",
    ".sql",
    ".ts",
    ".tsx",
    ".txt",
    ".vue",
    ".yaml",
    ".yml",
}

CODE_EXTENSIONS = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".py",
    ".php",
    ".rb",
    ".java",
    ".go",
    ".cs",
    ".vue",
}

ROUTE_REGEXES = (
    re.compile(r"@(?:app|router|api)\.(get|post|put|patch|delete|options|head)\([\"']([^\"']+)", re.I),
    re.compile(r"\b(?:app|router)\.(get|post|put|patch|delete|options|head)\([\"']([^\"']+)", re.I),
    re.compile(r"\b(?:Get|Post|Put|Patch|Delete)\([\"']([^\"']*)", re.I),
    re.compile(r"\bpath\([\"']([^\"']+)", re.I),
)

MEMORY_MARKERS = ("TODO", "FIXME", "NOTE", "ADR")


@dataclass(frozen=True)
class ScanContext:
    root: Path
    files: list[Path]
    warnings: list[str]
    errors: list[str]


def resolve_project_root(path: str | None = None) -> Path:
    if path:
        return Path(path).expanduser().resolve()

    for candidate in DEFAULT_PROJECT_ROOTS:
        if candidate.exists():
            return candidate.resolve()

    return Path.cwd().resolve()


def _is_ignored(path: Path) -> bool:
    for part in path.parts:
        lower = part.lower()

        if (
            lower in IGNORED_DIRS
            or lower.startswith("backup")
            or lower.startswith("backups")
            or lower.startswith("app.backup")
            or lower.endswith(".backup")
            or ".backup_" in lower
        ):
            return True

    return False


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _module_name(path: str) -> str:
    parts = Path(path).parts
    if not parts:
        return "."
    if parts[0] in {"app", "src"} and len(parts) > 1:
        return parts[1]
    return parts[0]


def _read_text(path: Path, limit: int = 250_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception:
        return ""


def _json_file(path: Path) -> dict[str, Any]:
    try:
        return json.loads(_read_text(path))
    except Exception:
        return {}


def _iter_files(root: Path, max_files: int = 5_000) -> ScanContext:
    warnings: list[str] = []
    errors: list[str] = []
    if not root.exists():
        return ScanContext(root=root, files=[], warnings=[], errors=[f"Projeto não encontrado: {root}"])
    if not root.is_dir():
        return ScanContext(root=root, files=[], warnings=[], errors=[f"Caminho não é diretório: {root}"])

    files: list[Path] = []
    try:
        for item in root.rglob("*"):
            if len(files) >= max_files:
                warnings.append(f"Limite de {max_files} arquivos atingido; resultado parcial.")
                break
            if _is_ignored(item):
                continue
            if not item.is_file():
                continue

            name = item.name.lower()

            if (
                name.endswith(".bak")
                or ".bak_" in name
                or name.endswith("~")
                or name.endswith(".orig")
                or name.endswith(".tmp")
            ):
                continue

            files.append(item)
    except Exception as exc:
        errors.append(str(exc))

    return ScanContext(root=root, files=files, warnings=warnings, errors=errors)


def _paths_by_kind(ctx: ScanContext, keywords: Iterable[str]) -> list[str]:
    lowered = tuple(keyword.lower() for keyword in keywords)
    return sorted(
        _rel(path, ctx.root)
        for path in ctx.files
        if any(keyword in _rel(path, ctx.root).lower() for keyword in lowered)
    )


def _extract_routes(path: Path, root: Path) -> list[dict[str, Any]]:
    rel = _rel(path, root)
    routes: list[dict[str, Any]] = []

    if "/api/" in f"/{rel}" and path.name.startswith("route."):
        routes.append({"framework": "Next", "method": "ANY", "path": "/" + rel, "file": rel})

    text = _read_text(path)
    if not text:
        return routes

    for regex in ROUTE_REGEXES:
        for match in regex.finditer(text):
            groups = match.groups()
            if len(groups) == 2:
                method, route_path = groups
            else:
                method, route_path = "ANY", groups[0]
            routes.append(
                {
                    "method": str(method).upper(),
                    "path": route_path or "/",
                    "file": rel,
                    "line": text[: match.start()].count("\n") + 1,
                }
            )

    return routes


def _folder_tree(ctx: ScanContext, max_depth: int = 4) -> list[dict[str, Any]]:
    directories: dict[str, dict[str, Any]] = {}
    for path in ctx.files:
        rel_parts = Path(_rel(path, ctx.root)).parts
        for depth in range(1, min(len(rel_parts), max_depth) + 1):
            current = "/".join(rel_parts[:depth])
            if "." in Path(current).name and depth == len(rel_parts):
                continue
            entry = directories.setdefault(current, {"path": current, "files": 0})
            if depth == len(rel_parts) - 1:
                entry["files"] += 1
    return sorted(directories.values(), key=lambda item: item["path"])


def _dependency_inventory(ctx: ScanContext) -> dict[str, Any]:
    dependencies: dict[str, Any] = {"files": [], "packages": {}}

    for path in ctx.files:
        name = path.name
        rel = _rel(path, ctx.root)
        if name in {"package.json", "requirements.txt", "pyproject.toml", "composer.json", "Pipfile"}:
            dependencies["files"].append(rel)

        if name == "package.json":
            package = _json_file(path)
            packages = {}
            for key in ("dependencies", "devDependencies"):
                packages.update(package.get(key) or {})
            dependencies["packages"].update(packages)

        if name == "requirements.txt":
            for line in _read_text(path).splitlines():
                text = line.strip()
                if text and not text.startswith("#"):
                    dependencies["packages"][re.split(r"[<>=~!]", text)[0].strip()] = text

        if name == "composer.json":
            package = _json_file(path)
            packages = {}
            for key in ("require", "require-dev"):
                packages.update(package.get(key) or {})
            dependencies["packages"].update(packages)

    return dependencies


def scan_project(path: str | None = None, max_files: int = 5_000) -> dict[str, Any]:
    started = time.perf_counter()
    root = resolve_project_root(path)
    ctx = _iter_files(root, max_files=max_files)
    dependencies = _dependency_inventory(ctx)
    routes = [route for file_path in ctx.files for route in _extract_routes(file_path, ctx.root)]
    markdown = sorted(_rel(file_path, ctx.root) for file_path in ctx.files if file_path.suffix.lower() == ".md")

    markers = scan_memory(str(root), max_files=max_files)["markers"]
    code_files = [file_path for file_path in ctx.files if file_path.suffix.lower() in CODE_EXTENSIONS]
    modules = Counter(_module_name(_rel(file_path, ctx.root)) for file_path in code_files)

    result = {
        "domain": "project_intelligence",
        "capability": "project.scan",
        "root": str(root),
        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        "files_analyzed": len(ctx.files),
        "files": sorted(_rel(file_path, ctx.root) for file_path in ctx.files),
        "structure": _folder_tree(ctx),
        "modules": [{"name": name, "files": count} for name, count in modules.most_common()],
        "controllers": _paths_by_kind(ctx, ("controller", "controllers", "routes", "views.py", "api.py")),
        "services": _paths_by_kind(ctx, ("service", "services")),
        "repositories": _paths_by_kind(ctx, ("repository", "repositories", "repo")),
        "models": _paths_by_kind(ctx, ("model", "models", "schema", "schemas")),
        "migrations": _paths_by_kind(ctx, ("migration", "migrations", "alembic", "versions")),
        "documentation": markdown,
        "markdown": markdown,
        "todo": [item for item in markers if item["marker"] == "TODO"],
        "fixme": [item for item in markers if item["marker"] == "FIXME"],
        "dependencies": dependencies,
        "apis": routes,
        "routes": routes,
        "warnings": ctx.warnings,
        "errors": ctx.errors,
    }
    result["modules_found"] = len(result["modules"])
    return result


def scan_frontend(path: str | None = None, max_files: int = 5_000) -> dict[str, Any]:
    started = time.perf_counter()
    root = resolve_project_root(path)
    ctx = _iter_files(root, max_files=max_files)
    deps = _dependency_inventory(ctx)["packages"]
    rels = [_rel(file_path, ctx.root) for file_path in ctx.files]

    frameworks = []
    checks = {
        "React": lambda: "react" in deps or any(file.endswith((".jsx", ".tsx")) for file in rels),
        "Next": lambda: "next" in deps or any(file.startswith("app/") for file in rels),
        "Vue": lambda: "vue" in deps or any(file.endswith(".vue") for file in rels),
        "Angular": lambda: "@angular/core" in deps or any("angular.json" == Path(file).name for file in rels),
    }
    for name, detector in checks.items():
        if detector():
            frameworks.append(name)

    pages = sorted(file for file in rels if re.search(r"(^|/)(pages|app)/.*(page|route)?\.(jsx|tsx|js|ts|vue)$", file))
    components = sorted(file for file in rels if "/components/" in f"/{file}" or re.search(r"/[A-Z][A-Za-z0-9]+\.(jsx|tsx|vue)$", f"/{file}"))
    hooks = sorted(file for file in rels if re.search(r"(^|/)use[A-Z].*\.(js|jsx|ts|tsx)$", Path(file).name) or "/hooks/" in f"/{file}")
    services = sorted(file for file in rels if "/services/" in f"/{file}" or "/api/" in f"/{file}")
    stores = sorted(file for file in rels if any(token in f"/{file}".lower() for token in ("/store", "/stores", "zustand", "redux", "pinia", "vuex")))
    layouts = sorted(file for file in rels if re.search(r"(^|/)layout\.(js|jsx|ts|tsx|vue)$", file, re.I))

    return {
        "domain": "project_intelligence",
        "capability": "frontend.scan",
        "root": str(root),
        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        "files_analyzed": len(ctx.files),
        "frameworks": frameworks,
        "pages": pages,
        "components": components,
        "hooks": hooks,
        "routes": [route for file_path in ctx.files for route in _extract_routes(file_path, ctx.root) if route.get("framework") == "Next"],
        "services": services,
        "stores": stores,
        "layouts": layouts,
        "warnings": ctx.warnings,
        "errors": ctx.errors,
    }


def scan_backend(path: str | None = None, max_files: int = 5_000) -> dict[str, Any]:
    started = time.perf_counter()
    root = resolve_project_root(path)
    ctx = _iter_files(root, max_files=max_files)
    deps = _dependency_inventory(ctx)["packages"]
    rels = [_rel(file_path, ctx.root) for file_path in ctx.files]
    text_names = set(deps) | {Path(file).name.lower() for file in rels}

    framework_checks = {
        "FastAPI": "fastapi" in text_names or any("FastAPI(" in _read_text(file_path, 20_000) for file_path in ctx.files if file_path.suffix == ".py"),
        "Django": "django" in text_names or any("manage.py" == Path(file).name for file in rels),
        "Flask": "flask" in text_names or any("Flask(" in _read_text(file_path, 20_000) for file_path in ctx.files if file_path.suffix == ".py"),
        "Express": "express" in text_names,
        "Nest": "@nestjs/core" in text_names or any(".module.ts" in file for file in rels),
        "Laravel": "laravel/framework" in text_names or any("artisan" == Path(file).name for file in rels),
    }
    frameworks = [name for name, detected in framework_checks.items() if detected]
    endpoints = [route for file_path in ctx.files for route in _extract_routes(file_path, ctx.root)]

    return {
        "domain": "project_intelligence",
        "capability": "backend.scan",
        "root": str(root),
        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        "files_analyzed": len(ctx.files),
        "frameworks": frameworks,
        "controllers": _paths_by_kind(ctx, ("controller", "controllers", "routes", "views.py", "api.py")),
        "endpoints": endpoints,
        "services": _paths_by_kind(ctx, ("service", "services")),
        "repositories": _paths_by_kind(ctx, ("repository", "repositories", "repo")),
        "middlewares": _paths_by_kind(ctx, ("middleware", "middlewares")),
        "validations": _paths_by_kind(ctx, ("validator", "validators", "schema", "schemas", "request")),
        "business_rules": _paths_by_kind(ctx, ("rule", "rules", "policy", "policies", "usecase", "use_case")),
        "warnings": ctx.warnings,
        "errors": ctx.errors,
    }


def scan_database(path: str | None = None, max_files: int = 5_000) -> dict[str, Any]:
    started = time.perf_counter()
    root = resolve_project_root(path)
    ctx = _iter_files(root, max_files=max_files)
    deps = _dependency_inventory(ctx)["packages"]
    rels = [_rel(file_path, ctx.root) for file_path in ctx.files]

    orm = []
    orm_checks = {
        "SQLAlchemy": "sqlalchemy" in deps or any("sqlalchemy" in _read_text(file_path, 20_000).lower() for file_path in ctx.files if file_path.suffix == ".py"),
        "Django ORM": "django" in deps and any(Path(file).name == "models.py" for file in rels),
        "Prisma": "prisma" in deps or any(file.endswith("schema.prisma") for file in rels),
        "TypeORM": "typeorm" in deps,
        "Sequelize": "sequelize" in deps,
        "Knex": "knex" in deps,
        "Eloquent": "laravel/framework" in deps,
        "Supabase": "supabase" in deps or "@supabase/supabase-js" in deps,
    }
    for name, detected in orm_checks.items():
        if detected:
            orm.append(name)

    migrations = _paths_by_kind(ctx, ("migration", "migrations", "alembic", "versions"))
    tables: set[str] = set()
    relationships: list[dict[str, str]] = []
    indexes: list[dict[str, str]] = []
    foreign_keys: list[dict[str, str]] = []

    for file_path in ctx.files:
        if file_path.suffix.lower() not in {".sql", ".py", ".ts", ".js", ".prisma", ".php"}:
            continue
        rel = _rel(file_path, ctx.root)
        text = _read_text(file_path)
        for match in re.finditer(r"\bcreate\s+table\s+(?:if\s+not\s+exists\s+)?[\"`]?([\w.]+)", text, re.I):
            tables.add(match.group(1))
        for match in re.finditer(r"\bclass\s+(\w+)\([^)]*Model[^)]*\)", text):
            tables.add(match.group(1))
        for match in re.finditer(r"\bmodel\s+(\w+)\s+\{", text):
            tables.add(match.group(1))
        for match in re.finditer(r"\bforeign\s+key\s*\(([^)]+)\)\s+references\s+([\w.]+)", text, re.I):
            foreign_keys.append({"file": rel, "column": match.group(1).strip(), "references": match.group(2).strip()})
        for match in re.finditer(r"\bcreate\s+(?:unique\s+)?index\s+([\w_]+)", text, re.I):
            indexes.append({"file": rel, "index": match.group(1)})
        for match in re.finditer(r"\b(ForeignKey|relationship)\(([^)]*)\)", text):
            relationships.append({"file": rel, "type": match.group(1), "target": match.group(2)[:120]})

    return {
        "domain": "project_intelligence",
        "capability": "database.scan",
        "root": str(root),
        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        "files_analyzed": len(ctx.files),
        "orm": orm,
        "migrations": migrations,
        "tables": sorted(tables),
        "relationships": relationships,
        "indexes": indexes,
        "foreign_keys": foreign_keys,
        "warnings": ctx.warnings,
        "errors": ctx.errors,
    }


def scan_memory(path: str | None = None, max_files: int = 5_000) -> dict[str, Any]:
    started = time.perf_counter()
    root = resolve_project_root(path)
    ctx = _iter_files(root, max_files=max_files)
    markers: list[dict[str, Any]] = []
    markdown: list[str] = []
    docs: list[str] = []
    adr: list[str] = []

    marker_pattern = re.compile(r"\b(TODO|FIXME|NOTE|ADR)\b[:\-\s]*(.*)", re.I)
    for file_path in ctx.files:
        rel = _rel(file_path, ctx.root)
        suffix = file_path.suffix.lower()
        if suffix == ".md":
            markdown.append(rel)
        if any(part.lower() in {"doc", "docs", "documentation"} for part in Path(rel).parts):
            docs.append(rel)
        if "adr" in rel.lower():
            adr.append(rel)
        if suffix not in TEXT_EXTENSIONS:
            continue
        for line_no, line in enumerate(_read_text(file_path).splitlines(), start=1):
            match = marker_pattern.search(line)
            if match:
                marker = match.group(1).upper()
                markers.append(
                    {
                        "marker": marker,
                        "module": _module_name(rel),
                        "file": rel,
                        "line": line_no,
                        "text": match.group(2).strip()[:300],
                    }
                )

    by_module: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in markers:
        by_module[item["module"]].append(item)

    return {
        "domain": "project_intelligence",
        "capability": "memory.search",
        "root": str(root),
        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        "files_analyzed": len(ctx.files),
        "markers": markers,
        "by_module": dict(sorted(by_module.items())),
        "markdown": sorted(markdown),
        "docs": sorted(set(docs)),
        "adr": sorted(set(adr)),
        "warnings": ctx.warnings,
        "errors": ctx.errors,
    }


def _git(root: Path, args: list[str], timeout: int = 30) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return result.returncode == 0, (result.stdout or result.stderr).strip()
    except Exception as exc:
        return False, str(exc)


def inspect_git(path: str | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    root = resolve_project_root(path)
    ok, top_level = _git(root, ["rev-parse", "--show-toplevel"])
    warnings: list[str] = []
    errors: list[str] = []
    if ok and top_level:
        root = Path(top_level).resolve()
    else:
        warnings.append(top_level or f"Diretório não é um repositório git: {root}")

    current_ok, current_branch = _git(root, ["branch", "--show-current"])
    branches_ok, branches_text = _git(root, ["branch", "--format=%(refname:short)"])
    log_ok, log_text = _git(root, ["log", "--name-only", "--pretty=format:COMMIT%x09%h%x09%an%x09%ad%x09%s", "--date=short", "-n", "50"])
    authors_ok, authors_text = _git(root, ["shortlog", "-sne", "--all"])

    file_counter: Counter[str] = Counter()
    last_changes: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    if log_ok:
        for line in log_text.splitlines():
            if line.startswith("COMMIT\t"):
                if current:
                    last_changes.append(current)
                _, sha, author, date, subject = (line.split("\t", 4) + [""])[:5]
                current = {"sha": sha, "author": author, "date": date, "subject": subject, "files": []}
                continue
            file_name = line.strip()
            if file_name and current is not None:
                current["files"].append(file_name)
                file_counter[file_name] += 1
        if current:
            last_changes.append(current)
    else:
        warnings.append(log_text)

    authors = []
    if authors_ok:
        for line in authors_text.splitlines():
            match = re.match(r"\s*(\d+)\s+(.+)", line)
            if match:
                authors.append({"commits": int(match.group(1)), "author": match.group(2)})

    hotspots = [{"file": file, "changes": count} for file, count in file_counter.most_common(25)]

    return {
        "domain": "project_intelligence",
        "capability": "git.inspect",
        "root": str(root),
        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        "current_branch": current_branch if current_ok else None,
        "branches": sorted(branch for branch in branches_text.splitlines() if branch.strip()) if branches_ok else [],
        "last_changes": last_changes[:20],
        "most_modified": hotspots,
        "authors": authors,
        "hotspots": hotspots,
        "warnings": warnings,
        "errors": errors,
    }


def generate_architecture(path: str | None = None, module: str | None = None, max_files: int = 5_000) -> dict[str, Any]:
    started = time.perf_counter()
    project = scan_project(path, max_files=max_files)
    frontend = scan_frontend(path, max_files=max_files)
    backend = scan_backend(path, max_files=max_files)
    database = scan_database(path, max_files=max_files)
    memory = scan_memory(path, max_files=max_files)
    git = inspect_git(path)

    modules = project.get("modules", [])
    selected_module = (module or "").strip().lower()
    incomplete_modules = []
    for item in modules:
        name = item["name"]
        module_markers = memory.get("by_module", {}).get(name, [])
        if module_markers or item.get("files", 0) <= 2:
            incomplete_modules.append(
                {
                    "name": name,
                    "signals": {
                        "files": item.get("files", 0),
                        "memory_markers": len(module_markers),
                    },
                }
            )

    backlog = [
        "Validar cobertura de testes dos módulos com mais rotas/endpoints.",
        "Consolidar documentação técnica dos fluxos principais.",
        "Priorizar TODO/FIXME por risco operacional.",
        "Mapear contratos de API e payloads críticos.",
    ]
    if database.get("tables") and not database.get("foreign_keys"):
        backlog.append("Revisar relacionamentos explícitos do banco e documentar foreign keys.")
    if backend.get("endpoints") and not backend.get("validations"):
        backlog.append("Criar catálogo de validações por endpoint.")
    if selected_module:
        backlog.insert(0, f"Detalhar dependências e gaps do módulo {module}.")

    markdown = _architecture_markdown(project, frontend, backend, database, memory, git, backlog, module)
    return {
        "domain": "project_intelligence",
        "capability": "architecture.generate",
        "root": project.get("root"),
        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        "module_filter": module,
        "json": {
            "modules_tree": project.get("structure", []),
            "dependencies": project.get("dependencies", {}),
            "functional_flow": {
                "frontend_routes": frontend.get("pages", []),
                "backend_endpoints": backend.get("endpoints", []),
                "database_tables": database.get("tables", []),
            },
            "incomplete_modules": incomplete_modules,
            "suggested_backlog": backlog,
        },
        "markdown": markdown,
        "scans": {
            "project": project,
            "frontend": frontend,
            "backend": backend,
            "database": database,
            "memory": memory,
            "git": git,
        },
        "warnings": project.get("warnings", []) + frontend.get("warnings", []) + backend.get("warnings", []) + database.get("warnings", []) + memory.get("warnings", []) + git.get("warnings", []),
        "errors": project.get("errors", []) + frontend.get("errors", []) + backend.get("errors", []) + database.get("errors", []) + memory.get("errors", []) + git.get("errors", []),
    }


def _architecture_markdown(
    project: dict[str, Any],
    frontend: dict[str, Any],
    backend: dict[str, Any],
    database: dict[str, Any],
    memory: dict[str, Any],
    git: dict[str, Any],
    backlog: list[str],
    module: str | None,
) -> str:
    title = f"Arquitetura encontrada - {module}" if module else "Arquitetura encontrada"
    lines = [
        f"# {title}",
        "",
        f"- Projeto: `{project.get('root')}`",
        f"- Arquivos analisados: {project.get('files_analyzed', 0)}",
        f"- Módulos encontrados: {project.get('modules_found', 0)}",
        "",
        "## Frontend",
        f"- Frameworks: {', '.join(frontend.get('frameworks') or ['não detectado'])}",
        f"- Páginas: {len(frontend.get('pages', []))}",
        f"- Componentes: {len(frontend.get('components', []))}",
        "",
        "## Backend",
        f"- Frameworks: {', '.join(backend.get('frameworks') or ['não detectado'])}",
        f"- Endpoints: {len(backend.get('endpoints', []))}",
        f"- Services: {len(backend.get('services', []))}",
        "",
        "## Banco",
        f"- ORM: {', '.join(database.get('orm') or ['não detectado'])}",
        f"- Tabelas/modelos: {len(database.get('tables', []))}",
        f"- Migrations: {len(database.get('migrations', []))}",
        "",
        "## Memória e documentação",
        f"- TODO/FIXME/NOTE/ADR: {len(memory.get('markers', []))}",
        f"- Markdown: {len(memory.get('markdown', []))}",
        "",
        "## Git",
        f"- Branch atual: {git.get('current_branch') or 'não detectada'}",
        f"- Hotspots: {len(git.get('hotspots', []))}",
        "",
        "## Roadmap sugerido",
    ]
    lines.extend(f"- {item}" for item in backlog)
    return "\n".join(lines)
