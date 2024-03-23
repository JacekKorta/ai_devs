import utils

TASK_NAME: str = ""

utils.print_task(TASK_NAME)


def solve(task_name: str) -> None:
    token_url: str = utils.get_token_url(task_name)
    token: str = utils.get_token(token_url)
    task_url: str = utils.get_task_url(token)
    task_obj = utils.get_task(task_url)
    utils.send_answer(token=token, answer=XXX)


if __name__ == "__main__":
    solve(TASK_NAME)