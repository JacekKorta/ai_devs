import os
from typing import Any, Optional
from uuid import uuid4

from langchain_community.document_loaders import JSONLoader
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from src import utils
from src.exceptions import StoppedByModeration
from src.openai_utils import is_flagged
from src.settings import get_settings

TASK_NAME: str = "search"
COLLECTION_NAME = "arch_ai_devs"
DATA_PATH = "tasks/task_data/archiwum_aidevs.json"
settings = get_settings()
client: OpenAI = OpenAI(api_key=settings.openai_api_key)


class TaskResponse(BaseModel):
    code: int
    msg: str
    question: Optional[str] = None
    answer: Optional[Any] = None

    def set_answer(self):
        if is_flagged([self.question]):
            raise StoppedByModeration(self.question)

        embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
        qdrant_client = QdrantClient(url=settings.qdrant_url)
        create_collection(qdrant_client, COLLECTION_NAME)
        populate_qdrant_db(qdrant_client, embeddings, COLLECTION_NAME, DATA_PATH)
        print("Question embedding")
        query_embedding = embeddings.embed_query(self.question)

        print("question searching")
        search = qdrant_client.search(
            collection_name=COLLECTION_NAME, query_vector=query_embedding
        )
        if search:
            print(search[0].payload["content"])
            print(search[0].payload["url"])
            self.answer = search[0].payload["url"]  # todo: add Pydantic model
        else:
            print("There is no answer for this question")


def solve(task_name: str) -> None:
    token_url: str = utils.get_token_url(task_name)
    token: str = utils.get_token(token_url)
    task_url: str = utils.get_task_url(token)
    task_obj = TaskResponse(**utils.get_task(task_url).json())
    task_obj.set_answer()

    utils.send_answer(token=token, answer=task_obj.answer)


def create_collection(client: QdrantClient, collection_name: str) -> bool:
    """Returns True if collection was created, otherwise returns False"""

    collections = client.get_collections()
    print(f"Available collections: {collections}")
    indexed = [col for col in collections.collections if col.name == COLLECTION_NAME]
    print(f"Indexed collections: {indexed}")
    if not indexed:
        print(f"Creating collection {COLLECTION_NAME}")
        client.create_collection(
            COLLECTION_NAME,
            vectors_config=VectorParams(
                size=1536, distance=Distance.COSINE, on_disk=True
            ),
        )
        return True
    return False


def populate_qdrant_db(
    client: QdrantClient,
    embeddings: OpenAIEmbeddings,
    collection_name: str,
    data_path: str,
):
    # todo: make more generic

    collection_info = client.get_collection(collection_name)
    if not collection_info.points_count:
        print(f"loading file: {os.path.basename(data_path)}")
        title_loader = JSONLoader(data_path, jq_schema=".[].title")
        info_loader = JSONLoader(data_path, jq_schema=".[].info")
        url_loader = JSONLoader(data_path, jq_schema=".[].url")
        info_data = info_loader.load()
        title_data = title_loader.load()
        url_data = url_loader.load()

        print("Concatenate titles and info")
        lc_data = []
        for inf_d, title_d, url_d in zip(info_data, title_data, url_data):
            title_d.page_content += f" {inf_d.page_content}"
            title_d.metadata.update(
                source=COLLECTION_NAME,
                content=title_d.page_content,
                uuid=str(uuid4()),
                url=url_d.page_content,
            )
            lc_data.append(title_d)

        [
            document.metadata.update(
                source=COLLECTION_NAME, content=document.page_content, uuid=str(uuid4())
            )
            for document in lc_data
        ]
        points = []
        print("Adding embeddings")
        for document in lc_data:
            embedding = embeddings.embed_documents([document.page_content])[0]
            points.append(
                PointStruct(
                    id=document.metadata["uuid"],
                    payload=document.metadata,
                    vector=embedding,
                )
            )
        print("Updating qdrant DB")
        client.upsert(COLLECTION_NAME, points=points)


if __name__ == "__main__":
    # utils.print_task(TASK_NAME)
    solve(TASK_NAME)
