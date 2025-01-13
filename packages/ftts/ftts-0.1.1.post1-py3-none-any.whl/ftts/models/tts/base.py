from ftts.models.base import Model
from typing import List
from ftts.data import Speaker, Waveform
from abc import abstractmethod


class TTSModel(Model):
    @abstractmethod
    def synthesize_waveform(
        self, texts: List[str], speaker: Speaker, **kwargs
    ) -> List[Waveform]:
        pass

    @abstractmethod
    def get_random_speaker(self) -> Speaker:
        pass
