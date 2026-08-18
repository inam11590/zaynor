from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on application startup."""
    Base.metadata.create_all(bind=engine)
    yield


# ---------------------------------------------------------------------------
# Rate Limiter
# ---------------------------------------------------------------------------
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT] if settings.RATE_LIMIT_ENABLED else [],
    enabled=settings.RATE_LIMIT_ENABLED,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------------------
# In production, replace CORS_ORIGINS with only the real ZAYNOR domain(s),
# e.g. ["https://zaynor.com", "https://www.zaynor.com"].
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# API Routers
# ---------------------------------------------------------------------------
from app.api.auth import router as auth_router  # noqa: E402
from app.api.products import router as products_router  # noqa: E402
from app.api.customers import router as customers_router  # noqa: E402
from app.api.orders import router as orders_router  # noqa: E402
from app.api.reviews import router as reviews_router  # noqa: E402
from app.api.wishlist import router as wishlist_router  # noqa: E402
from app.api.coupons import router as coupons_router  # noqa: E402
from app.api.analytics import router as analytics_router  # noqa: E402

app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(products_router, prefix=settings.API_PREFIX)
app.include_router(customers_router, prefix=settings.API_PREFIX)
app.include_router(orders_router, prefix=settings.API_PREFIX)
app.include_router(reviews_router, prefix=settings.API_PREFIX)
app.include_router(wishlist_router, prefix=settings.API_PREFIX)
app.include_router(coupons_router, prefix=settings.API_PREFIX)
app.include_router(analytics_router, prefix=settings.API_PREFIX)


# ---------------------------------------------------------------------------
# Root & Health Endpoints
# ---------------------------------------------------------------------------
@app.get("/", tags=["General"])
def root():
    """Root endpoint — confirms the API is running."""
    return {"message": "ZAYNOR API is running"}


@app.get("/health", tags=["General"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
