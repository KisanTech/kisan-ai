"""
Market Agent V3 Tools - Simplified
==================================

Simple tool that makes targeted API calls based on LLM-extracted parameters.
Let the LLM do the smart work, not hardcoded mappings.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from google.adk.tools import FunctionTool

# Setup logging
logger = logging.getLogger(__name__)

# Backend API configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL")


@FunctionTool
async def get_market_data_smart(
    state: str, commodity: str | None = None, days: int = 60
) -> dict[str, Any]:
    """
    Get market data with smart filtering using the new filtered endpoint.

    Args:
        state: Indian state name (e.g., "Karnataka", "Tamil Nadu")
        commodity: Optional commodity filter (e.g., "tomato", "onion")
        days: Number of days to look back (default: 60)
    """
    try:
        if not BACKEND_API_URL:
            return {"success": False, "error": "Backend API URL not configured"}

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Use the new filtered endpoint
        params = {
            "state": state,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "limit": 2000,  # Higher limit for agent queries
        }

        if commodity:
            params["commodity"] = commodity

        url = f"{BACKEND_API_URL}/api/v1/market/filtered-data"

        logger.info(f"📡 Smart API call: {url}")
        logger.info(f"   Filters: state={state}, commodity={commodity}, days={days}")

        async with aiohttp.ClientSession() as session_http:
            async with session_http.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    if data.get("success"):
                        records = data.get("data", [])

                        logger.info(f"✅ Found {len(records)} records")

                        return {
                            "success": True,
                            "data": records,
                            "total_records": len(records),
                            "filters_applied": data.get("filters_applied", {}),
                            "date_range": data.get("date_range", {}),
                            "source": "filtered_endpoint",
                        }
                    else:
                        error_msg = data.get("error", "Unknown error from filtered endpoint")
                        logger.error(f"❌ Filtered endpoint error: {error_msg}")
                        return {"success": False, "error": error_msg}
                else:
                    error_msg = f"API returned status {response.status}"
                    logger.error(f"❌ API Error: {error_msg}")
                    return {"success": False, "error": error_msg}

    except Exception as e:
        logger.error(f"❌ API call failed: {str(e)}")
        return {"success": False, "error": f"API call failed: {str(e)}"}


__all__ = ["get_market_data_smart"]
