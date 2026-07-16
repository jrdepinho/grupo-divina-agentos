import os

from openai import OpenAI


class OpenRouterProvider:

    def __init__(self):

        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY não configurada."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

        self.model = os.getenv(
            "LLM_MODEL_OPENROUTER",
            "openai/gpt-4.1-mini",
        )

    def generate_patch(
        self,
        goal,
        path,
        content,
    ):

        prompt = f"""
Você é um engenheiro de software especialista.

Objetivo:
{goal}

Arquivo:
{path}

Conteúdo atual:

{content}

Retorne APENAS o conteúdo completo do arquivo atualizado.

Não utilize markdown.

Não utilize ```.

Não explique.

Retorne somente o código.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "Você gera patches completos de código.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        new_content = response.choices[0].message.content.strip()

        return {
            "ok": True,
            "content": new_content,
        }
