"""
Market Agent Tools
==================

Tools for fetching and analyzing agricultural market data from Kisan AI backend.
Uses intelligent caching for fast access to all historical data.
"""

import asyncio
import os
from typing import Any, Dict, Optional

import aiohttp
from google.adk.tools import FunctionTool

# Import cache manager
from market_agent.cache_manager import (
    get_cache_status,
    get_cached_commodity_data,
    get_cached_market_comparison,
    get_cached_market_data,
)

# Backend API configuration from environment
BACKEND_API_URL = os.getenv("BACKEND_API_URL")


async def _get_market_data_raw(state: str, date: Optional[str] = None) -> Dict[str, Any]:
    """Raw function to fetch market data from cache (no API calls)."""
    try:
        # Get data from cache - much faster than API calls!
        result = get_cached_market_data(state, date)

        # Add metadata for consistency with old API
        if result["success"]:
            result["state"] = state
            result["date"] = date or "latest"

        return result

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to fetch cached market data: {str(e)}",
            "state": state,
            "date": date or "latest",
        }


async def _get_price_summary_raw(state: str, commodity: Optional[str] = None) -> Dict[str, Any]:
    """Raw function to get price summary."""
    try:
        # Use raw function instead of decorated tool
        market_data = await _get_market_data_raw(state)

        if not market_data["success"]:
            return market_data

        records = market_data["data"]
        if not records:
            return {"success": True, "message": f"No market data found for {state}", "summary": {}}

        # Filter by commodity if specified (flexible matching for singular/plural)
        if commodity:
            commodity_lower = commodity.lower().rstrip("s")  # Remove trailing 's' for plural

            filtered_records = []
            for r in records:
                comm_name = r.get("commodity", "")
                comm_name_lower = comm_name.lower().rstrip("s")  # Remove trailing 's'

                # Check both directions: commodity in comm_name OR comm_name in commodity
                if (
                    commodity_lower in comm_name_lower
                    or comm_name_lower in commodity_lower
                    or commodity.lower() in comm_name.lower()
                    or comm_name.lower() in commodity.lower()
                ):
                    filtered_records.append(r)

            records = filtered_records
            if not records:
                return {
                    "success": True,
                    "message": f"No data found for {commodity} in {state}",
                    "summary": {},
                }

        # Group by commodity for summary
        commodity_summary = {}
        for record in records:
            comm = record.get("commodity", "Unknown")
            # Convert from ₹/tonne to ₹/kg (API returns prices per tonne)
            price_per_tonne = float(record.get("modal_price", 0))
            price = price_per_tonne / 1000  # Convert tonne to kg
            market = record.get("market", "Unknown")

            if comm not in commodity_summary:
                commodity_summary[comm] = {"prices": [], "markets": set(), "records": []}

            commodity_summary[comm]["prices"].append(price)
            commodity_summary[comm]["markets"].add(market)
            commodity_summary[comm]["records"].append(record)

        # Calculate statistics for each commodity
        summary = {}
        for comm, data in commodity_summary.items():
            prices = data["prices"]
            summary[comm] = {
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_price": round(sum(prices) / len(prices), 2),
                "num_markets": len(data["markets"]),
                "markets": list(data["markets"]),
                "price_range": max(prices) - min(prices),
                "total_records": len(prices),
            }

        return {
            "success": True,
            "state": state,
            "commodity_filter": commodity,
            "total_commodities": len(summary),
            "summary": summary,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to calculate price summary: {str(e)}",
            "state": state,
            "commodity": commodity,
        }


