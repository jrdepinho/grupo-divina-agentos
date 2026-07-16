from .context import context
from fastapi.security import HTTPAuthorizationCredentials
from app.runtime.agentos.patching.patch_generator import PatchGenerator

from app.auth import get_admin_token

from .registry import Capability, register
from . import developer_v2 as developer
from app.runtime.agentos.llm import generate_patch
from .runtime.engine_v2 import run as engine_run
from app.runtime.agentos.chat import chat_complete

from app.runtime.agentos.execution_pipeline import ExecutionPipeline


from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)



SERVICE_ALIASES = {
    "agentos": "agentos-worker.service",
    "agentos-worker": "agentos-worker.service",
    "agente-divina": "agente-divina-api.service",
    "agente-divina-api": "agente-divina-api.service",
    "agente-divina-v2": "agente-divina-v2.service",
    "agente-mestre": "agente-mestre.service",
    "agente-mestre-worker": "agente-mestre-worker.service",
}


def credentials():
    token = get_admin_token()

    if not token:
        raise RuntimeError(
            "AGENTE_ADMIN_TOKEN não encontrado no ambiente "
            "nem nos arquivos de configuração."
        )

    return HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )


def service_name(name):
    value = str(name or "").strip()

    if not value:
        raise ValueError("Serviço não informado.")

    normalized = value.removesuffix(".service")

    return SERVICE_ALIASES.get(normalized, value)



def admin(path, body=None):
    headers={
        "Authorization":f"Bearer {credentials().credentials}"
    }

    response=client.post(
        path,
        json=body or {},
        headers=headers,
    )

    if response.status_code>=400:
        raise RuntimeError(response.text)

    return response.json()


def goal_echo(goal):
    return {
        "ok": True,
        "action": "goal.echo",
        "result": {
            "message": "Goal recebido",
            "goal": goal,
        },
    }


def admin_capabilities():
    from app.runtime.agentos.registry import list_capabilities, get

    items = []
    for name in sorted(list_capabilities()):
        cap = get(name)
        items.append({
            "name": cap.name,
            "description": cap.description,
        })

    return {
        "ok": True,
        "count": len(items),
        "capabilities": items,
    }


def service_status(service="agente-divina-api.service"):
    return admin(
        "/admin/service/status",
        {
            "service":service_name(service)
        },
    )


def service_logs(service="agente-divina-api.service", limit=100):
    return admin(
        "/admin/service/logs",
        {
            "service":service_name(service),
            "lines":limit,
        },
    )


def service_restart(service="agente-divina-api.service"):
    return admin(
        "/admin/service/restart",
        {
            "service":service_name(service),
        },
    )


def deploy_validate():
    return admin(
        "/admin/deploy/validate",
        {
            "cwd":"/opt/agente-divina-v2",
            "commands":[
                "python3 -m py_compile app/runtime/agentos/capabilities.py"
            ]
        },
    )


def nginx_test():
    return admin("nginx_test")


def nginx_reload():
    return admin("nginx_reload")


register(Capability("goal.echo","Echo",goal_echo))
register(Capability("admin.capabilities","Capabilities",admin_capabilities))
register(Capability("service.status","Status",service_status))
register(Capability("service.logs","Logs",service_logs))
register(Capability("service.restart","Restart",service_restart))
register(Capability("deploy.validate","Deploy Validate",deploy_validate))
# register(Capability("nginx.test","Nginx Test",nginx_test))
# register(Capability("nginx.reload","Nginx Reload",nginx_reload))


def developer_search(text):
    return developer.search(text)


def developer_read(path):
    return developer.read(path)


def developer_write(path, content):
    return developer.write(path, content)



def developer_patch(
    path,
    goal=None,
    content=None,
    old=None,
    new=None,
):

    if new is not None:
        content = new

    if content is None:

        source = developer.read(path)

        generator = PatchGenerator()

        content = generator.generate(
            goal=goal,
            source=source,
            path=path,
        )

    pipe = ExecutionPipeline()

    return pipe.execute(
        path=path,
        content=content,
    )


def developer_compile():
    return developer.compile()


def developer_validate():
    return developer.validate()


def developer_rollback():
    return developer.rollback()



register(Capability("developer.search","Developer Search",developer_search))
register(Capability("developer.read","Developer Read",developer_read))
register(Capability("developer.write","Developer Write",developer_write))
register(Capability("developer.patch","Developer Patch",developer_patch))
register(Capability("developer.compile","Developer Compile",developer_compile))
register(Capability("developer.validate","Developer Validate",developer_validate))
register(Capability("developer.rollback","Developer Rollback",developer_rollback))

register(
    Capability(
        "chat.complete",
        "Chat Complete",
        chat_complete,
    )
)




def engine_execute(goal):
    return engine_run(goal)



register(
    Capability(
        "engine.execute",
        "Engine Execute",
        engine_execute,
    )
)



def context_read():
    return {
        "ok": True,
        "context": dict(context),
    }


register(
    Capability(
        "context.read",
        "Context Read",
        context_read,
    )
)


def developer_generate_patch(goal, path, content):
    return generate_patch(
        goal=goal,
        path=path,
        content=content
    )

register(
    Capability(
        "developer.generate_patch",
        "Developer Generate Patch",
        developer_generate_patch,
    )
)