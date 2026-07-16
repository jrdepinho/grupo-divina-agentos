from .config import LLM_PROVIDER
import os


class LLMClient:

    def __init__(self):

        provider = (LLM_PROVIDER or "").lower()

        if provider == "auto":

            if os.getenv("OPENAI_API_KEY"):
                from .providers.openai import OpenAIProvider
                self.provider = OpenAIProvider()

            elif os.getenv("OPENROUTER_API_KEY"):
                from .providers.openrouter import OpenRouterProvider
                self.provider = OpenRouterProvider()

            elif os.getenv("OLLAMA_URL"):
                from .providers.ollama import OllamaProvider
                self.provider = OllamaProvider()

            else:
                raise RuntimeError(
                    "Nenhum provider LLM configurado."
                )

        elif provider == "openai":
            from .providers.openai import OpenAIProvider
            self.provider = OpenAIProvider()

        elif provider == "openrouter":
            from .providers.openrouter import OpenRouterProvider
            self.provider = OpenRouterProvider()

        elif provider == "ollama":
            from .providers.ollama import OllamaProvider
            self.provider = OllamaProvider()

        elif provider == "azure":
            from .providers.azure import AzureProvider
            self.provider = AzureProvider()

        else:
            raise RuntimeError(
                f"Provider desconhecido: {provider}"
            )

    def generate_patch(
        self,
        goal,
        path,
        content,
    ):
        return self.provider.generate_patch(
            goal,
            path,
            content,
        )

    def complete(
        self,
        prompt,
        system=None,
    ):
        return self.provider.complete(
            prompt,
            system,
        )
