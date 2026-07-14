from copy import deepcopy

from fastapi import Request
from fastapi.responses import JSONResponse


GPT_ALLOWED_PATHS = {
    "/status",
    "/health",
    "/version",
    "/agentos/execute-goal",
    "/supabase/admin/sql",
    "/admin/file/read",
    "/admin/file/write",
    "/admin/file/patch",
    "/admin/file/list",
    "/admin/exec",
    "/admin/service/status",
    "/admin/service/restart",
    "/admin/service/logs",
    "/admin/deploy/validate",
    "/project-intelligence/capabilities",
    "/project-intelligence/dispatch",
    "/project-intelligence/context/build",
    "/project-intelligence/architecture/generate",
    "/project-intelligence/goal",
}


def is_gpt_allowed_path(path: str) -> bool:
    return (
        path in GPT_ALLOWED_PATHS
        or path.startswith("/project-intelligence/")
    )



def register_openapi_gpt(app):
    @app.get("/openapi-gpt.json", include_in_schema=False)
    def openapi_gpt(request: Request):
        schema = deepcopy(request.app.openapi())

        schema["paths"] = {
            path: item
            for path, item in schema.get("paths", {}).items()
            if is_gpt_allowed_path(path)
        }

        for path_item in schema.get("paths", {}).values():
            for operation in path_item.values():
                if isinstance(operation, dict):
                    operation.pop("parameters", None)
                    operation["security"] = [{"bearerAuth": []}]

        used_refs = set()
        for path_item in schema["paths"].values():
            for operation in path_item.values():
                if isinstance(operation, dict):
                    body = str(operation)
                    for name in schema.get("components", {}).get("schemas", {}).keys():
                        if f"#/components/schemas/{name}" in body:
                            used_refs.add(name)

        components = schema.setdefault("components", {})
        schemas = components.get("schemas", {})
        components["schemas"] = {
            name: value
            for name, value in schemas.items()
            if name in used_refs or name in {"HTTPValidationError", "ValidationError"}
        }

        return JSONResponse(schema)
