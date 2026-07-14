from __future__ import annotations

from pydantic import BaseModel


class SyncMetadataRequest(BaseModel):
    schema_name: str = "public"
    batch_size: int = 20


class AdminExecRequest(BaseModel):
    cmd: str
    cwd: str = "/opt/agente-divina-v2"


class AdminReadFileRequest(BaseModel):
    path: str


class AdminWriteFileRequest(BaseModel):
    path: str
    content: str = ""


class AdminListFilesRequest(BaseModel):
    path: str = "/opt/agente-divina-v2"
    pattern: str = "*"
    max_items: int = 300


class AdminGitRequest(BaseModel):
    action: str
    message: str = ""
    cwd: str = "/opt/agente-divina-v2"


class AdminSupabaseQueryRequest(BaseModel):
    sql: str
    params: list = []


class AdminPatchFileRequest(BaseModel):
    file: str
    search: str
    replace: str
    compile_python: bool = False


class AdminRestartServiceRequest(BaseModel):
    service: str = "agente-divina-api.service"


class SQLRequest(BaseModel):
    sql: str


class ShellRequest(BaseModel):
    cmd: str

