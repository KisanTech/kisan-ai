"""Main FastAPI application entry point for Kisan AI"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.agent_invocation import router as agent_invocation_router
from app.api.v1.crop_diagnosis import router as crop_diagnosis_router
from app.api.v1.market_prices import router as market_router
from app.api.v1.speech import router as speech_router
from app.api.v1.translation import router as translation_router
from app.core.config import settings
from app.models.market import APIInfo, HealthCheckResponse
from app.utils.gcp.gcp_manager import gcp_manager
from app.utils.logger import logger

# Environment variables and credentials are loaded in app/__init__.py


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info(
        "Starting Kisan AI API", version=settings.APP_VERSION, environment=settings.ENVIRONMENT
    )

    try:
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

        # Initialize Google Cloud Platform services
        try:
            await gcp_manager.initialize()
        except Exception as gcp_error:
            logger.warning("Failed to initialize GCP services", error=str(gcp_error))

        # Market service is ready - no pre-loading needed
        logger.info("Market service initialized successfully")

        logger.info(
            "Kisan AI API startup complete",
            debug_mode=settings.DEBUG,
            cors_origins=len(settings.CORS_ORIGINS),
            has_market_api_key=bool(settings.DATA_GOV_API_KEY),
            gcp_project=settings.GOOGLE_CLOUD_PROJECT,
            firestore_db=settings.FIRESTORE_DATABASE,
        )

    except Exception as e:
        logger.error("Failed to start Kisan AI API", error=str(e), error_type=type(e).__name__)
        raise

    yield

    try:
        logger.info("Kisan AI API shutdown complete")
    except Exception as e:
        logger.error("Error during Kisan AI API shutdown", error=str(e))


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
            "Speech-to-Text with Google Chirp Model",
            "Multi-language Support (Hindi, English, Kannada, etc.)",
            "Simple Market Data Storage & Retrieval",
            "Data.gov.in API Integration",
            "Individual Price Updates",
            "Firestore Time-Series Storage",
            "TTL-based Data Cleanup",
            "Google Cloud Platform Integration",
            "Google Cloud Translation API",
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


app.include_router(agent_invocation_router, prefix="/api/v1", tags=["agent-invocation"])
app.include_router(market_router, prefix="/api/v1/market", tags=["market-data"])
app.include_router(crop_diagnosis_router, prefix="/api/v1/crop", tags=["crop-diagnosis"])
app.include_router(speech_router, prefix="/api/v1/speech", tags=["speech"])
app.include_router(translation_router, prefix="/api/v1/translation", tags=["translation"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
