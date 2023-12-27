from typing import Literal

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from bridge_skillz_gpt.open_ai.extensions.context_filter import ContextFilter
from bridge_skillz_gpt.server.chunks.chunks_service import Chunk, ChunksService
from bridge_skillz_gpt.server.utils.auth import authenticated

chunks_router = APIRouter(prefix="/v1", dependencies=[Depends(authenticated)])


class ChunksBody(BaseModel):
    text: str = Field(examples=["Q3 2023 sales"])
    context_filter: ContextFilter | None = None
    limit: int = 10
    prev_next_chunks: int = Field(default=0, examples=[2])


class ChunksResponse(BaseModel):
    object: Literal["list"]
    model: Literal["bridge-skillz-gpt"]
    data: list[Chunk]


@chunks_router.post("/chunks", tags=["Context Chunks"])
def chunks_retrieval(request: Request, body: ChunksBody) -> ChunksResponse:

    service = request.state.injector.get(ChunksService)
    results = service.retrieve_relevant(
        body.text, body.context_filter, body.limit, body.prev_next_chunks
    )
    return ChunksResponse(
        object="list",
        model="bridge-skillz-gpt",
        data=results,
    )
