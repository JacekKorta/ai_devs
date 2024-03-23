import pprint
from typing import Any

import requests

from .models import AnswerRequest, TokenRequest, TokenResponse
from .settings import get_settings

settings = get_settings()


def get_token_url(task_name: str) -> str:
    return f"{settings.task_url}/token/{task_name}"


def get_token(token_url: str) -> str:
    data = TokenRequest(apikey=settings.api_key)
    res = requests.post(url=token_url, data=data.model_dump_json())
    token_resp_obj = TokenResponse(**res.json())
    return token_resp_obj.token


def get_task_url(token: str) -> str:
    return f"{settings.task_url}/task/{token}"


def get_task(task_url: str) -> requests.Response:
    return requests.get(task_url)


def send_answer(token: str, answer: Any) -> None:
    headers = {"Content-type": "application/json"}
    answer_url = f"{settings.task_url}/answer/{token}"
    data = AnswerRequest(answer=answer)
    res = requests.post(url=answer_url, headers=headers, json=data.model_dump())
    pprint.pprint(res.json())


def print_task(task_name: str) -> None:
    token_url: str = get_token_url(task_name)
    token: str = get_token(token_url)
    task_url: str = get_task_url(token)
    task_data = get_task(task_url).json()
    pprint.pprint(task_data)


def get_task_for_task_name(task_name: str) -> requests.Response:
    token_url: str = get_token_url(task_name)
    token: str = get_token(token_url)
    task_url: str = get_task_url(token)
    return get_task(task_url)
