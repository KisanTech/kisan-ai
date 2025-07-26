#!/usr/bin/env python3
"""
Kisan AI - Daily Market Data Sync
=================================

Simple cron job script to fetch and store today's market data from Data.gov.in.
Designed to run daily to keep the database current.

Usage:
    python scripts/daily_data_sync.py
    
Cron job example (runs every day at 6 AM):
    0 6 * * * cd /path/to/kisan-ai/backend && uv run python scripts/daily_data_sync.py
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.market_service import market_service
from app.utils.gcp.gcp_manager import gcp_manager
from app.utils.logger import logger

# Key agricultural states to sync daily
PRIORITY_STATES = [
    "Karnataka", "Maharashtra", "Punjab", "Haryana", "Uttar Pradesh", 
    "Gujarat", "Rajasthan", "Madhya Pradesh", "Tamil Nadu", "Andhra Pradesh"
]

# Updated priority states based on actual data availability
RELIABLE_STATES = [
    "Punjab",
    "Haryana",
    "Uttar Pradesh",
    "Gujarat",
    "Rajasthan",
    "Madhya Pradesh",
    "Andhra Pradesh",
]

# States that need historical data fallback
HISTORICAL_FALLBACK_STATES = ["Karnataka", "Maharashtra", "Tamil Nadu"]


async def get_historical_data_for_state(state: str, days_back: int = 7):
    """Try to get data for a state from recent days if today's data is not available"""
    today = datetime.now().date()

    for days in range(1, days_back + 1):
        target_date = today - timedelta(days=days)

        logger.info(f"Trying historical data for {state}", date=target_date.isoformat())

        result = await market_service.get_market_data(state=state, date=target_date)

        if result.get("success", False) and result.get("data"):
            logger.info(
                "Found historical data for state",
                state=state,
                date=target_date.isoformat(),
                records=len(result.get("data", [])),
                days_back=days,
            )
            return result

    logger.warning(f"No historical data found for {state} in past {days_back} days")
    return None


async def sync_daily_data():
    """Sync today's market data for priority states"""
    today = datetime.now().date()

    logger.info("Starting daily market data sync", date=today.isoformat())

    try:
        # Initialize GCP services
        await gcp_manager.initialize()
        logger.info("GCP services initialized for daily sync")

        total_records = 0
        successful_states = 0
        failed_states = []

        for state in PRIORITY_STATES:
            try:
                logger.info(f"Syncing data for {state}")

                result = await market_service.get_market_data(
                    state=state,
                    date=today
                )

                if result.get("success", False):
                    records = result.get("data", [])
                    total_records += len(records)
                    successful_states += 1

                    logger.info(
                        "State sync successful",
                        state=state,
                        records=len(records),
                        source=result.get("source", "unknown")
                    )
                else:
                    # Try historical data for problematic states
                    if state in HISTORICAL_FALLBACK_STATES:
                        logger.info(f"Trying historical data fallback for {state}")
                        historical_result = await get_historical_data_for_state(state, days_back=7)

                        if historical_result and historical_result.get("success", False):
                            records = historical_result.get("data", [])
                            total_records += len(records)
                            successful_states += 1

                            logger.info(
                                "State sync successful with historical data",
                                state=state,
                                records=len(records),
                                source=f"historical_{historical_result.get('source', 'unknown')}",
                            )
                        else:
                            failed_states.append(state)
                            error_msg = result.get("error") or result.get(
                                "message", "Unknown error"
                            )
                            logger.warning(
                                "State sync failed even with historical fallback",
                                state=state,
                                error=error_msg,
                                source=result.get("source", "unknown"),
                            )
                    else:
                        failed_states.append(state)
                        error_msg = result.get("error") or result.get("message", "Unknown error")
                        logger.warning(
                            "State sync failed",
                            state=state,
                            error=error_msg,
                            source=result.get("source", "unknown"),
                        )

                # Small delay between requests (rate limiting)
                await asyncio.sleep(0.5)

            except Exception as e:
                failed_states.append(state)
                logger.error(
                    "Exception during state sync",
                    state=state,
                    error=str(e)
                )

        # Log final summary
        logger.info(
            "Daily sync completed",
            date=today.isoformat(),
            successful_states=successful_states,
            failed_states=len(failed_states),
            total_records=total_records,
            failed_state_list=failed_states
        )

        # Print summary for cron job logs
        print(f"✅ Daily sync completed: {successful_states}/{len(PRIORITY_STATES)} states successful")
        print(f"📦 Total records synced: {total_records:,}")

        if failed_states:
            print(f"⚠️  Failed states: {', '.join(failed_states)}")

        return {
            "success": True,
            "states_synced": successful_states,
            "total_records": total_records,
            "failed_states": failed_states
        }

    except Exception as e:
        logger.error("Daily sync failed", error=str(e))
        print(f"❌ Daily sync failed: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    asyncio.run(sync_daily_data()) 
