#!/usr/bin/env python3
"""
Kisan AI - Bulk Market Data Loader
==================================

Comprehensive script to fetch and store market data from Data.gov.in API into Firestore.
Supports loading data for multiple states, date ranges, and handles rate limiting.

Usage:
    python scripts/bulk_data_loader.py --help
    python scripts/bulk_data_loader.py --states all --days 30
    python scripts/bulk_data_loader.py --states Karnataka,Maharashtra --days 7
    python scripts/bulk_data_loader.py --date 2025-01-15  # Single date
"""

import argparse
import asyncio
import os
import sys
from datetime import date, datetime, timedelta
from typing import List, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.constants import DateFormats
from app.services.market_service import market_service
from app.utils.gcp.gcp_manager import gcp_manager
from app.utils.logger import logger


class BulkDataLoader:
    """Bulk data loader for market prices from Data.gov.in API"""
    
    # Indian states with agricultural markets
    INDIAN_STATES = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
        "Delhi", "Jammu and Kashmir", "Ladakh"
    ]
    
    def __init__(self, delay_between_requests: float = 1.0):
        """
        Initialize bulk data loader
        
        Args:
            delay_between_requests: Seconds to wait between API calls (rate limiting)
        """
        self.delay = delay_between_requests
        self.stats = {
            "requests_made": 0,
            "records_stored": 0,
            "errors": 0,
            "states_processed": 0,
            "dates_processed": 0
        }
    
    async def load_data_for_date_range(
        self, 
        states: List[str], 
        start_date: date, 
        end_date: date,
        skip_existing: bool = True
    ) -> dict:
        """
        Load market data for multiple states across a date range
        
        Args:
            states: List of state names to fetch data for
            start_date: Start date for data fetching
            end_date: End date for data fetching  
            skip_existing: Skip dates that already have data in Firestore
            
        Returns:
            Dictionary with loading statistics
        """
        logger.info(
            "Starting bulk data load",
            states=len(states),
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            skip_existing=skip_existing
        )
        
        # Initialize GCP services
        await gcp_manager.initialize()
        logger.info("GCP services initialized for bulk loading")
        
        current_date = start_date
        
        while current_date <= end_date:
            logger.info(f"Processing date: {current_date}")
            
            for state in states:
                try:
                    # Check if data already exists (if skip_existing is True)
                    if skip_existing and await self._has_existing_data(state, current_date):
                        logger.info(f"Skipping {state} for {current_date} - data already exists")
                        continue
                    
                    # Fetch data for this state and date
                    logger.info(f"Fetching data for {state} on {current_date}")
                    
                    result = await market_service.get_market_data(
                        state=state,
                        date=current_date
                    )
                    
                    self.stats["requests_made"] += 1
                    
                    # Check if successful
                    if result.get("success", False):
                        records = result.get("data", [])
                        self.stats["records_stored"] += len(records)
                        
                        logger.info(
                            "Data loaded successfully",
                            state=state,
                            date=current_date.isoformat(),
                            records=len(records),
                            source=result.get("source", "unknown")
                        )
                    else:
                        logger.warning(
                            "Failed to load data",
                            state=state,
                            date=current_date.isoformat(),
                            error=result.get("message", "Unknown error")
                        )
                        self.stats["errors"] += 1
                    
                    # Rate limiting - wait between requests
                    if self.delay > 0:
                        await asyncio.sleep(self.delay)
                        
                except Exception as e:
                    logger.error(
                        "Exception during data loading",
                        state=state,
                        date=current_date.isoformat(),
                        error=str(e)
                    )
                    self.stats["errors"] += 1
            
            self.stats["dates_processed"] += 1
            current_date += timedelta(days=1)
        
        self.stats["states_processed"] = len(states)
        
        logger.info("Bulk data loading completed", stats=self.stats)
        return self.stats
    
    async def load_data_for_single_date(
        self, 
        states: List[str], 
        target_date: date,
        skip_existing: bool = True
    ) -> dict:
        """Load data for multiple states on a single date"""
        return await self.load_data_for_date_range(
            states=states,
            start_date=target_date,
            end_date=target_date,
            skip_existing=skip_existing
        )
    
    async def load_latest_data(self, states: List[str]) -> dict:
        """Load latest available data (today) for specified states"""
        today = datetime.now().date()
        return await self.load_data_for_single_date(
            states=states,
            target_date=today,
            skip_existing=False  # Always fetch latest
        )
    
    async def _has_existing_data(self, state: str, check_date: date) -> bool:
        """Check if data already exists in Firestore for given state and date"""
        try:
            date_str = check_date.strftime(DateFormats.ISO_DATE)
            
            # Query for any document matching this state and date
            docs = gcp_manager.firestore.collection("daily_market_prices")\
                .where("state", "==", state)\
                .where("date", "==", date_str)\
                .limit(1)\
                .stream()
            
            # If any document exists, we have data
            for doc in docs:
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking existing data: {str(e)}")
            return False  # Assume no data exists if we can't check
    
    def print_summary(self):
        """Print loading summary statistics"""
        print("\n" + "=" * 60)
        print("📊 BULK DATA LOADING SUMMARY")
        print("=" * 60)
        
        print(f"🔄 Requests Made: {self.stats['requests_made']}")
        print(f"📦 Records Stored: {self.stats['records_stored']:,}")
        print(f"🏛️  States Processed: {self.stats['states_processed']}")
        print(f"📅 Dates Processed: {self.stats['dates_processed']}")
        print(f"❌ Errors: {self.stats['errors']}")
        
        if self.stats["requests_made"] > 0:
            avg_records = self.stats["records_stored"] / self.stats["requests_made"]
            print(f"📈 Avg Records/Request: {avg_records:.1f}")
        
        if self.stats["errors"] == 0:
            print("\n✅ ALL DATA LOADED SUCCESSFULLY!")
        else:
            error_rate = (self.stats["errors"] / self.stats["requests_made"]) * 100
            print(f"\n⚠️  Error Rate: {error_rate:.1f}%")


