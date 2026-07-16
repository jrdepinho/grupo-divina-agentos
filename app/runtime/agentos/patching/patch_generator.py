from __future__ import annotations

import os

from openai import OpenAI


class PatchGenerator:

    def generate(
        self,
        goal: str,
        source: str,
        path: str,
    ) -> str:

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY não configurada no ambiente."
            )

        client = OpenAI(api_key=api_key)

        prompt = f"""
Você é um engenheiro Python experiente.

Objetivo:
{goal}

Arquivo:
{path}

Código atual:

{source}

Regras:
- Corrija somente o necessário.
- Preserve todo o restante.
- Retorne apenas o código Python completo atualizado.
- Não use blocos Markdown.
- Não inclua explicações.
"""

        response = client.responses.create(
            model=os.getenv("OPENAI_PATCH_MODEL", "gpt-5.5"),
            input=prompt,
        )

        content = response.output_text.strip()

        if content.startswith("```"):
            lines = content.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            content = "\n".join(lines).strip()

        if not content:
            raise RuntimeError(
                "O modelo retornou conteúdo vazio."
            )

        return content
