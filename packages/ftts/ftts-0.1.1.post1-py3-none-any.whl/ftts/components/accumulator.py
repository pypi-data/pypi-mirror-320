from .base import BaseComponent
from ftts.data import SpeechList, Speech
from typing_extensions import Self
from ftts.preprocessors.text import StreamSentenceSplitter
from pydantic import Field
from ftts.models.punc.base import PuncModel
from ftts.config import registry


@registry.components.register("text_accumulator")
class TextAccumulator(BaseComponent):
    input_tags = ["speech.text"]
    output_tags = ["speech.text"]
    name = "text_accumulator"

    sentence_splitter: StreamSentenceSplitter = Field(
        StreamSentenceSplitter(), description="the sentence splitter"
    )
    punc_model: PuncModel | None = None
    use_punc_threshold: int = Field(100, description="the threshold to use punc model")

    def predict(self, speeches: SpeechList[Speech]) -> SpeechList[Speech]:
        assert len(speeches) == 1, "only support batch size of 1"
        speech: Speech = speeches[0]
        sent = self.sentence_splitter.process_text(speech.text, is_last=speech.is_last)
        if len(sent) < self.use_punc_threshold:
            return speeches

    def setup(self, model: str = "ct_transformer", **kwargs) -> Self:
        punc_model: PuncModel = registry.punc_models.get(model)()
        self.punc_model = punc_model.from_checkpoint(**kwargs)
        return self
