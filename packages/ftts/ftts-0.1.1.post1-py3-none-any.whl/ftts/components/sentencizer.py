from .base import BaseComponent
from ftts.data import Speech, SpeechList
from typing_extensions import Self


class StreamSentencizer(BaseComponent):
    def predict(self, speeches: SpeechList[Speech]) -> SpeechList[Speech]:
        return super().predict(speeches)

    def setup(self, **kwargs) -> Self:
        return super().setup(**kwargs)
