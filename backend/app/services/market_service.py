"""
Market Data Service with Cache-First Strategy
Fetches all state data once, filters locally for better performance
"""

from datetime import datetime, timedelta

from app.constants import APIEndpoints, MarketData
from app.core.config import settings
from app.utils.api_client import data_gov_request
from app.utils.logger import log_latency, logger


class MarketDataCache:
    """In-memory cache for market data with configurable TTL"""

    def __init__(self, ttl_hours: int = 24):
        self._cache: dict[str, list[dict]] = {}
        self._last_updated: dict[str, datetime] = {}
        self._cache_ttl_hours = ttl_hours

    def is_expired(self, state: str) -> bool:
        """Check if cache is expired for a state"""
        if state not in self._last_updated:
            return True

        age = datetime.now() - self._last_updated[state]
        return age > timedelta(hours=self._cache_ttl_hours)

    def get(self, state: str) -> list[dict] | None:
        """Get cached data for a state"""
        if self.is_expired(state):
            return None
        return self._cache.get(state, [])

    def set(self, state: str, data: list[dict]):
        """Cache data for a state"""
        self._cache[state] = data
        self._last_updated[state] = datetime.now()
        logger.info("Market data cached", state=state, records=len(data))


class MarketService:
    """Market data service with intelligent caching"""

    def __init__(self):
        self._cache = MarketDataCache()

    @log_latency("get_commodity_prices")
    async def get_commodity_prices(
        self,
        commodity: str | None = None,
        state: str | None = None,
        market: str | None = None,
    ) -> dict:
        """Get current commodity prices (cache-first approach)"""

        target_state = state or MarketData.DEFAULT_STATE

        try:
            # Get data from cache or fetch fresh
            market_data = await self._get_state_data(target_state)

            if not market_data:
                logger.warning("No market data available", state=target_state)
                return self._get_fallback_data(commodity, target_state)

            # Filter the cached data locally
            filtered_data = self._filter_market_data(
                market_data, commodity=commodity, market=market
            )

            return {
                "prices": filtered_data,
                "metadata": {
                    "source": "Data.gov.in (Cached)",
                    "state": target_state,
                    "total_records": len(filtered_data),
                    "cache_age_hours": self._get_cache_age_hours(target_state),
                    "last_updated": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            logger.error("Failed to fetch market prices", error=str(e), state=target_state)
            return self._get_fallback_data(commodity, target_state)

    async def _get_state_data(self, state: str) -> list[dict]:
        """Get all market data for a state (cache-first)"""

        # Check cache first
        cached_data = self._cache.get(state)
        if cached_data is not None:
            logger.info("Using cached market data", state=state, records=len(cached_data))
            return cached_data

        # Cache miss - fetch fresh data
        logger.info("Cache miss, fetching fresh market data", state=state)
        return await self._fetch_fresh_state_data(state)

    @log_latency("fetch_fresh_state_data")
    async def _fetch_fresh_state_data(self, state: str) -> list[dict]:
        """Fetch all market data for a state from Data.gov.in"""

        if not settings.DATA_GOV_API_KEY:
            logger.warning("No Data.gov.in API key, skipping fresh data fetch")
            return []

        try:
            # Fetch ALL data for the state with proper pagination
            all_records = []
            offset = 0
            limit = MarketData.DEFAULT_BATCH_SIZE
            total_records = None

            while True:
                params = {
                    "format": "json",
                    "limit": str(limit),
                    "offset": str(offset),
                    "filters[state.keyword]": state,
                }

                response = await data_gov_request(
                    resource_id=APIEndpoints.DATA_GOV_MANDI_RESOURCE_ID, params=params
                )

                # Get current batch of records
                batch_records = response.get("records", [])
                all_records.extend(batch_records)

                # Track total for logging
                if total_records is None:
                    total_records = response.get("total", 0)

                logger.info(
                    "Fetched batch",
                    state=state,
                    batch_size=len(batch_records),
                    offset=offset,
                    total_fetched=len(all_records),
                    total_available=total_records,
                )

                # Stop if we got fewer records than requested (end of data)
                if len(batch_records) < limit:
                    break

                # Move to next batch
                offset += limit

                # Safety limit to prevent infinite loops
                max_records = getattr(
                    settings, "MAX_RECORDS_PER_STATE", MarketData.DEFAULT_MAX_RECORDS
                )
                if len(all_records) >= max_records:
                    logger.warning(
                        "Hit safety limit, stopping pagination",
                        state=state,
                        records_fetched=len(all_records),
                        max_allowed=max_records,
                    )
                    break

            # Process all records (convert paisa to rupees)
            processed_records = self._process_price_data(all_records)

            # Cache the processed data
            self._cache.set(state, processed_records)

            logger.info(
                "Fresh market data fetched and cached",
                state=state,
                total_available=total_records,
                total_fetched=len(all_records),
                cached_records=len(processed_records),
            )

            return processed_records

        except Exception as e:
            logger.error("Failed to fetch fresh market data", state=state, error=str(e))
            return []

    def _process_price_data(self, raw_records: list[dict]) -> list[dict]:
        """Process raw API data - convert paisa to rupees, standardize format"""

        processed = []
        for record in raw_records:
            try:
                # Convert paisa to rupees (divide by 100)
                min_price = float(record.get("min_price", 0)) / 100
                max_price = float(record.get("max_price", 0)) / 100
                modal_price = float(record.get("modal_price", 0)) / 100

                processed_record = {
                    "state": record.get("state", ""),
                    "district": record.get("district", ""),
                    "market": record.get("market", ""),
                    "commodity": record.get("commodity", ""),
                    "variety": record.get("variety", ""),
                    "grade": record.get("grade", ""),
                    "arrival_date": record.get("arrival_date", ""),
                    "min_price_rs": round(min_price, 2),
                    "max_price_rs": round(max_price, 2),
                    "modal_price_rs": round(modal_price, 2),  # Most common price
                    "currency": "INR",
                }
                processed.append(processed_record)

            except (ValueError, TypeError) as e:
                logger.warning("Failed to process price record", error=str(e), record=record)
                continue

        return processed

    def _filter_market_data(
        self, data: list[dict], commodity: str | None = None, market: str | None = None
    ) -> list[dict]:
        """Filter cached market data locally"""

        filtered = data.copy()

        # Filter by commodity (case-insensitive partial match)
        if commodity:
            commodity_str = str(commodity).lower()
            filtered = [
                record
                for record in filtered
                if commodity_str in record.get("commodity", "").lower()
            ]

        # Filter by market (case-insensitive partial match)
        if market:
            market_str = str(market).lower()
            filtered = [
                record for record in filtered if market_str in record.get("market", "").lower()
            ]

        return filtered

    def _get_cache_age_hours(self, state: str) -> float:
        """Get cache age in hours"""
        if state not in self._cache._last_updated:
            return 0

        age = datetime.now() - self._cache._last_updated[state]
        return round(age.total_seconds() / 3600, 2)

    @log_latency("refresh_cache")
    async def refresh_cache(self, state: str = MarketData.DEFAULT_STATE) -> dict:
        """Manually refresh cache for a state"""

        logger.info("Manual cache refresh requested", state=state)

        # Force fresh data fetch
        fresh_data = await self._fetch_fresh_state_data(state)

        return {
            "status": "cache_refreshed",
            "state": state,
            "records_cached": len(fresh_data),
            "refreshed_at": datetime.now().isoformat(),
        }

    def _get_fallback_data(self, commodity: str | None, state: str | None) -> dict:
        """Simple fallback when API is unavailable"""

        return {
            "prices": [],
            "metadata": {
                "source": "API Unavailable",
                "state": state or MarketData.DEFAULT_STATE,
                "total_records": 0,
                "last_updated": datetime.now().isoformat(),
                "error": "Unable to fetch market data",
            },
        }


# Global service instance
market_service = MarketService()
