from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class CapabilityMetadata:
    name: str
    domain: str
    description: str
    risk: str = "low"
    changes_data: bool = False
    requires_approval: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


CAPABILITY_METADATA: dict[str, CapabilityMetadata] = {
    "goal.echo": CapabilityMetadata(
        name="goal.echo",
        domain="system",
        description="Confirma o recebimento do objetivo.",
    ),
    "admin.capabilities": CapabilityMetadata(
        name="admin.capabilities",
        domain="admin",
        description="Lista capacidades administrativas disponíveis.",
    ),
    "service.status": CapabilityMetadata(
        name="service.status",
        domain="admin",
        description="Consulta o estado de um serviço.",
    ),
    "service.logs": CapabilityMetadata(
        name="service.logs",
        domain="admin",
        description="Consulta logs recentes de um serviço.",
    ),
    "service.restart": CapabilityMetadata(
        name="service.restart",
        domain="admin",
        description="Reinicia um serviço.",
        risk="medium",
        changes_data=True,
        requires_approval=True,
    ),
    "deploy.validate": CapabilityMetadata(
        name="deploy.validate",
        domain="developer",
        description="Valida a aplicação antes de implantação.",
    ),
    "developer.search": CapabilityMetadata(
        name="developer.search",
        domain="developer",
        description="Pesquisa texto no código-fonte.",
    ),
    "developer.read": CapabilityMetadata(
        name="developer.read",
        domain="developer",
        description="Lê arquivo permitido do projeto.",
    ),
    "developer.write": CapabilityMetadata(
        name="developer.write",
        domain="developer",
        description="Escreve conteúdo em arquivo permitido.",
        risk="medium",
        changes_data=True,
        requires_approval=True,
    ),
    "developer.generate_patch": CapabilityMetadata(
        name="developer.generate_patch",
        domain="developer",
        description="Gera patch para arquivo lido.",
    ),

    "developer.patch": CapabilityMetadata(
        name="developer.patch",
        domain="developer",
        description="Aplica alteração pontual em arquivo permitido.",
        risk="medium",
        changes_data=True,
        requires_approval=True,
    ),
    "developer.compile": CapabilityMetadata(
        name="developer.compile",
        domain="developer",
        description="Compila e verifica sintaxe Python.",
    ),
    "developer.validate": CapabilityMetadata(
        name="developer.validate",
        domain="developer",
        description="Executa validações técnicas da aplicação.",
    ),
    "developer.rollback": CapabilityMetadata(
        name="developer.rollback",
        domain="developer",
        description="Restaura o último backup conhecido.",
        risk="high",
        changes_data=True,
        requires_approval=True,
    ),
    "chat.complete": CapabilityMetadata(
        name="chat.complete",
        domain="llm",
        description="Executa conversa direta com o modelo LLM.",
    ),
    "context.read": CapabilityMetadata(
        name="context.read",
        domain="system",
        description="Consulta o contexto atual do AgentOS.",
    ),
}


def get_metadata(name: str) -> CapabilityMetadata:
    return CAPABILITY_METADATA.get(
        name,
        CapabilityMetadata(
            name=name,
            domain="unknown",
            description="Capability sem metadados registrados.",
            risk="unknown",
        ),
    )


def list_metadata() -> list[dict]:
    return [
        metadata.to_dict()
        for metadata in CAPABILITY_METADATA.values()
    ]
