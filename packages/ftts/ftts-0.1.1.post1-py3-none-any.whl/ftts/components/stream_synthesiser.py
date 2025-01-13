from .base import BaseComponent
from typing import List, Literal
from typing_extensions import Self
from pydantic import Field, validate_call
from ftts.data import SpeechList, Speech, Speaker, Waveform, StreamWaveform
from pathlib import Path
from ftts.config import registry
from ftts.models.stream_tts.base import StreamTTSModel


@registry.components.register("stream_synthesiser")
class StreamSpeechSynthesiser(BaseComponent):
    name: str = "stream_synthesiser"
    input_tags: List[str] = ["speech.text", "speaker.id"]
    output_tags: List[str] = ["speech.waveform.stream", "speech.speaker"]

    model: StreamTTSModel | None = Field(
        None, description="The model used to synthesize speech"
    )
    speaker: Speaker | None = Field(
        None, description="The speaker to use for synthesis"
    )
    refine_text: bool = Field(False, description="Whether to refine the text")
    oral: int = Field(5, ge=0, le=9, description="The oral strength")
    laugh: int = Field(0, ge=0, le=2, description="The laugh strength")
    stop: int = Field(0, ge=0, le=2, description="The stop strength")
    speed: int = Field(5, ge=1, le=9, description="The speed of the speech synthesis")

    def predict(self, speeches: SpeechList[Speech]) -> SpeechList[Speech]:
        assert len(speeches) == 1, "Streaming synthesis only supports one speech"
        if not self.speaker:
            speaker = self.model.get_random_speaker()
        else:
            speaker = self.speaker
        if speeches[0].text is not None:
            waveform_stream = self.predict_waveform_stream(
                text=speeches[0].text,
                speaker=speaker,
                speed=self.speed,
                skip_refine_text=not self.refine_text,
                oral=self.oral,
                laugh=self.laugh,
                stop=self.stop,
            )
            speeches = self.set_stream_waveform(
                speeches=speeches, waveform=waveform_stream
            )
            speeches = self.set_speaker(speeches=speeches, speaker=speaker)
        return speeches

    def predict_waveform_stream(
        self, text: str, speaker: Speaker, **kwargs
    ) -> Waveform:
        waveform = self.model.synthesize_waveform_stream(
            text=text, speaker=speaker, **kwargs
        )
        return waveform

    def set_stream_waveform(
        self, speeches: SpeechList[Speech], waveform: StreamWaveform
    ) -> SpeechList[Speech]:
        assert len(speeches) == 1, "Streaming synthesis only supports one speech"
        speech: Speech = speeches[0]
        speech.set_stream_waveform(
            stream=waveform.stream, sample_rate=waveform.sample_rate
        )
        return speeches

    def set_speaker(
        self, speeches: SpeechList[Speech], speaker: Speaker
    ) -> SpeechList[Speech]:
        for speech in speeches:
            speech: Speech
            speech.set_speaker(
                id=speaker.id, embedding=speaker.embedding, sample=speaker.sample
            )
        return speeches

    @validate_call
    def setup(
        self,
        checkpoint_dir: str | Path | None = None,
        device: str | None = None,
        compile: bool = False,
        speaker_path: str | Path = None,
        model: Literal["stream_chattts_v1", "stream_chattts_v2"] = "stream_chattts_v1",
        **kwargs,
    ) -> Self:
        self.model: StreamTTSModel = registry.stream_tts_models.get(name=model)()
        self.model = self.model.from_checkpoint(
            checkpoint_dir=checkpoint_dir, device=device, compile=compile, **kwargs
        )
        if speaker_path is not None:
            speaker = Speaker().load_json(speaker_path)
            self.speaker = speaker
        return self
