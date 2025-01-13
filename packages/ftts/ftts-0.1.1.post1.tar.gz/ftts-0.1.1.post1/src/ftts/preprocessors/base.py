from pydantic import BaseModel
from abc import abstractmethod


class BaseTextProcessor(BaseModel):
    @abstractmethod
    def process_text(self, text: str) -> str:
        raise NotImplementedError

    def __call__(self, text: str) -> str:
        return self.process_text(text)
