from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field, HttpUrl

from .config import Settings, settings
from .features import LiveFeatureExtractor
from .logging import configure_logging
from .model import LoadedModel, ModelNotAvailable, load_model
from .security import UnsafeUrl, normalize_url
from .web import LANDING_PAGE

logger = logging.getLogger(__name__)


class PredictionRequest(BaseModel):
    url: str = Field(min_length=3, max_length=2_048, examples=["https://example.com/login"])
    include_live_features: bool = False


class PredictionResponse(BaseModel):
    url: str
    label: str
    phishing_probability: float
    model_name: str
    model_version: str
    lexical_features: dict[str, float]
    live_features: dict[str, float | str | bool | None] | None = None
    enrichment_status: dict[str, str] | None = None
    enrichment_errors: dict[str, str] | None = None
    latency_ms: float


def create_app(config: Settings = settings, model: LoadedModel | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        configure_logging()
        app.state.model = model or load_model(config.model_path)
        app.state.extractor = LiveFeatureExtractor(config)
        yield

    app = FastAPI(title="Phishing Detection API", version="1.0.0", lifespan=lifespan)

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def landing_page() -> HTMLResponse:
        """Serve the interactive detector without changing the API contract."""
        return HTMLResponse(LANDING_PAGE)

    @app.exception_handler(UnsafeUrl)
    async def unsafe_url_handler(_: Request, error: UnsafeUrl) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(error)})

    @app.get("/healthz")
    def healthz(request: Request) -> dict[str, str]:
        current: LoadedModel = request.app.state.model
        return {"status": "ok", "model_version": current.model_version}

    @app.post("/predict", response_model=PredictionResponse)
    def predict(payload: PredictionRequest, request: Request) -> PredictionResponse:
        started = time.perf_counter()
        try:
            normalized = normalize_url(payload.url)
            normalized_url = normalized.geturl()
            current: LoadedModel = request.app.state.model
            label, probability, lexical = current.predict(normalized_url)
            result = PredictionResponse(
                url=normalized_url,
                label="phishing" if label else "legitimate",
                phishing_probability=round(probability, 6),
                model_name=current.model_name,
                model_version=current.model_version,
                lexical_features=lexical,
                latency_ms=0.0,
            )
            if payload.include_live_features:
                live = request.app.state.extractor.extract(normalized_url)
                result.live_features = live.values
                result.enrichment_status = live.statuses
                result.enrichment_errors = live.errors or None
            result.latency_ms = round((time.perf_counter() - started) * 1_000, 3)
            logger.info("prediction_complete", extra={"event": "prediction_complete", "url_host": normalized.hostname, "latency_ms": result.latency_ms})
            return result
        except UnsafeUrl:
            raise
        except Exception as error:
            logger.exception("prediction_failed", extra={"event": "prediction_failed", "error": type(error).__name__})
            raise HTTPException(status_code=500, detail="prediction could not be completed") from error

    return app


app = create_app()
