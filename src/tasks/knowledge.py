import json
from typing import Optional

import requests
from openai import OpenAI
from pydantic import BaseModel

from src import utils
from src.exceptions import StoppedByModeration
from src.openai_utils import is_flagged
from src.settings import get_settings

TASK_NAME: str = "knowledge"
settings = get_settings()
client: OpenAI = OpenAI(api_key=settings.openai_api_key)

"ISO 4217 standard"


def get_currency_rate(iso_code: str) -> float:
    api_url = f"http://api.nbp.pl/api/exchangerates/rates/A/{iso_code}/?format=json"
    response = requests.get(api_url)
    return response.json()["rates"][0]["mid"]


get_currency_rate_schema = {
    "type": "function",
    "function": {
        "name": "get_currency_rate",
        "description": "Get the current exchange rate for the country with the fallen ISO code 4217",
        "parameters": {
            "type": "object",
            "properties": {
                "iso_code": {
                    "type": "string",
                    "description": "Tree letters ISO 4217 standard",
                },
            },
        },
    },
}


def get_population(country_name: str) -> int:
    api_url = f"https://restcountries.com/v3.1/name/{country_name.lower()}"
    response = requests.get(api_url)
    return response.json()[0]["population"]


get_population_schema = {
    "type": "function",
    "function": {
        "name": "get_population",
        "description": "Get populations of a given country ",
        "parameters": {
            "type": "object",
            "properties": {
                "country_name": {
                    "type": "string",
                    "description": "country name, one word, lowercase",
                },
            },
        },
    },
}

actions = {"get_population": get_population, "get_currency_rate": get_currency_rate}


class TaskResponse(BaseModel):
    code: int
    msg: str
    question: Optional[str] = None
    answer: Optional[str] = None

    def set_answer(self):
        if is_flagged([self.question]):
            raise StoppedByModeration(self.question)
        tools = [get_population_schema, get_currency_rate_schema]
        messages = [{"role": "user", "content": self.question}]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
            tools=tools,
            tool_choice="auto",  # auto is default
        )
        response_message = response.choices[0].message
        if tool_calls := response_message.tool_calls:
            for call in tool_calls:
                function_name = call.function.name
                function_to_call = actions[function_name]
                function_kwargs = json.loads(call.function.arguments)
                print(
                    f"Function {function_name} will be call with kwargs: {function_kwargs}"
                )
                self.answer = function_to_call(**function_kwargs)
        else:
            self.answer = response_message.content


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
