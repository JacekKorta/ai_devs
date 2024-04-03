import time
from typing import Optional

import requests
from openai import OpenAI
from pydantic import BaseModel

from src import utils
from src.settings import get_settings

TASK_NAME: str = "scraper"
settings = get_settings()
client: OpenAI = OpenAI(api_key=settings.openai_api_key)


class TaskResponse(BaseModel):
    code: int
    msg: str
    input: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    article: Optional[str] = None

    def set_answer(self):
        response = client.chat.completions.create(
            temperature=0.3,
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Odpowiedz na pytanie otrzymane pytanie. "
                    "Do odpowiedzi uzyj tylko danych z dostarczonego kontekstu:"
                    f"\n### Context: {self.article}",
                },
                {"role": "user", "content": f"{self.question}"},
            ],
        )
        self.answer = response.choices[0].message.content
        print(f">> odpowiedz to: {self.answer}")

    def get_article(self) -> None:
        article = ""
        loop = 1
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        }
        while not article:
            print(f"Pobieram artykuł. Próba {loop}")
            try:
                response = requests.get(self.input, headers=headers)
                response.raise_for_status()
            except Exception as e:
                print(f"Receive exception: {e}")
            else:
                article = response.text
            time.sleep(loop)
            loop += 1
        self.article = article


def solve(task_name: str) -> None:
    token_url: str = utils.get_token_url(task_name)
    token: str = utils.get_token(token_url)
    task_url: str = utils.get_task_url(token)
    task_obj = TaskResponse(**utils.get_task(task_url).json())
    task_obj.get_article()
    task_obj.set_answer()

    utils.send_answer(token=token, answer=task_obj.answer)


if __name__ == "__main__":
    # utils.print_task(TASK_NAME)
    solve(TASK_NAME)
