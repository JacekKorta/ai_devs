from pydantic import BaseModel


class TokenRequest(BaseModel):
    apikey: str


class TokenResponse(BaseModel):
    code: int
    msg: str
    token: str


# ten model jest zmienny
class TaskResponse(BaseModel):
    code: int
    msg: str
    cookie: str # to pole ni ejst stałe


class AnswerRequest(BaseModel):
    answer: str


class AnswerResponse(BaseModel):
    code: int
    msg: str
    note: str
