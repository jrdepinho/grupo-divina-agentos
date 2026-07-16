import os

from openai import OpenAI

from .base import BaseProvider


class OpenAIProvider(BaseProvider):

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.model = os.getenv(
            "LLM_MODEL_OPENAI",
            "gpt-5.5"
        )

    def complete(
        self,
        prompt,
        system=None,
    ):

        messages = []

        if system:
            messages.append(
                {
                    "role": "system",
                    "content": system,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )

        return {
            "ok": True,
            "provider": "openai",
            "model": self.model,
            "text": response.choices[0].message.content,
        }

    def generate_patch(
        self,
        goal,
        path,
        content,
    ):

        prompt = f"""
Objetivo:

{goal}

Arquivo:

{path}

Conteúdo:

{content}

Retorne SOMENTE o novo conteúdo completo do arquivo.

Não explique.

Não utilize markdown.

Não utilize ```.

"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role":"system",
                    "content":"Você é um engenheiro de software especializado em Python."
                },
                {
                    "role":"user",
                    "content":prompt
                }
            ]
        )

        return {
            "ok": True,
            "provider": "openai",
            "model": self.model,
            "path": path,
            "old": content,
            "new": response.choices[0].message.content,
        }
