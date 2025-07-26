#!/usr/bin/env python3
"""
Historical Market Data Generator
===============================

Generates 6 months of realistic historical market data for demo purposes.
Creates data with realistic price variations, seasonal trends, and market fluctuations.

Features:
- Extracts existing data patterns for Karnataka, Tamil Nadu, and Punjab
- Generates data for past 6 months (January 2025 to June 2025)
- Maintains realistic price trends and seasonal variations
- Uses same commodities, markets, and data structure as current data
- Adds random but realistic price fluctuations

Usage:
    python scripts/generate_historical_data.py --preview  # Show what will be generated
    python scripts/generate_historical_data.py --generate # Actually generate and upload
"""

import asyncio
import json
import math
import os
import random
import sys
from datetime import date, datetime, timedelta
from typing import Any, Dict, List

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.constants import DateFormats, FieldNames, Separators
from app.utils.gcp.gcp_manager import gcp_manager
from app.utils.logger import logger


class HistoricalDataGenerator:
    def __init__(self):
        self.target_states = ['Karnataka', 'Tamil Nadu', 'Punjab']
        self.months_back = 6
        self.current_data = {}
        self.seasonal_patterns = {
            # Seasonal multipliers for different months (1.0 = normal, 1.2 = 20% higher, 0.8 = 20% lower)
            'Karnataka': {
                1: 0.85,  # January - winter harvest, lower prices
                2: 0.90,  # February
                3: 1.05,  # March - pre-summer demand increase
                4: 1.15,  # April - summer demand peak
                5: 1.10,  # May
                6: 0.95,  # June - monsoon begins
                7: 1.00,  # July - current baseline
            },
            'Tamil Nadu': {
                1: 0.90,  # January
                2: 0.95,  # February
                3: 1.10,  # March
                4: 1.20,  # April - hot season demand
                5: 1.15,  # May
                6: 1.00,  # June - monsoon
                7: 1.00,  # July - current baseline
            },
            'Punjab': {
                1: 0.80,  # January - winter harvest
                2: 0.85,  # February
                3: 1.00,  # March
                4: 1.10,  # April
                5: 1.15,  # May - wheat harvest season demand
                6: 0.95,  # June
                7: 1.00,  # July - current baseline
            }
        }

    async def extract_current_data(self):
        """Extract current data patterns for each target state"""
        logger.info("Extracting current data patterns")
        
        await gcp_manager.initialize()
        collection_ref = gcp_manager.firestore.collection('daily_market_prices')
        
        for state in self.target_states:
            logger.info(f"Extracting data for {state}")
            
            # Get all documents for this state
            docs = collection_ref.where('state', '==', state).stream()
            
            state_data = {
                'markets': set(),
                'commodities': {},  # commodity -> {prices: [], markets: [], varieties: [], grades: []}
                'districts': set(),
                'total_records': 0
            }
            
            for doc in docs:
                doc_data = doc.to_dict()
                
                # Extract basic info
                market = doc_data.get('market', 'Unknown')
                commodity = doc_data.get('commodity', 'Unknown')
                district = doc_data.get('district', 'Unknown')
                variety = doc_data.get('variety', 'Common')
                grade = doc_data.get('grade', 'Medium')
                
                state_data['markets'].add(market)
                state_data['districts'].add(district)
                state_data['total_records'] += 1
                
                # Extract commodity-specific data
                if commodity not in state_data['commodities']:
                    state_data['commodities'][commodity] = {
                        'prices': [],
                        'markets': set(),
                        'varieties': set(),
                        'grades': set(),
                        'districts': set()
                    }
                
                # Add commodity data
                try:
                    modal_price = float(doc_data.get('modal_price', 0))
                    min_price = float(doc_data.get('min_price', modal_price * 0.9))
                    max_price = float(doc_data.get('max_price', modal_price * 1.1))
                    
                    if modal_price > 0:
                        state_data['commodities'][commodity]['prices'].append({
                            'modal': modal_price,
                            'min': min_price,
                            'max': max_price
                        })
                except:
                    continue
                
                state_data['commodities'][commodity]['markets'].add(market)
                state_data['commodities'][commodity]['varieties'].add(variety)
                state_data['commodities'][commodity]['grades'].add(grade)
                state_data['commodities'][commodity]['districts'].add(district)
            
            # Convert sets to lists for JSON serialization later
            state_data['markets'] = list(state_data['markets'])
            state_data['districts'] = list(state_data['districts'])
            
            for commodity in state_data['commodities']:
                comm_data = state_data['commodities'][commodity]
                comm_data['markets'] = list(comm_data['markets'])
                comm_data['varieties'] = list(comm_data['varieties'])
                comm_data['grades'] = list(comm_data['grades'])
                comm_data['districts'] = list(comm_data['districts'])
            
            self.current_data[state] = state_data
            
            logger.info(
                f"Extracted {state} data",
                markets=len(state_data['markets']),
                commodities=len(state_data['commodities']),
                total_records=state_data['total_records']
            )

    def calculate_base_price(self, commodity_data: Dict, month: int) -> Dict[str, float]:
        """Calculate base prices for a commodity in a given month"""
        if not commodity_data['prices']:
            return {'modal': 1000, 'min': 900, 'max': 1100}
        
        # Calculate average prices from current data
        total_modal = sum(p['modal'] for p in commodity_data['prices'])
        total_min = sum(p['min'] for p in commodity_data['prices'])
        total_max = sum(p['max'] for p in commodity_data['prices'])
        count = len(commodity_data['prices'])
        
        avg_modal = total_modal / count
        avg_min = total_min / count
        avg_max = total_max / count
        
        return {
            'modal': avg_modal,
            'min': avg_min,
            'max': avg_max
        }

    def apply_seasonal_variation(self, base_price: float, state: str, month: int) -> float:
        """Apply seasonal variation to base price"""
        seasonal_multiplier = self.seasonal_patterns.get(state, {}).get(month, 1.0)
        return base_price * seasonal_multiplier

    def apply_daily_variation(self, base_price: float, day_of_month: int) -> float:
        """Apply daily price variations (market fluctuations)"""
        # Create some predictable patterns within months
        # Early month: slightly higher (market opening)
        # Mid month: normal
        # End month: slightly lower (clearing inventory)
        
        if day_of_month <= 10:
            variation = random.uniform(0.95, 1.08)  # -5% to +8%
        elif day_of_month <= 20:
            variation = random.uniform(0.92, 1.05)  # -8% to +5%
        else:
            variation = random.uniform(0.88, 1.02)  # -12% to +2%
        
        # Add some random market noise
        noise = random.uniform(0.95, 1.05)
        
        return base_price * variation * noise

    def generate_price_data(self, base_prices: Dict[str, float], state: str, month: int, day: int) -> Dict[str, float]:
        """Generate modal, min, max prices for a specific date"""
        # Apply seasonal variation
        seasonal_modal = self.apply_seasonal_variation(base_prices['modal'], state, month)
        seasonal_min = self.apply_seasonal_variation(base_prices['min'], state, month)
        seasonal_max = self.apply_seasonal_variation(base_prices['max'], state, month)
        
        # Apply daily variations
        modal_price = self.apply_daily_variation(seasonal_modal, day)
        min_price = self.apply_daily_variation(seasonal_min, day)
        max_price = self.apply_daily_variation(seasonal_max, day)
        
        # Ensure logical price relationships
        if min_price > modal_price:
            min_price = modal_price * 0.9
        if max_price < modal_price:
            max_price = modal_price * 1.1
        
        return {
            'modal_price': round(modal_price, 1),
            'min_price': round(min_price, 1),
            'max_price': round(max_price, 1)
        }

    def create_document_id(self, state: str, date_str: str, market: str, commodity: str) -> str:
        """Create document ID matching existing format"""
        clean_market = market.replace(Separators.SLASH, Separators.UNDERSCORE).replace(
            Separators.SPACE, Separators.UNDERSCORE
        )
        clean_commodity = commodity.replace(Separators.SLASH, Separators.UNDERSCORE).replace(
            Separators.SPACE, Separators.UNDERSCORE
        )
        
        return (
            f"{state}{Separators.UNDERSCORE}{date_str}{Separators.UNDERSCORE}"
            f"{clean_market}{Separators.UNDERSCORE}{clean_commodity}"
        )

    async def generate_historical_data(self, preview_only: bool = True) -> Dict[str, Any]:
        """Generate 6 months of historical data"""
        logger.info("Starting historical data generation", preview_only=preview_only, months_back=self.months_back)
        
        # Calculate date range (6 months back from current date)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30 * self.months_back)
        
        logger.info(f"Generating data from {start_date} to {end_date}")
        
        generated_data = {}
        total_records = 0
        
        for state in self.target_states:
            state_data = self.current_data[state]
            generated_data[state] = []
            
            logger.info(f"Generating data for {state}")
            
            # Generate data for each date in the range
            current_date = start_date
            while current_date < end_date:
                # Skip future dates (keep only until yesterday)
                if current_date >= datetime.now().date():
                    current_date += timedelta(days=1)
                    continue
                
                date_str = current_date.strftime(DateFormats.ISO_DATE)
                arrival_date = current_date.strftime("%d/%m/%Y")
                
                # Generate data for each commodity
                for commodity, commodity_data in state_data['commodities'].items():
                    if not commodity_data['prices']:  # Skip commodities without price data
                        continue
                    
                    # Calculate base prices for this commodity
                    base_prices = self.calculate_base_price(commodity_data, current_date.month)
                    
                    # Generate for 60-80% of available markets (not all commodities in all markets daily)
                    available_markets = commodity_data['markets']
                    num_markets = max(1, int(len(available_markets) * random.uniform(0.6, 0.8)))
                    selected_markets = random.sample(available_markets, num_markets)
                    
                    for market in selected_markets:
                        # Generate prices for this market
                        prices = self.generate_price_data(base_prices, state, current_date.month, current_date.day)
                        
                        # Select random variety and grade
                        variety = random.choice(commodity_data['varieties']) if commodity_data['varieties'] else 'Common'
                        grade = random.choice(commodity_data['grades']) if commodity_data['grades'] else 'Medium'
                        district = random.choice(commodity_data['districts']) if commodity_data['districts'] else 'Unknown'
                        
                        # Create document
                        doc_id = self.create_document_id(state, date_str, market, commodity)
                        
                        document = {
                            'doc_id': doc_id,
                            'state': state,
                            'date': date_str,
                            'market': market,
                            'commodity': commodity,
                            'district': district,
                            'variety': variety,
                            'grade': grade,
                            'arrival_date': arrival_date,
                            'modal_price': str(int(prices['modal_price'])),
                            'min_price': str(int(prices['min_price'])),
                            'max_price': str(int(prices['max_price'])),
                            'data_source': 'Generated Historical Data',
                            'stored_at': datetime.now(),
                            'ttl': datetime.now() + timedelta(days=365)  # 1 year TTL for historical data
                        }
                        
                        generated_data[state].append(document)
                        total_records += 1
                
                current_date += timedelta(days=1)
            
            logger.info(f"Generated {len(generated_data[state])} records for {state}")
        
        logger.info(f"Total historical records generated: {total_records}")
        
        if not preview_only:
            await self.upload_to_firestore(generated_data)
        
        return {
            'total_records': total_records,
            'states': {state: len(records) for state, records in generated_data.items()},
            'date_range': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'preview_data': {
                state: records[:3] for state, records in generated_data.items()  # First 3 records per state
            }
        }

    async def upload_to_firestore(self, generated_data: Dict[str, List[Dict]]):
        """Upload generated data to Firestore"""
        logger.info("Uploading historical data to Firestore")
        
        collection_ref = gcp_manager.firestore.collection('daily_market_prices')
        
        # Process in batches of 500 (Firestore batch limit)
        batch_size = 500
        total_uploaded = 0
        
        for state, records in generated_data.items():
            logger.info(f"Uploading {len(records)} records for {state}")
            
            for i in range(0, len(records), batch_size):
                batch = gcp_manager.firestore.batch()
                batch_records = records[i:i + batch_size]
                
                for record in batch_records:
                    doc_id = record.pop('doc_id')  # Remove doc_id from document data
                    doc_ref = collection_ref.document(doc_id)
                    batch.set(doc_ref, record)
                
                # Commit batch
                batch.commit()
                total_uploaded += len(batch_records)
                
                logger.info(f"Uploaded batch {i//batch_size + 1} for {state}: {len(batch_records)} records")
        
        logger.info(f"Successfully uploaded {total_uploaded} historical records to Firestore")

    async def preview_generation(self):
        """Show preview of what will be generated"""
        print("🔍 HISTORICAL DATA GENERATION PREVIEW")
        print("=" * 50)
        
        await self.extract_current_data()
        
        for state in self.target_states:
            state_data = self.current_data[state]
            print(f"\n📊 {state} Analysis:")
            print(f"  • Current records: {state_data['total_records']:,}")
            print(f"  • Markets: {len(state_data['markets'])}")
            print(f"  • Commodities: {len(state_data['commodities'])}")
            print(f"  • Top commodities: {list(state_data['commodities'].keys())[:10]}")
            
            # Estimate historical records
            avg_records_per_day = state_data['total_records'] / 3  # Current data spans ~3 days
            estimated_historical = int(avg_records_per_day * 30 * self.months_back * 0.7)  # 70% coverage
            print(f"  • Estimated historical records: {estimated_historical:,}")
        
        print(f"\n⏰ Date Range: {self.months_back} months back from today")
        print(f"📈 Features:")
        print(f"  • Seasonal price variations")
        print(f"  • Daily market fluctuations")
        print(f"  • Realistic price trends")
        print(f"  • Same data structure as current records")
        
        print(f"\n💡 Use --generate flag to actually create and upload the data")


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Historical Market Data")
    parser.add_argument("--preview", action="store_true", help="Show preview without generating")
    parser.add_argument("--generate", action="store_true", help="Generate and upload historical data")
    parser.add_argument("--months", type=int, default=6, help="Number of months to generate (default: 6)")
    
    args = parser.parse_args()
    
    generator = HistoricalDataGenerator()
    generator.months_back = args.months
    
    if args.preview:
        await generator.preview_generation()
    elif args.generate:
        await generator.extract_current_data()
        result = await generator.generate_historical_data(preview_only=False)
        
        print("✅ HISTORICAL DATA GENERATION COMPLETED")
        print("=" * 50)
        print(f"📦 Total records created: {result['total_records']:,}")
        print(f"📅 Date range: {result['date_range']['start']} to {result['date_range']['end']}")
        print(f"🏛️ States:")
        for state, count in result['states'].items():
            print(f"  • {state}: {count:,} records")
    else:
        print("❌ Please specify either --preview or --generate")
        print("Usage:")
        print("  python scripts/generate_historical_data.py --preview")
        print("  python scripts/generate_historical_data.py --generate")


if __name__ == "__main__":
    asyncio.run(main()) 