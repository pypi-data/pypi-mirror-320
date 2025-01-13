from .base import BaseTextProcessor
from typing import List
from ftts.models.punc.base import PuncModel


class StreamSentenceSplitter(BaseTextProcessor):
    buffer: str = ""
    use_level2_threshold: int = 100
    use_level3_threshold: int = 200

    def process_text(
        self,
        text: str,
        is_last: bool = False,
        punc_model: PuncModel = None,
        use_punc_threshold: int = 100,
        **kwargs,
    ) -> List[str]:
        self.buffer = self.buffer + text
        if punc_model is not None:
            if len(self.buffer) >= use_punc_threshold:
                self.buffer = punc_model.restore(self.buffer)
        sentences, indices = self.split_sentences(self.buffer)
        assert len(sentences) == len(
            indices
        ), "The number of sentences and indices do not match"
        if not is_last:
            if len(indices) != 0:
                self.buffer = self.buffer[indices[-1] + 1 :]
            return sentences
        else:
            if len(sentences) == 0:
                sentences = [self.buffer]
                self.buffer = ""
                return sentences
            if indices[-1] == len(self.buffer) - 1:
                self.buffer = ""
                return sentences
            else:
                self.buffer = ""
                return sentences + [text[indices[-1] + 1 :]]

    def split_sentences(self, text: str) -> List[str]:
        indices = self.get_sentence_end_indices(text)
        sentences = []
        start = 0
        for i in indices:
            sentences.append(text[start : i + 1])
            start = i + 1
        return sentences, indices

    def is_sentence_end_level1(self, text: str) -> bool:
        return text.endswith(
            (
                "!",
                "?",
                "。",
                "？",
                "！",
                "；",
                ";",
            )
        )

    def is_sentence_end_level2(self, text: str) -> bool:
        return text.endswith(
            (
                "、",
                "...",
                "…",
                ",",
                "，",
            )
        )

    def is_sentence_end_level3(self, text: str) -> bool:
        return text.endswith(
            (
                ":",
                "：",
            )
        )

    def get_sentence_end_indices(self, text: str) -> List[int]:
        sents_l1 = [i for i, c in enumerate(text) if self.is_sentence_end_level1(c)]
        if len(sents_l1) == 0 and len(text) > self.use_level2_threshold:
            sents_l2 = [i for i, c in enumerate(text) if self.is_sentence_end_level2(c)]
            if len(sents_l2) == 0 and len(text) > self.use_level3_threshold:
                sents_l3 = [
                    i for i, c in enumerate(text) if self.is_sentence_end_level3(c)
                ]
                return sents_l3
            else:
                return sents_l2

        else:
            return sents_l1

    def reset(self):
        self.buffer = ""
