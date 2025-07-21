"""
Market prices API endpoints with production-ready error handling
"""

from fastapi import APIRouter, HTTPException, Query, status

from app.constants import MarketData
from app.models.market import CacheRefreshResponse, MarketPricesResponse
from app.services.market_service import market_service
from app.utils.logger import logger

router = APIRouter()


@router.get("/current", response_model=MarketPricesResponse)
async def get_current_prices(
    crop: str | None = Query(None, description="Specific crop name"),
    market: str | None = Query(None, description="Market/Mandi name"),
    state: str | None = Query(MarketData.DEFAULT_STATE, description="State name"),
) -> MarketPricesResponse:
    """
    Get current market prices for crops

    Returns market price data with caching for performance.
    Defaults to {MarketData.DEFAULT_STATE} state if not specified.
    """
    try:
        result = await market_service.get_commodity_prices(
            commodity=crop, state=state, market=market
        )
        return MarketPricesResponse(**result)

    except Exception as e:
        logger.error(
            "Failed to fetch market prices", error=str(e), crop=crop, market=market, state=state
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Market data service temporarily unavailable",
        )


@router.post("/cache/refresh", response_model=CacheRefreshResponse)
async def refresh_market_cache(
    state: str = Query(MarketData.DEFAULT_STATE, description="State to refresh cache for"),
) -> CacheRefreshResponse:
    """
    Manually refresh market data cache for a state

    Forces a fresh fetch from Data.gov.in API and updates the cache.
    Use this when you need the latest data immediately.
    """
    try:
        result = await market_service.refresh_cache(state)
        return CacheRefreshResponse(**result)

    except Exception as e:
        logger.error("Failed to refresh cache", error=str(e), state=state)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cache refresh service temporarily unavailable",
        )
