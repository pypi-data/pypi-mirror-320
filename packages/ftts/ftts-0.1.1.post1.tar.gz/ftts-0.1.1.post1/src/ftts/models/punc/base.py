from ftts.models.base import Model
from abc import abstractmethod


class PuncModel(Model):
    @abstractmethod
    def restore(self, text: str) -> str:
        raise NotImplementedError
