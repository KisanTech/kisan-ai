"""
Simple Market Data API
Only handles data retrieval and price updates
"""

from datetime import datetime

from fastapi import APIRouter, Body, HTTPException, Query, status
from pydantic import BaseModel

from app.constants import DateFormats
from app.services.market_service import market_service
from app.utils.logger import logger

router = APIRouter()


class MarketDataResponse(BaseModel):
    """Simple market data response"""

    success: bool
    data: list
    source: str
    state: str
    date: str
    total_records: int
    error: str | None = None


class PriceUpdateRequest(BaseModel):
    """Price update request"""

    state: str
    market: str
    commodity: str
    date: str  # YYYY-MM-DD format
    price: float
    updated_by: str = "api"


class PriceUpdateResponse(BaseModel):
    """Price update response"""

    success: bool
    message: str
    old_price: float | None = None
    new_price: float | None = None
    state: str
    market: str
    commodity: str
    date: str
    error: str | None = None


@router.get("/data", response_model=MarketDataResponse)
async def get_market_data(
    state: str = Query(..., description="State name (required)"),
    date: str | None = Query(
        None, description=f"Date in {DateFormats.ISO_DATE} format (defaults to today)"
    ),
    limit: int = Query(100, description="Number of records per page (default: 100, max: 1000)"),
    offset: int = Query(0, description="Number of records to skip (default: 0)"),
) -> MarketDataResponse:
    """
    Get market data for a specific state and date with pagination

    Supports pagination for large datasets. Use limit=1000 and iterate with offset
    to get all data for caching purposes.
    """
    try:
        # Validate pagination parameters
        if limit < 1 or limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Limit must be between 1 and 1000"
            )

        if offset < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Offset must be non-negative"
            )
        # Parse date if provided
        target_date = None
        if date:
            try:
                target_date = datetime.strptime(date, DateFormats.ISO_DATE).date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid date format. Use {DateFormats.ISO_DATE}",
                )

        result = await market_service.get_market_data(
            state=state, date=target_date, limit=limit, offset=offset
        )
        return MarketDataResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get market data", error=str(e), state=state, date=date)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Market data service temporarily unavailable",
        )


@router.put("/price", response_model=PriceUpdateResponse)
async def update_crop_price(request: PriceUpdateRequest = Body(...)) -> PriceUpdateResponse:
    """
    Update price for a specific crop in a specific market

    Updates the price for an existing crop record.
    The record must already exist in the database.
    """
    try:
        # Parse and validate date
        try:
            target_date = datetime.strptime(request.date, DateFormats.ISO_DATE).date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid date format. Use {DateFormats.ISO_DATE}",
            )

        # Validate price
        if request.price < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Price must be non-negative"
            )

        result = await market_service.update_crop_price(
            state=request.state,
            market=request.market,
            commodity=request.commodity,
            date=target_date,
            price=request.price,
            updated_by=request.updated_by,
        )

        return PriceUpdateResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update crop price", error=str(e), request=request.dict())
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Price update service temporarily unavailable",
        )
