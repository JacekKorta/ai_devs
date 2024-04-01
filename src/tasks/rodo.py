from typing import Optional

from openai import OpenAI
from pydantic import BaseModel

from src import utils
from src.settings import get_settings

TASK_NAME: str = "rodo"
settings = get_settings()
client: OpenAI = OpenAI(api_key=settings.openai_api_key)

PROMPT = """
Napisz kilka zdań o sobie.
Wszystkie użyte imiona, nazwisko, zawody, miasta zamień na %imie%, %nazwisko%, %miasto%, %zawod%
"""


class TaskResponse(BaseModel):
    code: int
    msg: str
    answer: Optional[str] = None


def solve(task_name: str) -> None:
    token_url: str = utils.get_token_url(task_name)
    token: str = utils.get_token(token_url)
    task_url: str = utils.get_task_url(token)
    task_obj = TaskResponse(**utils.get_task(task_url).json())
    task_obj.answer = PROMPT
    utils.send_answer(token=token, answer=task_obj.answer)


if __name__ == "__main__":
    # utils.print_task(TASK_NAME)
    solve(TASK_NAME)
