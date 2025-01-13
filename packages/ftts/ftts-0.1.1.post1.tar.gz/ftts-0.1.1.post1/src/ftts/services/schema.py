from pydantic import BaseModel
from ftts.data import Waveform


class TextChunk(BaseModel):
    text: str
    is_last: bool = False
    speaker: str | None = None


class SpeechChunk(BaseModel):
    waveform: Waveform | None = None
    is_last: bool = False
    speaker: str | None = None
