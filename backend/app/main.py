from fastapi import FastAPI

from app.presentation.api.router import api_router
from app.presentation.ws.router import ws_router


def create_application() -> FastAPI:
    app = FastAPI(
        title="CS-Icebreaker Hub API",
        version="0.1.0",
        description="Phase 1 backend skeleton with Clean Architecture boundaries.",
    )
    app.include_router(api_router, prefix="/api")
    app.include_router(ws_router, prefix="/ws")
    return app


app = create_application()
