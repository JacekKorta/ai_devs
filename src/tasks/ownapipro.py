from src import utils
from src.settings import get_settings

TASK_NAME: str = "ownapipro"
settings = get_settings()


def solve(task_name: str) -> None:
    token_url: str = utils.get_token_url(task_name)
    token: str = utils.get_token(token_url)

    utils.send_answer(token=token, answer=settings.own_api_url)


if __name__ == "__main__":
    # utils.print_task(TASK_NAME)
    solve(TASK_NAME)
