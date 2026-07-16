from .base import BaseProvider

class OllamaProvider(BaseProvider):

    def generate_patch(self, goal, path, content):
        raise NotImplementedError(
            "OllamaProvider ainda não implementado."
        )
