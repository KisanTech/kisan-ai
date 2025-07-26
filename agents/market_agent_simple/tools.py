"""
Simplified Market Agent Tools
============================

Minimal tools approach - just fetch data, let LLM do all analysis.
"""

import asyncio
import os
from typing import Any, Dict, Optional

import aiohttp
from google.adk.tools import FunctionTool

# Backend API configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL")


@FunctionTool
async def get_market_data(state: str, date: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch market data from Kisan AI backend API.

    Args:
        state: Indian state name (e.g., "Karnataka", "Maharashtra")
        date: Optional date in YYYY-MM-DD format. If not provided, returns latest data.

    Returns:
        Dictionary containing all raw market data for LLM analysis
    """
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{BACKEND_API_URL}/api/v1/market/data"
            params = {"state": state}

            if date:
                params["date"] = date

            async with session.get(url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data.get("data", []),
                        "total_records": len(data.get("data", [])),
                        "source": data.get("source", "unknown"),
                        "state": state,
                        "date": date or "latest",
                        "instruction": "Analyze this raw market data to answer the user's question about prices, revenue calculations, or market comparisons.",
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API returned status {response.status}",
                        "state": state,
                        "date": date or "latest",
                    }

    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": "Request timeout - backend API took too long to respond",
            "state": state,
            "date": date or "latest",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to fetch market data: {str(e)}",
            "state": state,
            "date": date or "latest",
        }
