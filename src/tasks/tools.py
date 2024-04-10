import json
from datetime import datetime
from typing import Optional

from openai import OpenAI
from pydantic import BaseModel

from src import utils
from src.exceptions import StoppedByModeration
from src.openai_utils import is_flagged
from src.settings import get_settings

TASK_NAME: str = "tools"
settings = get_settings()
client: OpenAI = OpenAI(api_key=settings.openai_api_key)
TODAY_STR = datetime.today().strftime("%Y-%m-%d")


def select_action_tool(tool: str, desc: str, date: Optional[str] = None) -> None:
    # dummy function
    pass


select_action_tool_schema = {
    "type": "function",
    "function": {
        "name": "select_action_tool",
        "description": "select action (Calendar|ToDo) depend of user query, add date if Calendar."
        " Fact: today is {today}".format(today=TODAY_STR),
        "parameters": {
            "type": "object",
            "properties": {
                "tool": {
                    "type": "string",
                    "description": "Tool name depending on the query provided by the user",
                    "enum": ["Calendar", "ToDo"],
                },
                "desc": {
                    "type": "string",
                    "description": "Task description",
                },
                "date": {
                    "type": "string",
                    "description": "Optional field. Used only when tool=Calendar. Date format: YYYY-MM-DD",
                },
            },
            "required": ["tool", "desc"],
        },
    },
}


class TaskResponse(BaseModel):
    code: int
    msg: str
    question: Optional[str] = None
    answer: Optional[str] = None

    def set_answer(self):
        if is_flagged([self.question]):
            raise StoppedByModeration(self.question)

        print(f"Question is: {self.question}")
        messages = [{"role": "user", "content": self.question}]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
            tools=[select_action_tool_schema],
            tool_choice="auto",  # auto is default
        )
        response_message = response.choices[0].message
        if tool_calls := response_message.tool_calls:
            model_answer = tool_calls[0].function.arguments
            print(f"Model answer: {model_answer}")
            self.answer = json.loads(model_answer)


def solve(task_name: str) -> None:
    token_url: str = utils.get_token_url(task_name)
    token: str = utils.get_token(token_url)
    task_url: str = utils.get_task_url(token)
    task_obj = TaskResponse(**utils.get_task(task_url).json())
    task_obj.set_answer()

    utils.send_answer(token=token, answer=task_obj.answer)


if __name__ == "__main__":
    # utils.print_task(TASK_NAME)
    solve(TASK_NAME)
