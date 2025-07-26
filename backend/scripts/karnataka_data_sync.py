#!/usr/bin/env python3
"""
Karnataka Market Data Sync
===========================

Specialized script to fetch Karnataka market data with historical fallback.
Since Karnataka data is not always available for the current date, this script
tries to get the most recent available data.

Usage:
    python scripts/karnataka_data_sync.py
    
Features:
- Tries current date first
- Falls back to recent historical dates (up to 30 days)
- Stores data with appropriate date metadata
- Provides detailed reporting
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


async def sync_karnataka_data(max_days_back: int = 30):
    """Sync Karnataka market data with extensive historical fallback"""
    today = datetime.now().date()
    
    logger.info("Starting Karnataka market data sync", max_days_back=max_days_back)
    
    try:
        # Initialize GCP services
        await gcp_manager.initialize()
        logger.info("GCP services initialized for Karnataka sync")
        
        # Try to get data starting from today going backwards
        for days_back in range(max_days_back + 1):
            target_date = today - timedelta(days=days_back)
            
            logger.info(
                "Attempting Karnataka data fetch",
                date=target_date.isoformat(),
                days_back=days_back
            )
            
            result = await market_service.get_market_data(
                state="Karnataka",
                date=target_date
            )
            
            if result.get("success", False) and result.get("data"):
                records = result.get("data", [])
                
                logger.info(
                    "Karnataka data sync successful",
                    date=target_date.isoformat(),
                    records=len(records),
                    days_back=days_back,
                    source=result.get("source", "unknown")
                )
                
                # Print summary for console
                if days_back == 0:
                    print(f"✅ Found current Karnataka data: {len(records):,} records")
                else:
                    print(f"✅ Found Karnataka data from {days_back} days ago ({target_date}): {len(records):,} records")
                
                # Show sample markets/commodities
                markets = set(record.get("market", "Unknown") for record in records[:10])
                commodities = set(record.get("commodity", "Unknown") for record in records[:10])
                
                print(f"📍 Sample markets: {', '.join(list(markets)[:5])}")
                print(f"🌾 Sample commodities: {', '.join(list(commodities)[:5])}")
                
                return {
                    "success": True,
                    "date": target_date.isoformat(),
                    "days_back": days_back,
                    "records": len(records),
                    "source": result.get("source", "unknown")
                }
        
        # No data found in the entire range
        logger.warning(
            "No Karnataka data found in date range",
            max_days_back=max_days_back,
            start_date=today.isoformat(),
            end_date=(today - timedelta(days=max_days_back)).isoformat()
        )
        
        print(f"❌ No Karnataka data found in the past {max_days_back} days")
        print("💡 Karnataka might not be available in the current Data.gov.in dataset")
        
        return {
            "success": False,
            "error": f"No Karnataka data found in past {max_days_back} days"
        }
        
    except Exception as e:
        logger.error("Karnataka sync failed", error=str(e))
        print(f"❌ Karnataka sync failed: {str(e)}")
        return {"success": False, "error": str(e)}


async def check_karnataka_availability():
    """Check if Karnataka data is available and when"""
    logger.info("Checking Karnataka data availability")
    
    try:
        await gcp_manager.initialize()
        
        # Check stored data in Firestore
        stored_data = await market_service._get_stored_data("Karnataka", datetime.now().date().strftime("%Y-%m-%d"))
        
        if stored_data:
            print(f"📊 Karnataka data already stored for today: {len(stored_data):,} records")
            return True
        
        print("🔍 No Karnataka data found for today, checking availability...")
        result = await sync_karnataka_data(max_days_back=30)
        return result.get("success", False)
        
    except Exception as e:
        logger.error("Karnataka availability check failed", error=str(e))
        print(f"❌ Availability check failed: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Karnataka Market Data Sync")
    parser.add_argument(
        "--days-back", 
        type=int, 
        default=30, 
        help="Maximum days to look back for data (default: 30)"
    )
    parser.add_argument(
        "--check-only", 
        action="store_true", 
        help="Only check availability, don't sync"
    )
    
    args = parser.parse_args()
    
    if args.check_only:
        asyncio.run(check_karnataka_availability())
    else:
        asyncio.run(sync_karnataka_data(max_days_back=args.days_back)) 