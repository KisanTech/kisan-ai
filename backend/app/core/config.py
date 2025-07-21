"""Application configuration settings"""

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Project Kisan application settings"""

    # App Info
    APP_NAME: str = Field(default="Project Kisan API", description="Application name")
    APP_VERSION: str = Field(default="0.1.0", description="Application version")
    ENVIRONMENT: str = Field(default="dev", description="Environment (dev/staging/prod)")
    DEBUG: bool = Field(default=False, description="Enable debug mode")

    # API Configuration
    API_V1_STR: str = Field(default="/api/v1", description="API v1 prefix")
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")

    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT: str = Field(default="", description="Google Cloud project ID")
    GOOGLE_APPLICATION_CREDENTIALS: str = Field(
        default="", description="Path to GCP service account key"
    )

    # Vertex AI Configuration
    VERTEX_AI_REGION: str = Field(default="us-central1", description="Vertex AI region")
    GEMINI_MODEL: str = Field(default="gemini-2.0-flash-exp", description="Gemini model version")

    # Speech API Configuration
    SPEECH_LANGUAGE_CODE: str = Field(
        default="kn-IN", description="Speech recognition language (Kannada)"
    )

    # Indian Government APIs
    DATA_GOV_API_KEY: str = Field(default="", description="Data.gov.in API key for market data")

    # CORS Configuration
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://localhost:8000",
        description="Comma-separated list of allowed CORS origins",
    )

    # Cache Configuration
    CACHE_TTL_SECONDS: int = Field(default=3600, description="Cache TTL in seconds (1 hour)")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="API rate limit per minute")

    @computed_field
    @property
    def CORS_ORIGINS(self) -> list[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "env_prefix": "",
        "extra": "ignore",  # Ignore extra env vars
    }


# Create settings instance
settings = Settings()
