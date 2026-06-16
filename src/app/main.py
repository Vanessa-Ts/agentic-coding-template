import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator


from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.exceptions import CatalogueError
from app.routes.agents import router as agents_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown lifecycle hook."""
    logger.info(
        "Starting %s v%s [%s]",
        settings.app_name,
        settings.version,
        settings.environment,
    )
    yield
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

_UI_DIR = Path(__file__).resolve().parent / "ui"
app.mount("/static", StaticFiles(directory=_UI_DIR), name="static")
templates = Jinja2Templates(directory=_UI_DIR)

app.include_router(agents_router, prefix="/api")


@app.exception_handler(CatalogueError)
async def catalogue_error_handler(
    request: Request, exc: CatalogueError
) -> JSONResponse:
    logger.exception("Catalogue error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Configuration error"})


# --Health--
@app.get("/health/live", response_model=None, status_code=200)
async def liveness() -> JSONResponse:
    """Liveness probe — process is running."""
    return JSONResponse({"status": "ok"})


@app.get("/health/ready", response_model=None, status_code=200)
async def readiness() -> JSONResponse:
    """Readiness probe — add dependency checks here."""
    return JSONResponse({"status": "ok"})


# --Routes--
@app.get("/", response_model=None, status_code=200)
async def index(request: Request) -> Response:
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "app_name": settings.app_name,
            "version": settings.version,
            "environment": settings.environment,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # noqa: S104
        port=8000,
        reload=settings.environment == "development",
    )
