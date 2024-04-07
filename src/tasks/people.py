from typing import Optional

import requests
from openai import OpenAI
from pydantic import BaseModel

from src import utils
from src.exceptions import StoppedByModeration
from src.openai_utils import ask_model, is_flagged
from src.settings import get_settings
from src.tasks.people_prompts import get_get_name_prompt, get_user_info_prompt

TASK_NAME: str = "people"
DATA_URL: str = "/data/people.json"
settings = get_settings()
client: OpenAI = OpenAI(api_key=settings.openai_api_key)


class TaskResponse(BaseModel):
    code: int
    msg: str
    question: Optional[str] = None
    answer: Optional[str] = None
    memory_db: Optional[dict] = {}

    @property
    def name_index(self) -> str:  # unused
        lines = ["| imie | naazwisko | klucz |", "| - | - | - | "]
        for k, v in self.memory_db.items():
            lines.append(f"| {v['imie']} | {v['nazwisko']} | {k} | ")
        return "\n".join(lines)

    def set_answer(self):
        if is_flagged([self.question]):
            raise StoppedByModeration(self.question)
        full_name = ask_model(client, messages=get_get_name_prompt(self.question))
        key = "-".join(full_name.lower().split(" "))
        person_data = self.memory_db[key]
        self.answer = ask_model(
            client, messages=get_user_info_prompt(person_data, self.question)
        )

    def populate_db(self) -> None:
        response = requests.get(f"{settings.task_url}{DATA_URL}")
        for person in response.json():
            key = f"{person['imie'].lower()}-{person['nazwisko'].lower()}"
            self.memory_db[key] = person


def solve(task_name: str) -> None:
    token_url: str = utils.get_token_url(task_name)
    token: str = utils.get_token(token_url)
    task_url: str = utils.get_task_url(token)
    task_obj = TaskResponse(**utils.get_task(task_url).json())
    task_obj.populate_db()
    task_obj.set_answer()

    utils.send_answer(token=token, answer=task_obj.answer)


if __name__ == "__main__":
    # utils.print_task(TASK_NAME)
    solve(TASK_NAME)
