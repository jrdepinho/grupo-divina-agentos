# Agente Divina API V2

Esta versão preserva o `app/api.py` existente e adiciona o entrypoint
`app.main:app` com um módulo administrativo protegido por `AGENTE_ADMIN_TOKEN`.

## Execução

```bash
cd /opt/agente-divina-v2
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Validação

```bash
python3 -m py_compile app/main.py
uvicorn app.main:app --host 127.0.0.1 --port 8050
curl http://127.0.0.1:8050/health
curl http://127.0.0.1:8050/openapi.json
```

## Endpoints administrativos seguros

Todos usam Bearer Auth com `AGENTE_ADMIN_TOKEN`:

- `POST /admin/file/read`
- `POST /admin/file/write`
- `POST /admin/file/patch`
- `POST /admin/file/list`
- `POST /admin/exec`
- `POST /admin/service/status`
- `POST /admin/service/restart`
- `POST /admin/service/logs`
- `POST /admin/deploy/validate`

As ações administrativas são auditadas em:

```text
/opt/agente-divina/logs/admin_actions.log
```

## Project Intelligence

O domínio `project_intelligence` transforma o agente em leitor de projeto antes
de executar alterações. Todos os endpoints usam Bearer Auth com
`AGENTE_ADMIN_TOKEN` e preservam as APIs existentes.

Capabilities registradas:

- `project.scan`
- `frontend.scan`
- `backend.scan`
- `database.scan`
- `memory.search`
- `git.inspect`
- `context.build`
- `architecture.generate`

Endpoints:

- `GET /project-intelligence/capabilities`
- `POST /project-intelligence/dispatch`
- `POST /project-intelligence/project/scan`
- `POST /project-intelligence/frontend/scan`
- `POST /project-intelligence/backend/scan`
- `POST /project-intelligence/database/scan`
- `POST /project-intelligence/memory/search`
- `POST /project-intelligence/git/inspect`
- `POST /project-intelligence/context/build`
- `POST /project-intelligence/architecture/generate`
- `POST /project-intelligence/goal`

Exemplo para GOAL:

```bash
curl -X POST http://127.0.0.1:8050/project-intelligence/goal \
  -H "Authorization: Bearer $AGENTE_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"goal":"Analise o módulo Comercial","execute":true}'
```

O planner reconhece frases como `analisar módulo`, `continuar implantação`,
`reconstruir módulo`, `entender arquitetura` e `levantar dependências`, criando
automaticamente o plano:

```text
context.build
architecture.generate
```

O `context.build` executa internamente os scanners:

```text
project.scan
frontend.scan
backend.scan
database.scan
memory.search
git.inspect
```

e entrega ao motor de arquitetura um objeto único `project_context`.

Cada execução registra auditoria com duração, arquivos analisados, módulos
encontrados, warnings e erros em `/opt/agente-divina/logs/admin_actions.log`.
