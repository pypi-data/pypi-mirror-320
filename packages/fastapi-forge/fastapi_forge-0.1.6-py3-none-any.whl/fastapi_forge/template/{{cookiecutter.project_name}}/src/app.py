from loguru import logger
from settings import settings

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from routes import base_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan."""

    yield


def get_app() -> FastAPI:
    """Get FastAPI app."""

    logger.info(
        settings.model_dump_json(indent=2),
    )

    app = FastAPI(lifespan=lifespan)
    app.include_router(base_router)
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:get_app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        reload=settings.reload,
        lifespan="on",
        factory=True,
    )
