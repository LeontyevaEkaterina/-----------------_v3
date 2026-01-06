"""FastAPI entrypoint for Chat with Neural Networks backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .api import routes_auth, routes_users, routes_chats, routes_models, routes_stream


settings = get_settings()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.project_name,
        version="0.1.0",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_prefix = settings.api_v1_prefix

    app.include_router(routes_auth.router, prefix=api_prefix)
    app.include_router(routes_users.router, prefix=api_prefix)
    app.include_router(routes_chats.router, prefix=api_prefix)
    app.include_router(routes_models.router, prefix=api_prefix)
    app.include_router(routes_stream.router, prefix=api_prefix)

    @app.get(f"{api_prefix}/health", tags=["health"])
    async def healthcheck() -> dict:
        """Basic healthcheck endpoint."""
        return {"status": "ok"}

    return app


app = create_app()


