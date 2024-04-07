from typing import Any, Dict, List

from openai import OpenAI

from src.settings import get_settings

settings = get_settings()
client: OpenAI = OpenAI(api_key=settings.openai_api_key)


def is_flagged(data: List[str]) -> bool:
    # todo: refactor, add dependency injection for client
    response = client.moderations.create(input=data)
    return any(m.flagged for m in response.results)


def ask_model(
    client: OpenAI,
    messages: List[Dict[str, Any]],
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.3,
) -> str:
    print(f"Make request to model, with messages = {messages}")
    response = client.chat.completions.create(
        temperature=temperature, model=model, messages=messages
    )  # todo: zamień na logi
    print(f"Model response {response.choices[0].message.content}")
    return response.choices[0].message.content
