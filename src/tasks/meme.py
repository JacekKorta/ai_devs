from typing import Optional

import requests
from openai import OpenAI
from pydantic import BaseModel

from src import utils
from src.settings import get_settings

TASK_NAME: str = "meme"
settings = get_settings()
client: OpenAI = OpenAI(api_key=settings.openai_api_key)

RENDER_FORM_URL = "https://api.renderform.io"
TEMPLATE_ID = "puffy-vampires-argue-briefly-1198"


def get_meme(image, text) -> str:
    headers = {
        "accept": "application/json",
        "x-api-key": settings.renderform_api_key,
        "Content-Type": "application/json",
    }
    body = {
        "template": TEMPLATE_ID,
        "data": {
            "text_box.text": text,
            "image_box.src": image,
        },
        "fileName": "meme_answer",
        "metadata": {"text_box.text": text},
    }
    res = requests.post(f"{RENDER_FORM_URL}/api/v2/render", json=body, headers=headers)
    print(res.json()["href"])
    return res.json()["href"]


class TaskResponse(BaseModel):
    code: int
    msg: str
    text: Optional[str] = None
    image: Optional[str] = None
    answer: Optional[str] = None

    def set_answer(self): ...


def solve(task_name: str) -> None:
    token_url: str = utils.get_token_url(task_name)
    token: str = utils.get_token(token_url)
    task_url: str = utils.get_task_url(token)
    task_obj = TaskResponse(**utils.get_task(task_url).json())
    url = get_meme(task_obj.image, task_obj.text)
    # task_obj.set_answer()

    utils.send_answer(token=token, answer=url)


if __name__ == "__main__":
    # utils.print_task(TASK_NAME)
    solve(TASK_NAME)
