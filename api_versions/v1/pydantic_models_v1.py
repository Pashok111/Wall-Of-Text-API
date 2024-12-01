# Main imports
from pydantic import BaseModel, Field, StringConstraints

# Other imports
from typing import Annotated
from datetime import datetime


class Error(BaseModel):
    error: str


class TextBase(BaseModel):
    username: str
    text: str


class TextCreate(TextBase):
    username: Annotated[
        str,
        StringConstraints(min_length=3, strip_whitespace=True)  # noqa
    ] = "Anonymous"
    text: Annotated[
        str,
        StringConstraints(min_length=1, strip_whitespace=True)  # noqa
    ]


class TextResponse(TextBase):
    id: int
    created_at_utc: datetime


class GetTextsQueryParams(BaseModel):
    model_config = {"extra": "forbid"}

    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)
