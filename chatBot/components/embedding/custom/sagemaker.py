# mypy: ignore-errors
import json
from typing import Any

import boto3
from llama_index.embeddings.base import BaseEmbedding
from pydantic import Field, PrivateAttr


class SagemakerEmbedding(BaseEmbedding):

    endpoint_name: str = Field(description="")

    _boto_client: Any = boto3.client(
        "sagemaker-runtime",
    )  # TODO make it an optional field

    _async_not_implemented_warned: bool = PrivateAttr(default=False)

    @classmethod
    def class_name(cls) -> str:
        return "SagemakerEmbedding"

    def _async_not_implemented_warn_once(self) -> None:
        if not self._async_not_implemented_warned:
            print("Async embedding not available, falling back to sync method.")
            self._async_not_implemented_warned = True

    def _embed(self, sentences: list[str]) -> list[list[float]]:
        request_params = {
            "inputs": sentences,
        }

        resp = self._boto_client.invoke_endpoint(
            EndpointName=self.endpoint_name,
            Body=json.dumps(request_params),
            ContentType="application/json",
        )

        response_body = resp["Body"]
        response_str = response_body.read().decode("utf-8")
        response_json = json.loads(response_str)

        return response_json["vectors"]

    def _get_query_embedding(self, query: str) -> list[float]:
        """Get query embedding."""
        return self._embed([query])[0]

    async def _aget_query_embedding(self, query: str) -> list[float]:
        # Warn the user that sync is being used
        self._async_not_implemented_warn_once()
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> list[float]:
        # Warn the user that sync is being used
        self._async_not_implemented_warn_once()
        return self._get_text_embedding(text)

    def _get_text_embedding(self, text: str) -> list[float]:
        """Get text embedding."""
        return self._embed([text])[0]

    def _get_text_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Get text embeddings."""
        return self._embed(texts)
