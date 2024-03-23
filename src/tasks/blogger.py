from typing import List, Optional

from openai import OpenAI
from pydantic import BaseModel

from src import utils
from src.exceptions import StoppedByModeration
from src.openai_utils import is_flagged
from src.settings import get_settings

TASK_NAME: str = "blogger"
settings = get_settings()
client: OpenAI = OpenAI(api_key=settings.openai_api_key)


class TaskResponse(BaseModel):
    code: int
    msg: str
    blog: List[str]
    answer: Optional[List[str]] = None

    def set_answer(self):
        if is_flagged(self.blog):
            raise StoppedByModeration(self.blog)
        response = client.chat.completions.create(
            temperature=0.3,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful food blogger"},
                {
                    "role": "user",
                    "content": f"Write blog posts for these topics {self.blog}."
                    f" return one string separate posts by '#@#'",
                },
            ],
        )
        response = response.choices[0].message.content
        data = response.split("#@#")
        self.answer = data


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
