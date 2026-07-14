from __future__ import annotations

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


PRODUCTION_SERVER = {
    "url": "https://agente.divinahomepy.com",
    "description": "Agente Divina Production",
}

ADMIN_SECURE_OPERATIONS = {
    ("post", "/admin/file/read"),
    ("post", "/admin/file/write"),
    ("post", "/admin/file/patch"),
    ("post", "/admin/file/list"),
    ("post", "/admin/exec"),
    ("post", "/admin/service/status"),
    ("post", "/admin/service/restart"),
    ("post", "/admin/service/logs"),
    ("post", "/admin/deploy/validate"),
    ("get", "/project-intelligence/capabilities"),
    ("post", "/project-intelligence/dispatch"),
    ("post", "/project-intelligence/project/scan"),
    ("post", "/project-intelligence/frontend/scan"),
    ("post", "/project-intelligence/backend/scan"),
    ("post", "/project-intelligence/database/scan"),
    ("post", "/project-intelligence/memory/search"),
    ("post", "/project-intelligence/git/inspect"),
    ("post", "/project-intelligence/context/build"),
    ("post", "/project-intelligence/architecture/generate"),
    ("post", "/project-intelligence/goal"),
}


def configure_openapi(app: FastAPI) -> None:
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            servers=[PRODUCTION_SERVER],
        )

        components = openapi_schema.setdefault("components", {})
        security_schemes = components.setdefault("securitySchemes", {})
        security_schemes["bearerAuth"] = {"type": "http", "scheme": "bearer"}

        for path, path_item in openapi_schema.get("paths", {}).items():
            for method, operation in path_item.items():
                if not isinstance(operation, dict):
                    continue
                if (method.lower(), path) in ADMIN_SECURE_OPERATIONS:
                    operation["security"] = [{"bearerAuth": []}]

        openapi_schema["servers"] = [PRODUCTION_SERVER]
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi_schema = None
    app.openapi = custom_openapi
