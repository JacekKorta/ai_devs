from typing import List

from openai import OpenAI

from src.settings import get_settings

settings = get_settings()
client: OpenAI = OpenAI(api_key=settings.openai_api_key)


def is_flagged(data: List[str]) -> bool:
    response = client.moderations.create(input=data)
    return any(m.flagged for m in response.results)
