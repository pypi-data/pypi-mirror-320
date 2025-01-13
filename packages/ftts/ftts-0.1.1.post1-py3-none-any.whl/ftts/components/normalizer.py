from .base import BaseComponent
from typing import List
from ftts.data import SpeechList, Speech
from pydantic import Field
from ftts.config import registry, Config
from pathlib import Path
from joblib import Parallel, delayed
from kaldifst import TextNormalizer as KaldiTextNormalizer
import string


EOS = "<EOS>"
TN_ORDERS = {
    "date": ["year", "month", "day"],
    "fraction": ["denominator", "numerator"],
    "measure": ["denominator", "numerator", "value"],
    "money": ["value", "currency"],
    "time": ["noon", "hour", "minute", "second"],
}
EN_TN_ORDERS = {
    "date": ["preserve_order", "text", "day", "month", "year"],
    "money": ["integer_part", "fractional_part", "quantity", "currency_maj"],
}
ITN_ORDERS = {
    "date": ["year", "month", "day"],
    "fraction": ["sign", "numerator", "denominator"],
    "measure": ["numerator", "denominator", "value"],
    "money": ["currency", "value", "decimal"],
    "time": ["hour", "minute", "second", "noon"],
}


class Token:
    def __init__(self, name):
        self.name = name
        self.order = []
        self.members = {}

    def append(self, key, value):
        self.order.append(key)
        self.members[key] = value

    def string(self, orders):
        output = self.name + " {"
        if self.name in orders.keys():
            if (
                "preserve_order" not in self.members.keys()
                or self.members["preserve_order"] != "true"
            ):
                self.order = orders[self.name]

        for key in self.order:
            if key not in self.members.keys():
                continue
            output += ' {}: "{}"'.format(key, self.members[key])
        return output + " }"


class TokenParser:
    def __init__(self, ordertype="tn"):
        if ordertype == "tn":
            self.orders = TN_ORDERS
        elif ordertype == "itn":
            self.orders = ITN_ORDERS
        elif ordertype == "en_tn":
            self.orders = EN_TN_ORDERS
        else:
            raise NotImplementedError()

    def load(self, input):
        assert len(input) > 0
        self.index = 0
        self.text = input
        self.char = input[0]
        self.tokens = []

    def read(self):
        if self.index < len(self.text) - 1:
            self.index += 1
            self.char = self.text[self.index]
            return True
        self.char = EOS
        return False

    def parse_ws(self):
        not_eos = self.char != EOS
        while not_eos and self.char == " ":
            not_eos = self.read()
        return not_eos

    def parse_char(self, exp):
        if self.char == exp:
            self.read()
            return True
        return False

    def parse_chars(self, exp):
        ok = False
        for x in exp:
            ok |= self.parse_char(x)
        return ok

    def parse_key(self):
        assert self.char != EOS
        assert self.char not in string.whitespace

        key = ""
        while self.char in string.ascii_letters + "_":
            key += self.char
            self.read()
        return key

    def parse_value(self):
        assert self.char != EOS
        escape = False

        value = ""
        while self.char != '"':
            value += self.char
            escape = self.char == "\\"
            self.read()
            if escape:
                escape = False
                value += self.char
                self.read()
        return value

    def parse(self, input):
        self.load(input)
        while self.parse_ws():
            name = self.parse_key()
            self.parse_chars(" { ")

            token = Token(name)
            while self.parse_ws():
                if self.char == "}":
                    self.parse_char("}")
                    break
                key = self.parse_key()
                self.parse_chars(': "')
                value = self.parse_value()
                self.parse_char('"')
                token.append(key, value)
            self.tokens.append(token)

    def reorder(self, input):
        self.parse(input)
        output = ""
        for token in self.tokens:
            output += token.string(self.orders) + " "
        return output.strip()


class Normalizer:
    def __init__(
        self,
        lang="zh",
        operator="tn",
        remove_erhua=False,
        enable_0_to_9=False,
    ):
        repo_dir = Path(__file__).parent.parent / "asset" / "wetext"
        assert lang in ["zh", "en"] and operator in ["tn", "itn"]
        tagger_path = repo_dir / lang / operator / "tagger.fst"
        if lang == "zh" and operator == "itn" and enable_0_to_9:
            tagger_path = repo_dir / "zh" / "itn" / "tagger_enable_0_to_9.fst"

        verbalizer_path = repo_dir / lang / operator / "verbalizer.fst"
        if lang == "zh" and operator == "tn" and remove_erhua:
            verbalizer_path = repo_dir / "zh" / "tn" / "verbalizer_remove_erhua.fst"

        self.operator = operator
        self.tagger = KaldiTextNormalizer(str(tagger_path))
        self.verbalizer = KaldiTextNormalizer(str(verbalizer_path))

    def tag(self, text):
        return self.tagger(text)

    def verbalize(self, text):
        text = TokenParser(self.operator).reorder(text)
        return self.verbalizer(text)

    def normalize(self, text):
        return self.verbalize(self.tag(text))


@registry.components.register("normalizer")
class TextNormalizer(BaseComponent):
    input_tags: List[str] = ["speech.text"]
    output_tags: List[str] = ["speech.text"]
    name: str = "normalizer"

    remove_erhua: bool = Field(
        False, description="Remove erhua (儿化) in Mandarin Chinese"
    )
    enable_0_to_9: bool = Field(False, description="Enable 0 to 9 in Mandarin Chinese")
    model: Normalizer | None = None
    num_threads: int = Field(2, description="The number of threads to use")

    def predict(self, speeches: SpeechList[Speech]) -> SpeechList[Speech]:
        _ = Parallel(n_jobs=self.num_threads, prefer="threads")(
            delayed(self.normalize)(speech) for speech in speeches
        )
        return speeches

    def setup(self, **kwargs) -> "TextNormalizer":
        if self.model is None:
            self.model = Normalizer(
                remove_erhua=self.remove_erhua,
                enable_0_to_9=self.enable_0_to_9,
            )
        return self

    def normalize(self, speech: Speech) -> Speech:
        speech.text = self.model.normalize(speech.text)
        return speech

    def get_config(self):
        data = {
            "component": {
                "@components": "normalizer",
                "remove_erhua": self.remove_erhua,
            }
        }
        return Config(data=data)

    def save(self, save_dir: str | Path = "normalizer") -> None:
        save_dir = self.ensure_dir_exists(save_dir)
        config_path = save_dir / "config.cfg"
        config = self.get_config()
        config.to_disk(path=config_path)

    def load(self, save_dir: str | Path = "normalizer") -> "TextNormalizer":
        save_dir = self.assert_dir_exists(save_dir)
        config_path = Path(save_dir) / "config.cfg"
        config = Config().from_disk(path=config_path)
        normalizer = registry.resolve(config=config)["component"]
        return normalizer
