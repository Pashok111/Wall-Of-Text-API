# Main imports
from pydantic import BaseModel, Field, StringConstraints
from pydantic.functional_validators import BeforeValidator

# Other imports
from typing import Annotated, List


class Error(BaseModel):
    error: str


class TextBase(BaseModel):
    username: str
    text: str
    parent_id: int = -1


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
    utc_created_at: Annotated[float, BeforeValidator(lambda t: t.timestamp())]
    comments: List["TextResponse"] = []


class GetTextsQueryParams(BaseModel):
    model_config = {"extra": "forbid"}

    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)
    parent_id: int = None
    include_comments: bool = True


TextResponse.model_rebuild()
