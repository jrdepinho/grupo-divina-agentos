from .base import BaseProvider

class AzureProvider(BaseProvider):

    def generate_patch(self, goal, path, content):
        raise NotImplementedError(
            "AzureProvider ainda não implementado."
        )
