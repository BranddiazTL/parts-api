from enum import StrEnum
from typing import Optional

from pydantic import BaseModel


class TokenType(StrEnum):
    BEARER = "bearer"


class Token(BaseModel):
    access_token: str
    token_type: TokenType


class TokenData(BaseModel):
    username: Optional[str] = None
