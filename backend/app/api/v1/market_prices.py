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


class FilteredMarketDataResponse(BaseModel):
    """Filtered market data response for Agent V3"""

    success: bool
    data: list
    total_records: int
    filters_applied: dict
    date_range: dict | None = None
    error: str | None = None


class PriceUpdateRequest(BaseModel):
    """Price update request"""

    state: str
    market: str
    commodity: str
    price: float
    date: str | None = None


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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve market data",
        )


@router.get("/filtered-data", response_model=FilteredMarketDataResponse)
async def get_filtered_market_data(
    state: str = Query(..., description="State name (required)"),
    commodity: str | None = Query(None, description="Commodity/crop name (optional)"),
    market: str | None = Query(None, description="Market name (optional)"),
    start_date: str | None = Query(
        None, description=f"Start date in {DateFormats.ISO_DATE} format (optional)"
    ),
    end_date: str | None = Query(
        None, description=f"End date in {DateFormats.ISO_DATE} format (optional)"
    ),
    limit: int = Query(1000, description="Number of records to return (default: 1000, max: 5000)"),
) -> FilteredMarketDataResponse:
    """
    Get filtered market data for Market Agent V3

    Supports filtering by:
    - state (required)
    - commodity (optional) - filters by crop/commodity name
    - market (optional) - filters by specific market
    - start_date & end_date (optional) - date range filtering

    If no date range is provided, returns data from the last 60 days (default for Agent V3).
    Optimized for agent queries with smart filtering and higher limits.
    """
    try:
        # Validate pagination parameters
        if limit < 1 or limit > 5000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Limit must be between 1 and 5000"
            )

        # Parse date range if provided
        parsed_start_date = None
        parsed_end_date = None

        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, DateFormats.ISO_DATE).date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid start_date format. Use {DateFormats.ISO_DATE}",
                )

        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, DateFormats.ISO_DATE).date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid end_date format. Use {DateFormats.ISO_DATE}",
                )

        # Validate date range
        if parsed_start_date and parsed_end_date and parsed_start_date > parsed_end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be before or equal to end_date",
            )

        result = await market_service.get_filtered_market_data(
            state=state,
            commodity=commodity,
            market=market,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            limit=limit,
        )

        return FilteredMarketDataResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get filtered market data",
            error=str(e),
            state=state,
            commodity=commodity,
            market=market,
            start_date=start_date,
            end_date=end_date,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve filtered market data",
        )


@router.get("/bulk-data", response_model=dict)
async def get_bulk_market_data(
    date: str | None = Query(
        None, description=f"Date in {DateFormats.ISO_DATE} format (defaults to today)"
    ),
    states: str | None = Query(
        None,
        description="Comma-separated state names (e.g., 'Karnataka,Tamil Nadu,Punjab'). If not provided, returns all states.",
    ),
    limit: int = Query(1000, description="Number of records per page (default: 1000, max: 3000)"),
    offset: int = Query(0, description="Number of records to skip (default: 0)"),
) -> dict:
    """
    Get market data for multiple states or all states for a specific date with pagination.

    This endpoint is optimized for bulk data loading and cache initialization.
    Returns data organized by state for easy processing.

    Examples:
    - /bulk-data?date=2025-01-27  (all states for this date)
    - /bulk-data?date=2025-01-27&states=Karnataka,Tamil Nadu  (specific states)
    - /bulk-data  (all states for today)
    """
    try:
        # Validate pagination parameters
        if limit < 1 or limit > 3000:  # Higher limit for bulk operations
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Limit must be between 1 and 3000"
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

        # Parse states if provided
        target_states = None
        if states:
            target_states = [state.strip() for state in states.split(",")]
            # Validate state names (optional - you can add validation here)

        result = await market_service.get_bulk_market_data(
            date=target_date, states=target_states, limit=limit, offset=offset
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get bulk market data", error=str(e), date=date, states=states)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bulk market data service temporarily unavailable",
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
