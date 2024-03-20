import requests
from typing import Any

from settings import get_settings
from models import TokenRequest, TokenResponse, TaskResponse, AnswerRequest, AnswerResponse

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


def get_task(task_url: str) -> TaskResponse:
    res = requests.get(task_url)
    return TaskResponse(**res.json())


def send_answer(token: str, answer: Any) -> None:
    answer_url = f"{settings.task_url}/answer/{token}"
    data = AnswerRequest(answer=answer)
    res = requests.post(url=answer_url, data=data.model_dump_json())
    res_obj = AnswerResponse(**res.json())
    print(res_obj.msg) #todo: inny format
    print(res_obj.code)


def print_task(task_name: str) -> None:
    token_url: str = get_token_url(task_name)
    token: str = get_token(token_url)
    task_url: str = get_task_url(token)
    task_obj = get_task(task_url)
    print(task_obj.model_dump_json(indent=4))


def get_task_for_task_name(task_name: str) -> TaskResponse:
    token_url: str = get_token_url(task_name)
    token: str = get_token(token_url)
    task_url: str = get_task_url(token)
    return get_task(task_url)


