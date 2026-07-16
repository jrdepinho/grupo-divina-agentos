from .client import LLMClient


def generate_patch(goal, path, content):

    client = LLMClient()

    return client.generate_patch(
        goal=goal,
        path=path,
        content=content,
    )
