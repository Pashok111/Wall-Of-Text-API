# Main imports
from pydantic import BaseModel, Field

# Other imports
from typing import Optional, Dict, Literal
from datetime import datetime


class Error(BaseModel):
    error: Dict[Literal["error"], str]


class TextBase(BaseModel):
    username: str
    text: str


class TextCreate(TextBase):
    username: Optional[str] = "Anonymous"


class TextResponse(TextBase):
    id: int
    created_at_utc: datetime


class GetTextsQueryParams(BaseModel):
    model_config = {"extra": "forbid"}

    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)
