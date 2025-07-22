"""Main FastAPI application entry point for Project Kisan"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.crop_diagnosis import router as crop_diagnosis_router
from app.api.v1.market_prices import router as market_router
from app.constants import MarketData
from app.core.config import settings
from app.models.market import APIInfo, HealthCheckResponse
from app.services.market_service import market_service
from app.utils.logger import logger

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info(
        "Starting Project Kisan API", version=settings.APP_VERSION, environment=settings.ENVIRONMENT
    )

    try:
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

        # Pre-load market data cache for Karnataka (startup optimization)
        if settings.DATA_GOV_API_KEY:
            try:
                logger.info(f"Pre-loading market data cache for {MarketData.DEFAULT_STATE}")
                await market_service.refresh_cache(MarketData.DEFAULT_STATE)
            except Exception as cache_error:
                logger.warning("Failed to pre-load market cache", error=str(cache_error))

        logger.info(
            "Project Kisan API startup complete",
            debug_mode=settings.DEBUG,
            cors_origins=len(settings.CORS_ORIGINS),
            has_market_api_key=bool(settings.DATA_GOV_API_KEY),
        )

    except Exception as e:
        logger.error("Failed to start Project Kisan API", error=str(e), error_type=type(e).__name__)
        raise

    yield

    try:
        logger.info("Project Kisan API shutdown complete")
    except Exception as e:
        logger.error("Error during Project Kisan API shutdown", error=str(e))


# Create FastAPI app with lifespan management
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Agricultural Assistant for Hackathon MVP",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=APIInfo)
async def root() -> APIInfo:
    """Root endpoint with API information"""
    logger.info("Root endpoint accessed")
    return APIInfo(
        message=f"{settings.APP_NAME} - Ready for Hackathon!",
        version=settings.APP_VERSION,
        features=[
            "Market Price Display",
            "Crop Disease Diagnosis",
        ],
        environment=settings.ENVIRONMENT,
        docs="/docs",
    )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )


app.include_router(market_router, prefix="/api/v1/market", tags=["market-prices"])
app.include_router(crop_diagnosis_router, prefix="/api/v1/crop", tags=["crop-diagnosis"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
