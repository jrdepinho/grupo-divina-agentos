from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    def generate_patch(
        self,
        goal: str,
        path: str,
        content: str,
    ):
        pass
