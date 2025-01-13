from .base import BaseComponent
from typing import List
from pydantic import Field
from ftts.data import SpeechList, Speech, Speaker, Waveform
from pathlib import Path
from ftts.config import registry
from ftts.models.tts.base import TTSModel


@registry.components.register("synthesizer")
class SpeechSynthesiser(BaseComponent):
    name: str = "synthesiser"
    input_tags: List[str] = ["speech.text", "speech.speaker"]
    output_tags: List[str] = ["speech.waveform", "speech.speaker"]

    speed: int = Field(5, description="The speed of the speech synthesis", ge=1, le=9)
    model: TTSModel | None = Field(
        None, description="The model used to synthesize speech"
    )
    speaker: Speaker | None = Field(
        None, description="The speaker to use for synthesis"
    )
    refine_text: bool = Field(False, description="Whether to refine the text")

    def predict(self, speeches: SpeechList[Speech]) -> SpeechList[Speech]:
        if not self.speaker:
            speaker = self.model.get_random_speaker()
        else:
            speaker = self.speaker
        texts = [speech.text for speech in speeches]
        waveform: Waveform = self.predict_waveform(
            texts=texts,
            speaker=speaker,
            speed=self.speed,
            skip_refine_text=not self.refine_text,
        )
        speeches = self.set_waveform(speeches=speeches, waveforms=waveform)
        speeches = self.set_speaker(speeches=speeches, speaker=speaker)
        return speeches

    def predict_waveform(
        self, texts: List[str], speaker: Speaker, **kwargs
    ) -> List[Waveform]:
        waveforms = self.model.synthesize_waveform(
            texts=texts, speaker=speaker, **kwargs
        )
        assert len(waveforms) == len(
            texts
        ), "The number of waveforms should be equal to the number of texts"
        return waveforms

    def set_waveform(
        self, speeches: SpeechList[Speech], waveforms: List[Waveform]
    ) -> SpeechList[Speech]:
        assert len(speeches) == len(
            waveforms
        ), "The number of waveforms should be equal to the number of speeches"
        for speech, waveform in zip(speeches, waveforms):
            speech: Speech
            speech.set_waveform(data=waveform.data, sample_rate=waveform.sample_rate)
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

    def setup(
        self,
        device: str | None = None,
        compile: bool = False,
        speaker_path: str | Path = None,
        model: str = "chattts",
        **kwargs,
    ) -> "SpeechSynthesiser":
        model: TTSModel = registry.tts_models.get(model)()
        self.model = model.from_checkpoint(device=device, compile=compile, **kwargs)
        if speaker_path is not None:
            speaker = Speaker().load_json(speaker_path)
            self.speaker = speaker
        return self
