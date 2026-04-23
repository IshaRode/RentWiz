"""
RentWiz – FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.services.prediction import load_model

# API routers
from app.api.v1 import predict, analyze, deals, insights

# ─── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# ─── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 RentWiz API starting up…")
    load_model()          # Load ML model once at startup
    yield
    logger.info("🛑 RentWiz API shutting down…")


# ─── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered rental deal finder API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ───────────────────────────────────────────────────────────────────
app.include_router(predict.router,   prefix="/api/v1", tags=["Prediction"])
app.include_router(analyze.router,   prefix="/api/v1", tags=["Analysis"])
app.include_router(deals.router,     prefix="/api/v1", tags=["Deals"])
app.include_router(insights.router,  prefix="/api/v1", tags=["Insights"])


# ─── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    from app.services.prediction import _model
    return {
        "status": "ok",
        "version": settings.app_version,
        "model_loaded": _model is not None,
    }


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to RentWiz API", "docs": "/docs"}