async def _calculate_revenue_raw(state: str, commodity: str, quantity_kg: float) -> Dict[str, Any]:
    """Raw function to calculate revenue."""
    try:
        # Use raw function instead of decorated tool
        price_data = await _get_price_summary_raw(state, commodity)

        if not price_data["success"]:
            return price_data

        summary = price_data.get("summary", {})

        # Find matching commodity (flexible matching for singular/plural)
        matching_commodity = None
        commodity_lower = commodity.lower().rstrip("s")  # Remove trailing 's' for plural

        for comm_name, comm_data in summary.items():
            comm_name_lower = comm_name.lower().rstrip("s")  # Remove trailing 's'

            # Check both directions: commodity in comm_name OR comm_name in commodity
            if (
                commodity_lower in comm_name_lower
                or comm_name_lower in commodity_lower
                or commodity.lower() in comm_name.lower()
                or comm_name.lower() in commodity.lower()
            ):
                matching_commodity = comm_name
                break

        if not matching_commodity:
            return {
                "success": False,
                "error": f"No price data found for {commodity} in {state}",
                "suggestion": f"Available commodities: {list(summary.keys())}",
            }

        comm_data = summary[matching_commodity]

        # Calculate revenue scenarios
        min_revenue = comm_data["min_price"] * quantity_kg
        max_revenue = comm_data["max_price"] * quantity_kg
        avg_revenue = comm_data["avg_price"] * quantity_kg

        # Find best and worst markets using raw data
        market_data = await _get_market_data_raw(state)
        best_market = None
        worst_market = None
        best_price = 0
        worst_price = float("inf")
        market_prices = {}

        if market_data["success"]:
            commodity_lower = commodity.lower().rstrip("s")  # Remove trailing 's' for plural

            for record in market_data["data"]:
                comm_name = record.get("commodity", "")
                comm_name_lower = comm_name.lower().rstrip("s")  # Remove trailing 's'

                # Check both directions: commodity in comm_name OR comm_name in commodity
                if (
                    commodity_lower in comm_name_lower
                    or comm_name_lower in commodity_lower
                    or commodity.lower() in comm_name.lower()
                    or comm_name.lower() in commodity.lower()
                ):
                    market = record.get("market", "Unknown")
                    # Convert from ₹/tonne to ₹/kg (API returns prices per tonne)
                    price_per_tonne = float(record.get("modal_price", 0))
                    price = price_per_tonne / 1000  # Convert tonne to kg
                    market_prices[market] = price

                    if price > best_price:
                        best_price = price
                        best_market = market
                    if price < worst_price:
                        worst_price = price
                        worst_market = market

        return {
            "success": True,
            "commodity": matching_commodity,
            "quantity_kg": quantity_kg,
            "state": state,
            "revenue_analysis": {
                "minimum_revenue": round(min_revenue, 2),
                "maximum_revenue": round(max_revenue, 2),
                "average_revenue": round(avg_revenue, 2),
                "potential_profit_range": round(max_revenue - min_revenue, 2),
            },
            "price_analysis": {
                "min_price_per_kg": comm_data["min_price"],
                "max_price_per_kg": comm_data["max_price"],
                "avg_price_per_kg": comm_data["avg_price"],
                "price_variation": comm_data["price_range"],
            },
            "market_recommendations": {
                "best_market": best_market,
                "best_price": best_price,
                "worst_market": worst_market,
                "worst_price": worst_price,
                "all_market_prices": market_prices,
            },
            "num_markets_analyzed": comm_data["num_markets"],
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to calculate revenue: {str(e)}",
            "commodity": commodity,
            "quantity_kg": quantity_kg,
            "state": state,
        }


# ===== TOOL DECORATORS (Agent-callable) =====
# These wrap the raw functions for agent use


@FunctionTool
async def get_market_data(state: str, date: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch market data from Kisan AI backend API.

    Args:
        state: Indian state name (e.g., "Karnataka", "Maharashtra")
        date: Optional date in YYYY-MM-DD format. If not provided, returns latest data.

    Returns:
        Dictionary containing market data with success status and records
    """
    return await _get_market_data_raw(state, date)


@FunctionTool
async def get_price_summary(state: str, commodity: Optional[str] = None) -> Dict[str, Any]:
    """
    Get price summary and statistics for specific commodity or all commodities.

    Args:
        state: Indian state name
        commodity: Optional commodity name to filter by

    Returns:
        Price summary with min, max, average prices and market information
    """
    return await _get_price_summary_raw(state, commodity)


@FunctionTool
async def calculate_revenue(state: str, commodity: str, quantity_kg: float) -> Dict[str, Any]:
    """
    Calculate potential revenue for selling a specific quantity of commodity.

    Args:
        state: Indian state name
        commodity: Commodity name
        quantity_kg: Quantity in kilograms

    Returns:
        Revenue calculation with min, max, and average potential earnings
    """
    return await _calculate_revenue_raw(state, commodity, quantity_kg)
