from typing import Optional

import requests
from openai import OpenAI
from pydantic import BaseModel

from src import utils
from src.settings import get_settings

TASK_NAME: str = "liar"
settings = get_settings()
client: OpenAI = OpenAI(api_key=settings.openai_api_key)


class TaskResponse(BaseModel):
    question: str = "podaj nazwe stolicy polski"
    expected_answer: str = "warszawa"
    code: int
    msg: str
    server_response: Optional[str] = None
    answer: Optional[str] = None

    def set_answer(self, task_url: str):
        data = {"question": self.question}
        response = requests.post(task_url, data=data)
        self.server_response = response.json().get("answer")
        self.answer = self.is_true()

    def is_true(self) -> str:
        if self.expected_answer in self.server_response.lower():
            return "YES"
        return "NO"


def solve(task_name: str) -> None:
    token_url: str = utils.get_token_url(task_name)
    token: str = utils.get_token(token_url)
    task_url: str = utils.get_task_url(token)
    task_obj = TaskResponse(**utils.get_task(task_url).json())
    task_obj.set_answer(task_url)

    utils.send_answer(token=token, answer=task_obj.answer)


if __name__ == "__main__":
    # utils.print_task(TASK_NAME)
    solve(TASK_NAME)
