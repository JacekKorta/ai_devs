from typing import Any

from openai import OpenAI
from pydantic import BaseModel

from src import utils
from src.exceptions import StoppedByModeration
from src.openai_utils import is_flagged
from src.settings import get_settings

TASK_NAME: str = ""
settings = get_settings()
client: OpenAI = OpenAI(api_key=settings.openai_api_key)


class TaskResponse(BaseModel):
    code: int
    msg: str
    x: Any
    answer: Any

    def set_answer(self):
        if is_flagged(self.x):
            raise StoppedByModeration(self.x)


def solve(task_name: str) -> None:
    token_url: str = utils.get_token_url(task_name)
    token: str = utils.get_token(token_url)
    task_url: str = utils.get_task_url(token)
    task_obj = TaskResponse(**utils.get_task(task_url).json())
    task_obj.set_answer()

    utils.send_answer(token=token, answer=task_obj.answer)


if __name__ == "__main__":
    utils.print_task(TASK_NAME)
    # solve(TASK_NAME)
