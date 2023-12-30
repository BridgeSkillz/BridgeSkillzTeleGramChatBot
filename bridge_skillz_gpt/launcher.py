"""Bridge Skillz FastAPI app creation, logger configuration and main API routes."""
import logging

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from injector import Injector

from bridge_skillz_gpt.server.chat.chat_router import chat_router
from bridge_skillz_gpt.server.chunks.chunks_router import chunks_router
from bridge_skillz_gpt.server.completions.completions_router import completions_router
from bridge_skillz_gpt.server.embeddings.embeddings_router import embeddings_router
from bridge_skillz_gpt.server.health.health_router import health_router
from bridge_skillz_gpt.server.ingest.ingest_router import ingest_router
from bridge_skillz_gpt.settings.settings import Settings
from bridge_skillz_gpt.server.ui.ui_router import ui_router
from bridge_skillz_gpt.server.ui.ui_router import favicon_router

logger = logging.getLogger(__name__)


def create_app(root_injector: Injector) -> FastAPI:

    # Start the API
    async def bind_injector_to_request(request: Request) -> None:
        request.state.injector = root_injector

    app = FastAPI(redoc_url=None, docs_url=None, dependencies=[
                  Depends(bind_injector_to_request)])

    app.include_router(completions_router)
    app.include_router(chat_router)
    app.include_router(chunks_router)
    app.include_router(ingest_router)
    app.include_router(embeddings_router)
    app.include_router(health_router)
    app.include_router(ui_router)
    app.include_router(favicon_router)

    settings = root_injector.get(Settings)
    if settings.server.cors.enabled:
        logger.debug("Setting up CORS middleware")
        app.add_middleware(
            CORSMiddleware,
            allow_credentials=settings.server.cors.allow_credentials,
            allow_origins=settings.server.cors.allow_origins,
            allow_origin_regex=settings.server.cors.allow_origin_regex,
            allow_methods=settings.server.cors.allow_methods,
            allow_headers=settings.server.cors.allow_headers,
        )

    return app
