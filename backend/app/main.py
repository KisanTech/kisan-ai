from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Project Kisan - AI Agricultural Assistant",
    description="Hackathon MVP for Google Agentic AI Day",
    version="0.1.0",
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Project Kisan API - Ready for Hackathon!",
        "features": [
            "Crop Disease Identification",
            "Voice Interface (Kannada)",
            "Market Price Display",
        ],
        "status": "MVP Development",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "project-kisan-api"}


# TODO: Import and include routers for the 3 core features
# from app.api.v1.crop_diagnosis import router as crop_router
# from app.api.v1.voice_interface import router as voice_router
# from app.api.v1.market_prices import router as market_router

# app.include_router(crop_router, prefix="/api/v1/crop", tags=["crop-diagnosis"])
# app.include_router(voice_router, prefix="/api/v1/voice", tags=["voice-interface"])
# app.include_router(market_router, prefix="/api/v1/market", tags=["market-prices"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
