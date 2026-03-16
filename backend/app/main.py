"""
FastAPI application entry point.

Initialises the app, registers middleware, mounts all API routers and defines
the lifespan context (startup / shutdown hooks).
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.database import close_db, init_db
from app.middleware.audit_middleware import AuditMiddleware
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.rate_limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Routers
from app.routers import (
    admin,
    analysis,
    assessment,
    auth,
    chat,
    mentorship,
    prediction,
    roadmap,
    users,
)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Run startup tasks before yield and shutdown tasks after."""
    await init_db()
    yield
    await close_db()


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# Middleware (outermost → innermost)
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)
app.add_middleware(AuditMiddleware)
app.add_middleware(AuthMiddleware)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

PREFIX = settings.api_v1_prefix

app.include_router(auth.router, prefix=PREFIX)
app.include_router(users.router, prefix=PREFIX)
app.include_router(assessment.router, prefix=PREFIX)
app.include_router(prediction.router, prefix=PREFIX)
app.include_router(analysis.router, prefix=PREFIX)
app.include_router(roadmap.router, prefix=PREFIX)
app.include_router(mentorship.router, prefix=PREFIX)
app.include_router(chat.router, prefix=PREFIX)
app.include_router(admin.router, prefix=PREFIX)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["health"])
async def health_check():
    """Liveness probe – returns 200 OK when the service is running."""
    from app.database import check_db_connection

    db_ok = await check_db_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "version": settings.APP_VERSION,
        "database": "connected" if db_ok else "unavailable",
    }


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {"message": f"Welcome to {settings.APP_NAME}", "version": settings.APP_VERSION}
