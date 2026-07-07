from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logging import setup_logging
from db.mongodb import connect_db, disconnect_db

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await disconnect_db()


if settings.sentry_dsn:
    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=0.1,
        environment=settings.app_env,
    )

app = FastAPI(
    title="Krishi Sahayak — AI Agriculture Assistant",
    version="1.0.0",
    description="LangGraph-powered multi-agent platform for Indian farmers",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
from routers.auth import router as auth_router
from routers.farmers import router as farmers_router
from routers.chat import router as chat_router
from routers.crops import router as crops_router
from routers.disease import router as disease_router
from routers.weather import router as weather_router
from routers.market import router as market_router
from routers.schemes import router as schemes_router
from routers.soil import router as soil_router
from routers.notifications import router as notifications_router
from routers.admin import router as admin_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(farmers_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(crops_router, prefix="/api/v1")
app.include_router(disease_router, prefix="/api/v1")
app.include_router(weather_router, prefix="/api/v1")
app.include_router(market_router, prefix="/api/v1")
app.include_router(schemes_router, prefix="/api/v1")
app.include_router(soil_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
