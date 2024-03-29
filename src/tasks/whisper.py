import os
import time
from typing import Optional

import requests
from openai import OpenAI
from openai.types.audio import Transcription
from pydantic import BaseModel

from src import utils
from src.settings import get_settings

TASK_NAME: str = "whisper"
settings = get_settings()
client: OpenAI = OpenAI(api_key=settings.openai_api_key)

FILE_URL = "https://tasks.aidevs.pl/data/mateusz.mp3"
BASE_FILE_PATH = "tasks/task_data/"


class TaskResponse(BaseModel):
    code: int
    msg: str
    answer: Optional[Transcription] = None

    def set_answer(self, path: str):
        with open(path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", file=audio_file, response_format="text"
            )
            self.answer = transcription


def add_time_stamp(filename: str) -> str:
    name, extension = os.path.splitext(filename)
    return f"{name}{time.time_ns()}{extension}"


def get_file(url: str) -> str:
    local_filename = add_time_stamp(url.split("/")[-1])
    path = os.path.join(BASE_FILE_PATH, local_filename)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return path


def solve(task_name: str) -> None:
    token_url: str = utils.get_token_url(task_name)
    token: str = utils.get_token(token_url)
    task_url: str = utils.get_task_url(token)
    task_obj = TaskResponse(**utils.get_task(task_url).json())
    file_name = get_file(FILE_URL)
    task_obj.set_answer(file_name)
    utils.send_answer(token=token, answer=task_obj.answer)


if __name__ == "__main__":
    # utils.print_task(TASK_NAME)
    solve(TASK_NAME)
