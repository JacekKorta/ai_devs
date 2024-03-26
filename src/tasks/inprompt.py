from typing import Any, List, Optional

from openai import OpenAI
from pydantic import BaseModel

from src import utils
from src.exceptions import StoppedByModeration
from src.openai_utils import is_flagged
from src.settings import get_settings

TASK_NAME: str = "inprompt"
settings = get_settings()
client: OpenAI = OpenAI(api_key=settings.openai_api_key)

# todo: dodać logger + pl > eng
# todo: wyodrębnić zapytania do openai do osobnej funkcji


class TaskResponse(BaseModel):
    code: int
    msg: str
    input: List[str]
    question: Optional[str]
    answer: Optional[Any] = None
    database: Optional[dict] = {}

    def set_answer(self, name):
        response = client.chat.completions.create(
            temperature=0.3,
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Odpowiedz na pytanie otrzymane pytanie. "
                    "Do odpowiedzi uzyj tylko danych z dostarczonego kontekstu:"
                    f"\n### Context: {self.database.get(name)}",
                },
                {"role": "user", "content": f"{self.question}"},
            ],
        )
        self.answer = response.choices[0].message.content
        print(f">> odpowiedz to: {self.answer}")

    def set_db(self):
        for line in self.input:
            name = line.split()[0]
            self.database[name] = line
        print(">> Zasilono DB")

    def get_name(self):
        if is_flagged([self.question]):
            raise StoppedByModeration(self.x)
        response = client.chat.completions.create(
            temperature=0.3,
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Twoim zadaniem jest wyciągnięcie imienia z tekstu. "
                    "Zwróć Jedno słowo: imię w Mianowniku i nic więcej.",
                },
                {"role": "user", "content": f"{self.question}"},
            ],
        )
        name = response.choices[0].message.content
        print(f">> Uzyskane imię to {name}")
        return name


def solve(task_name: str) -> None:
    token_url: str = utils.get_token_url(task_name)
    token: str = utils.get_token(token_url)
    task_url: str = utils.get_task_url(token)
    task_obj = TaskResponse(**utils.get_task(task_url).json())
    task_obj.set_db()
    name = task_obj.get_name()
    task_obj.set_answer(name)

    utils.send_answer(token=token, answer=task_obj.answer)


if __name__ == "__main__":
    # utils.print_task(TASK_NAME)
    solve(TASK_NAME)
