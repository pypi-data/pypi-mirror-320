from docarray import BaseDoc
from pydantic import Field
from docarray.typing import ID
from typing import List


class Token(BaseDoc):
    id: ID | None = None

    text: str = Field(..., description="the token text")
    follow: str = Field("", description="the follow punctuation")


class Span(BaseDoc):
    id: ID | None = None

    start: int = Field(..., description="the start index")
    end: int = Field(..., description="the end index")
    text: str = Field(..., description="the span text")


class Text(BaseDoc):
    id: ID | None = None

    raw_text: str = Field(..., description="the text")
    tokens: List[Token] = Field([], description="the token list")
    sents: List[str] = Field([], description="the sentence list")
