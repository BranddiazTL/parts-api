from pydantic import BaseModel
from typing import Optional
from enum import StrEnum


class TokenType(StrEnum):
    BEARER = "bearer"


class Token(BaseModel):
    access_token: str
    token_type: TokenType


class TokenData(BaseModel):
    username: Optional[str] = None
