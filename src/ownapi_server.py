import json
import logging
import sys
from typing import Dict, List

from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel
from serpapi import GoogleSearch
from settings import get_settings

settings = get_settings()
client: OpenAI = OpenAI(api_key=settings.openai_api_key)

app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(levelname)s: %(name)s: %(message)s")
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)


get_answer_schema = {
    "type": "function",
    "function": {
        "name": "get_answer",
        "description": "Reply briefly for user question",
        "parameters": {
            "type": "object",
            "properties": {
                "reply": {
                    "type": "string",
                    "description": "Answer for the user question",
                },
            },
        },
    },
}


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    reply: str


db = []


@app.post("/")
def answer(question: QuestionRequest):
    logger.info(question.json())
    db.append(question)
    messages = []
    if db:
        messages.append(
            {
                "role": "system",
                "content": f"if it possible, to answer use this context: {db}",
            }
        )

    messages.append({"role": "user", "content": question.question})
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages,
        tools=[get_answer_schema],
        tool_choice="auto",  # auto is default
    )
    response_message = response.choices[0].message
    if tool_calls := response_message.tool_calls:
        model_answer = tool_calls[0].function.arguments
        logger.info(f"Model answer: {model_answer}")
        return json.loads(model_answer)


@app.post("/search")
def search(question: QuestionRequest):
    logger.info(question.json())
    search_results = make_query(question.question)
    logger.info("Search results received")
    context = get_context(search_results.get("organic_results"))
    logger.info(f"Context received: {context}")
    logger.info("Asking LLM")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {
                "role": "user",
                "content": "IMPORTANT RULE: as a reply only return the full url",
            },
            {
                "role": "user",
                "content": f"Use the data from the attached context to answer the question:{context}\n###Question:\n",
            },
            {"role": "user", "content": question.question},
        ],
        tools=[get_answer_schema],
        tool_choice="auto",  # auto is default
    )
    response_message = response.choices[0].message
    if tool_calls := response_message.tool_calls:
        model_answer = tool_calls[0].function.arguments
        logger.info(f"Model answer: {model_answer}")
        return json.loads(model_answer)
    return AnswerResponse(reply=question.question)


def make_query(query: str) -> dict:
    params = {
        "api_key": settings.serp_api_key,
        "engine": "google",
        "q": query,
        "location": "Warsaw, Poland",
        "google_domain": "google.com",
        "gl": "pl",
        "hl": "pl",
    }
    results = GoogleSearch(params)
    return results.get_dict()


def get_context(organic_results: List[Dict]) -> str:
    context = ""
    for res in organic_results:
        context += f"\n{res['title']}\n{res['snippet']}\n{res['link']}\n###"
    return context
