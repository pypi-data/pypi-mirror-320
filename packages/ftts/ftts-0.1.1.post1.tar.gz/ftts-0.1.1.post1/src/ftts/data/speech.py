from docarray import BaseDoc, DocList
from docarray.typing import NdArray
from pydantic import Field, ConfigDict
from typing import Dict, Iterable
from queue import Queue
import numpy as np
from pathlib import Path


class Waveform(BaseDoc):
    id: str | None = Field(None, description="the waveform id")
    data: NdArray | None = Field(None, description="the waveform data")
    sample_rate: int | None = Field(None, description="the sample rate of the waveform")

    def display(self, start: int | None = None, end: int | None = None):
        """display the waveform in a Jupyter notebook"""
        from IPython.display import Audio

        data = self.select_waveform(start, end)
        return Audio(data=data, rate=self.sample_rate)

    def select_waveform(
        self, start_ms: float | None, end_ms: float | None = None
    ) -> np.ndarray:
        if start_ms is None:
            start_ms = 0
        if end_ms is None:
            end_ms = self.duration_ms
        start_idx = int(start_ms * (self.sample_rate // 1000))
        end_idx = int(end_ms * (self.sample_rate // 1000))
        return self.data[start_idx:end_idx]

    @property
    def duration_ms(self) -> float:
        """the waveform duration in milliseconds"""
        return len(self.data) / self.sample_rate * 1000

    @property
    def duration(self) -> float:
        """the waveform duration in seconds"""
        return len(self.data) / self.sample_rate


class StreamWaveform(Waveform):
    id: str | None = Field(None, description="the waveform id")
    data: NdArray | None = Field(None, description="the stream waveform data")
    stream: Iterable[NdArray] | None = Field(
        None, description="the stream waveform data"
    )
    sample_rate: int | None = Field(None, description="the sample rate of the waveform")

    def streaming_data(self) -> Iterable[np.ndarray]:
        """streaming the waveform data

        Yields:
            Iterator[Iterable[np.ndarray]]: the waveform data
        """
        if self.data is None:
            self.data = np.array([])
        for waveform in self.stream:
            waveform: np.ndarray
            if len(waveform.shape) == 1:
                yield waveform
                self.data = np.concatenate([self.data, waveform], axis=0)
            else:
                yield waveform[0]
                self.data = np.concatenate([self.data, waveform[0]], axis=0)
        self.stream = None

    def display(self):
        """display the stream waveform"""
        import sounddevice as sd

        stream = sd.OutputStream(samplerate=self.sample_rate, channels=1)
        with stream:
            if self.stream is not None:
                for waveform in self.streaming_data():
                    stream.write(waveform)
            else:
                stream.write(self.data.astype(np.float32))


class Speaker(BaseDoc):
    """the speaker representation"""

    id: str | None = Field(None, description="the speaker id")
    name: str | None = Field(None, description="the speaker name")
    embedding: NdArray | None = Field(None, description="the speaker embedding")
    sample: Waveform | str | None = Field(None, description="the speaker sample")

    def save_json(self, path: str | Path):
        """save the speaker to a json file"""
        import json

        with open(path, "w") as f:
            json.dump(self.model_dump(), f)

    def load_json(self, path: str | Path) -> "Speaker":
        """load the speaker from a json file"""
        import json

        with open(path, "r") as f:
            data = json.load(f)
        speaker = self.model_construct(**data)
        return speaker


class Speech(BaseDoc):
    """the speech representation"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, extra="ignore"
    )

    id: str | None = Field(None, description="the speech id")
    text: str | None = Field(None, description="the speech text")
    waveform: Waveform | StreamWaveform | None = Field(
        None, description="the speech waveform"
    )
    speaker: Speaker | None = Field(None, description="the speech speaker")
    is_last: bool | None = Field(None, description="the speech is the last")
    is_bad: bool | None = Field(None, description="the speech is bad")
    bad_reason: str | None = Field(None, description="the speech bad reason")
    bad_component: str | None = Field(None, description="the speech bad component")

    spent_time: Dict[str, float] | None = Field(
        None, title="Time spent on processing the audio."
    )

    def display(self):
        """display the speech in a Jupyter notebook"""
        return self.waveform.display()

    def set_speaker(
        self,
        id: str | None = None,
        name: str | None = None,
        embedding: NdArray | None = None,
        sample: Waveform | str | None = None,
    ) -> None:
        """set the speaker of the speech"""
        self.speaker = Speaker(id=id, name=name, embedding=embedding, sample=sample)

    def set_waveform(self, data: NdArray, sample_rate: int):
        """set the waveform of the speech"""
        self.waveform = Waveform(data=data, sample_rate=sample_rate)

    def set_stream_waveform(self, stream: Iterable[NdArray], sample_rate: int):
        """set the waveform of the speech"""
        self.waveform = StreamWaveform(stream=stream, sample_rate=sample_rate)

    def stream(self) -> Iterable[np.ndarray]:
        """stream the speech waveform"""
        assert isinstance(
            self.waveform, StreamWaveform
        ), "The waveform is not a stream waveform"
        return self.waveform.streaming_data()

    @property
    def duration(self) -> float | None:
        """the speech duration"""
        if self.waveform is not None:
            return round(len(self.waveform.data) / self.waveform.sample_rate, 2)
        return None

    @property
    def duration_ms(self) -> float | None:
        """the speech duration in milliseconds"""
        if self.waveform is not None:
            return round(len(self.waveform.data) / self.waveform.sample_rate * 1000, 2)
        return None


class SpeechList(DocList):
    """the speech list representation"""

    @property
    def duration(self) -> float:
        """the speech duration"""
        return sum(speech.duration for speech in self)

    @property
    def duration_ms(self) -> float:
        """the speech duration in milliseconds"""
        return sum(speech.duration_ms for speech in self)


class SpeechQueue(Queue):
    """the speech queue representation"""

    pass
