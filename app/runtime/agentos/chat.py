from app.runtime.agentos.llm.client import LLMClient


def chat_complete(
    goal: str,
    **kwargs,
):
    client = LLMClient()

    result = client.complete(
        prompt=goal,
        system=(
            "Você é o AgentOS. "
            "Responda de forma objetiva e técnica."
        ),
    )

    return {
        "ok": True,
        "answer": result["text"],
        "provider": result["provider"],
        "model": result["model"],
    }
