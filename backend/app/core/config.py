import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings and configuration"""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Project Kisan"

    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT: str | None = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_APPLICATION_CREDENTIALS: str | None = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # Vertex AI Configuration
    VERTEX_AI_REGION: str = os.getenv("VERTEX_AI_REGION", "us-central1")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

    # Speech API Configuration
    SPEECH_LANGUAGE_CODE: str = os.getenv("SPEECH_LANGUAGE_CODE", "kn-IN")  # Kannada

    # External API Configuration
    MARKET_API_BASE_URL: str | None = os.getenv("MARKET_API_BASE_URL")
    MARKET_API_KEY: str | None = os.getenv("MARKET_API_KEY")

    # Development Settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    class Config:
        env_file = ".env"


settings = Settings()

# TODO: Add validation for required Google Cloud credentials
# TODO: Add configuration for specific market data sources
# TODO: Add configuration for government scheme APIs
