# Other imports
from typing import Annotated, List

# Main imports
from pydantic import BaseModel, Field, StringConstraints
from pydantic.functional_validators import BeforeValidator


class Error(BaseModel):
    """
    Represents an error message.

    Attributes:

    - error (str): The error message.
    """
    error: str


class TextBase(BaseModel):
    """
    Base model for text-related models.
    """
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
    comment_depth: int = 0
    comments: List["TextResponse"] = Field(default_factory=list)  # noqa


class GetTextsQueryParams(BaseModel):
    model_config = {"extra": "forbid"}

    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)
    parent_id: int = None
    include_comments: bool = True


TextResponse.model_rebuild()
