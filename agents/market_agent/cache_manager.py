"""
Market Data Cache Manager
========================

Intelligent caching system that loads all market data at startup using paginated API calls,
then serves data locally without repeated API calls. Perfect for trend analysis.

Features:
- Startup data loading with pagination
- In-memory caching for fast access
- Smart filtering and querying
- Background refresh capability
- Memory-efficient data structures
"""

import asyncio
import logging
import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp

# Setup logging
logger = logging.getLogger(__name__)

# Backend API configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL")


class MarketDataCache:
    def __init__(self):
        self.cache: Dict[str, Dict[str, List[Dict[str, Any]]]] = defaultdict(
            lambda: defaultdict(list)
        )
        # Structure: cache[state][date] = [records...]

        self.metadata = {
            "last_updated": None,
            "total_records": 0,
            "states_loaded": set(),
            "date_range": {"start": None, "end": None},
            "loading_status": "not_started",  # not_started, loading, loaded, error
        }

        self.target_states = ["Karnataka", "Tamil Nadu", "Punjab"]
        self.load_lock = asyncio.Lock()

    async def initialize(self) -> bool:
        """Initialize cache by loading all historical data at startup"""
        async with self.load_lock:
            if self.metadata["loading_status"] == "loaded":
                logger.info("Cache already loaded")
                return True

            if self.metadata["loading_status"] == "loading":
                logger.info("Cache loading already in progress")
                return False

            self.metadata["loading_status"] = "loading"
            logger.info("🚀 Starting market data cache initialization...")

            try:
                total_loaded = 0

                for state in self.target_states:
                    logger.info(f"Loading data for {state}...")
                    state_records = await self._load_all_state_data(state)

                    # Organize by date
                    for record in state_records:
                        date = record.get("date", "unknown")
                        if date != "unknown":
                            self.cache[state][date].append(record)

                    self.metadata["states_loaded"].add(state)
                    total_loaded += len(state_records)
                    logger.info(f"✅ Loaded {len(state_records):,} records for {state}")

                self.metadata["total_records"] = total_loaded
                self.metadata["last_updated"] = datetime.now()
                self.metadata["loading_status"] = "loaded"

                # Calculate date range
                all_dates = []
                for state_data in self.cache.values():
                    all_dates.extend(state_data.keys())

                if all_dates:
                    self.metadata["date_range"]["start"] = min(all_dates)
                    self.metadata["date_range"]["end"] = max(all_dates)

                logger.info(f"🎉 Cache initialization complete!")
                logger.info(f"   📦 Total records: {total_loaded:,}")
                logger.info(f"   🏛️  States: {len(self.target_states)}")
                logger.info(
                    f"   📅 Date range: {self.metadata['date_range']['start']} to {self.metadata['date_range']['end']}"
                )

                return True

            except Exception as e:
                logger.error(f"❌ Failed to initialize cache: {str(e)}")
                self.metadata["loading_status"] = "error"
                return False

    async def _load_all_state_data(self, state: str) -> List[Dict[str, Any]]:
        """Load all data for a state using pagination"""
        all_records = []

        # Get today's date and calculate 6 months back
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=180)  # 6 months

        # Load data for each date in range
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")

            # Load all records for this state and date using pagination
            offset = 0
            limit = 1000  # Max per page

            while True:
                try:
                    async with aiohttp.ClientSession() as session:
                        url = f"{BACKEND_API_URL}/api/v1/market/data"
                        params = {
                            "state": state,
                            "date": date_str,
                            "limit": limit,
                            "offset": offset,
                        }

                        async with session.get(url, params=params, timeout=30) as response:
                            if response.status == 200:
                                data = await response.json()
                                records = data.get("data", [])

                                if not records:
                                    break  # No more records for this date

                                all_records.extend(records)

                                # If we got less than limit, we're done with this date
                                if len(records) < limit:
                                    break

                                offset += limit

                            else:
                                logger.warning(
                                    f"API error for {state} {date_str}: status {response.status}"
                                )
                                break

                except Exception as e:
                    logger.error(f"Error loading {state} {date_str}: {str(e)}")
                    break

            current_date += timedelta(days=1)

            # Small delay to avoid overwhelming the API
            await asyncio.sleep(0.1)

        return all_records

    def get_market_data(self, state: str, date: Optional[str] = None) -> Dict[str, Any]:
        """Get market data from cache (no API calls)"""
        if self.metadata["loading_status"] != "loaded":
            return {
                "success": False,
                "error": "Cache not initialized. Please wait for startup to complete.",
                "data": [],
                "total_records": 0,
            }

        # Default to today if no date specified
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        if state not in self.cache:
            return {
                "success": True,
                "data": [],
                "message": f"No data available for {state}",
                "total_records": 0,
                "source": "cache",
            }

        records = self.cache[state].get(date, [])

        return {
            "success": True,
            "data": records,
            "total_records": len(records),
            "source": "cache",
            "state": state,
            "date": date,
        }

    def get_commodity_data(self, state: str, commodity: str, days_back: int = 30) -> Dict[str, Any]:
        """Get commodity data across multiple dates for trend analysis"""
        if self.metadata["loading_status"] != "loaded":
            return {"success": False, "error": "Cache not initialized", "data": []}

        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)

        matching_records = []

        if state in self.cache:
            for date_str, records in self.cache[state].items():
                # Check if date is in range
                try:
                    record_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if start_date <= record_date <= end_date:
                        # Filter by commodity
                        for record in records:
                            if record.get("commodity", "").lower() == commodity.lower():
                                matching_records.append(record)
                except:
                    continue

        return {
            "success": True,
            "data": matching_records,
            "total_records": len(matching_records),
            "source": "cache",
            "state": state,
            "commodity": commodity,
            "days_back": days_back,
        }

    def get_market_comparison(
        self, state: str, commodity: str, markets: List[str] = None
    ) -> Dict[str, Any]:
        """Get commodity data across different markets for comparison"""
        if self.metadata["loading_status"] != "loaded":
            return {"success": False, "error": "Cache not initialized", "data": []}

        matching_records = []

        if state in self.cache:
            for records in self.cache[state].values():
                for record in records:
                    record_commodity = record.get("commodity", "").lower()
                    record_market = record.get("market", "")

                    # Match commodity
                    if record_commodity == commodity.lower():
                        # Match market if specified
                        if not markets or record_market in markets:
                            matching_records.append(record)

        return {
            "success": True,
            "data": matching_records,
            "total_records": len(matching_records),
            "source": "cache",
            "state": state,
            "commodity": commodity,
        }

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics and metadata"""
        stats = dict(self.metadata)
        stats["states_loaded"] = list(stats["states_loaded"])

        # Add per-state record counts
        state_counts = {}
        for state, state_data in self.cache.items():
            total_records = sum(len(records) for records in state_data.values())
            state_counts[state] = {
                "total_records": total_records,
                "dates_available": len(state_data),
            }

        stats["state_breakdown"] = state_counts
        return stats

    async def refresh_cache(self) -> bool:
        """Refresh cache data (can be called periodically)"""
        logger.info("🔄 Refreshing market data cache...")

        # Clear existing cache
        self.cache.clear()
        self.metadata["loading_status"] = "not_started"

        # Reload data
        return await self.initialize()


# Global cache instance
market_cache = MarketDataCache()


async def initialize_cache():
    """Initialize the global cache instance"""
    return await market_cache.initialize()


def get_cached_market_data(state: str, date: Optional[str] = None) -> Dict[str, Any]:
    """Get market data from cache"""
    return market_cache.get_market_data(state, date)


def get_cached_commodity_data(state: str, commodity: str, days_back: int = 30) -> Dict[str, Any]:
    """Get commodity trend data from cache"""
    return market_cache.get_commodity_data(state, commodity, days_back)


def get_cached_market_comparison(
    state: str, commodity: str, markets: List[str] = None
) -> Dict[str, Any]:
    """Get market comparison data from cache"""
    return market_cache.get_market_comparison(state, commodity, markets)


def get_cache_status() -> Dict[str, Any]:
    """Get cache status and statistics"""
    return market_cache.get_cache_stats()
