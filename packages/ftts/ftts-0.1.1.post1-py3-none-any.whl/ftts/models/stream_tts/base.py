from ftts.models.base import CachedModel
from abc import abstractmethod
from ftts.data import Speaker, StreamWaveform


class StreamTTSModel(CachedModel):
    @abstractmethod
    def synthesize_waveform_stream(
        self, text: str, speaker: Speaker, **kwargs
    ) -> StreamWaveform:
        pass

    @abstractmethod
    def get_random_speaker(self) -> Speaker:
        pass