def parse_states(states_input: str) -> List[str]:
    """Parse state input string into list of states"""
    if states_input.lower() == "all":
        return BulkDataLoader.INDIAN_STATES
    else:
        return [state.strip() for state in states_input.split(",")]


def parse_date(date_string: str) -> date:
    """Parse date string in YYYY-MM-DD format"""
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_string}. Use YYYY-MM-DD")


async def main():
    """Main entry point for bulk data loader"""
    parser = argparse.ArgumentParser(
        description="Bulk load market data from Data.gov.in into Firestore",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load data for all states for the last 7 days
  python bulk_data_loader.py --states all --days 7
  
  # Load data for specific states for the last 30 days
  python bulk_data_loader.py --states "Karnataka,Maharashtra,Punjab" --days 30
  
  # Load data for a specific date
  python bulk_data_loader.py --states all --date 2025-01-15
  
  # Load only today's data for all states (daily cron job)
  python bulk_data_loader.py --states all --latest
        """
    )
    
    # State selection
    parser.add_argument(
        "--states",
        default="Karnataka",
        help="States to load data for. Use 'all' for all states, or comma-separated list (default: Karnataka)"
    )
    
    # Date options (mutually exclusive)
    date_group = parser.add_mutually_exclusive_group(required=True)
    date_group.add_argument(
        "--days",
        type=int,
        help="Number of days to load (from today backwards)"
    )
    date_group.add_argument(
        "--date",
        type=parse_date,
        help="Specific date to load (YYYY-MM-DD format)"
    )
    date_group.add_argument(
        "--latest",
        action="store_true",
        help="Load only today's data (for daily cron jobs)"
    )
    date_group.add_argument(
        "--date-range",
        nargs=2,
        metavar=("START", "END"),
        type=parse_date,
        help="Date range to load (START END in YYYY-MM-DD format)"
    )
    
    # Options
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between API requests in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reload even if data already exists"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be loaded without actually loading"
    )
    
    args = parser.parse_args()
    
    # Parse states
    states = parse_states(args.states)
    print(f"🏛️  States to process: {len(states)}")
    if len(states) <= 5:
        print(f"   States: {', '.join(states)}")
    else:
        print(f"   States: {', '.join(states[:3])}... and {len(states)-3} more")
    
    # Determine date range
    if args.days:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=args.days - 1)
        print(f"📅 Date range: {start_date} to {end_date} ({args.days} days)")
    elif args.date:
        start_date = end_date = args.date
        print(f"📅 Single date: {args.date}")
    elif args.latest:
        start_date = end_date = datetime.now().date()
        print(f"📅 Latest data: {start_date}")
    elif args.date_range:
        start_date, end_date = args.date_range
        print(f"📅 Date range: {start_date} to {end_date}")
    
    if args.dry_run:
        print("\n🧪 DRY RUN MODE - No data will actually be loaded")
        total_requests = len(states) * ((end_date - start_date).days + 1)
        print(f"📊 Would make approximately {total_requests} API requests")
        return
    
    # Initialize loader
    loader = BulkDataLoader(delay_between_requests=args.delay)
    
    # Load data
    print(f"\n🚀 Starting bulk data load...")
    print(f"⏱️  Rate limit: {args.delay} seconds between requests")
    print(f"🔄 Skip existing: {'No' if args.force else 'Yes'}")
    
    try:
        stats = await loader.load_data_for_date_range(
            states=states,
            start_date=start_date,
            end_date=end_date,
            skip_existing=not args.force
        )
        
        loader.print_summary()
        
    except KeyboardInterrupt:
        print("\n⚠️  Loading interrupted by user")
        loader.print_summary()
    except Exception as e:
        print(f"\n❌ Error during bulk loading: {str(e)}")
        loader.print_summary()


if __name__ == "__main__":
    asyncio.run(main()) 