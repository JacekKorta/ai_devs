from typing import Any

from pydantic import BaseModel


class TokenRequest(BaseModel):
    apikey: str


class TokenResponse(BaseModel):
    code: int
    msg: str
    token: str


class AnswerRequest(BaseModel):
    answer: Any
