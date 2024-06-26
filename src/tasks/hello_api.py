from pydantic import BaseModel

from src import utils

TASK_NAME: str = "helloapi"

utils.print_task(TASK_NAME)


class TaskResponse(BaseModel):
    code: int
    msg: str
    cookie: str


def solve(task_name: str) -> None:
    token_url: str = utils.get_token_url(task_name)
    token: str = utils.get_token(token_url)
    task_url: str = utils.get_task_url(token)
    task_obj = TaskResponse(**utils.get_task(task_url).json())
    utils.send_answer(token=token, answer=task_obj.cookie)


if __name__ == "__main__":
    solve(TASK_NAME)
