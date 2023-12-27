from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from bridge_skillz_gpt.open_ai.extensions.context_filter import ContextFilter
from bridge_skillz_gpt.open_ai.openai_models import (
    OpenAICompletion,
    OpenAIMessage,
)
from bridge_skillz_gpt.server.chat.chat_router import ChatBody, chat_completion
from bridge_skillz_gpt.server.utils.auth import authenticated

completions_router = APIRouter(prefix="/v1", dependencies=[Depends(authenticated)])


class CompletionsBody(BaseModel):
    prompt: str
    system_prompt: str | None = None
    use_context: bool = False
    context_filter: ContextFilter | None = None
    include_sources: bool = True
    stream: bool = False

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": "How do you fry an egg?",
                    "system_prompt": "You are Bikram a BridgeSkillz ai assistant",
                    "stream": False,
                    "use_context": False,
                    "include_sources": False,
                }
            ]
        }
    }


@completions_router.post(
    "/completions",
    response_model=None,
    summary="Completion",
    responses={200: {"model": OpenAICompletion}},
    tags=["Contextual Completions"],
)
def prompt_completion(
    request: Request, body: CompletionsBody
) -> OpenAICompletion | StreamingResponse:
    messages = [OpenAIMessage(content=body.prompt, role="user")]
    # If system prompt is passed, create a fake message with the system prompt.
    if body.system_prompt:
        messages.insert(0, OpenAIMessage(content=body.system_prompt, role="system"))

    chat_body = ChatBody(
        messages=messages,
        use_context=body.use_context,
        stream=body.stream,
        include_sources=body.include_sources,
        context_filter=body.context_filter,
    )
    return chat_completion(request, chat_body)
