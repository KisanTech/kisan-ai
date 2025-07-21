from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class MarketRecord(BaseModel):
    """Market price record with essential fields"""

    state: str
    district: str
    market: str
    commodity: str
    variety: str
    grade: str
    arrival_date: str
    min_price_rs: float = Field(ge=0)
    max_price_rs: float = Field(ge=0)
    modal_price_rs: float = Field(ge=0)
    currency: str = "INR"

    @field_validator("min_price_rs", "max_price_rs", "modal_price_rs")
    @classmethod
    def round_prices(cls, v: float) -> float:
        return round(v, 2)


class MarketDataMetadata(BaseModel):
    """Response metadata"""

    source: str
    state: str | None = None
    total_records: int = Field(ge=0)
    cache_age_hours: float | None = Field(None, ge=0)
    last_updated: str


class MarketPricesResponse(BaseModel):
    """Market prices API response"""

    prices: list[MarketRecord]
    metadata: MarketDataMetadata


class CacheRefreshResponse(BaseModel):
    """Cache refresh response"""

    status: str
    state: str
    records_cached: int = Field(ge=0)
    refreshed_at: str


class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: str
    service: str
    version: str
    environment: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class APIInfo(BaseModel):
    """Root API information"""

    message: str
    version: str
    features: list[str]
    environment: str
    docs: str
