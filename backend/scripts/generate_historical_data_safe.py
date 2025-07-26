#!/usr/bin/env python3
"""
Safe Historical Market Data Generator for Trend Analysis
========================================================

SAFETY-FIRST approach for generating historical data to enable trend analysis.
Matches EXACT document structure from existing Firestore data.

Key Features:
- Exact field structure matching (all prices as strings)
- Focus on trend-enabling data for queries like "tomatoes in Bangalore vs Mysore"
- Small test mode before bulk generation
- Realistic seasonal and market variations
- Safe batch processing with error handling

Usage:
    python scripts/generate_historical_data_safe.py --test      # Generate 1 week test data
    python scripts/generate_historical_data_safe.py --preview   # Show what will be generated
    python scripts/generate_historical_data_safe.py --generate  # Generate full 6 months
"""

import asyncio
import copy
import json
import os
import random
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.constants import DateFormats, Separators
from app.utils.gcp.gcp_manager import gcp_manager
from app.utils.logger import logger


class SafeHistoricalDataGenerator:
    def __init__(self):
        self.target_states = ['Karnataka', 'Tamil Nadu', 'Punjab']
        self.months_back = 6
        self.current_data = {}
        
        # Focus on key commodities for trend analysis
        self.trend_commodities = {
            'Karnataka': ['Tomato', 'Onion', 'Potato', 'Cabbage', 'Beans', 'Beetroot', 'Brinjal'],
            'Tamil Nadu': ['Tomato', 'Onion', 'Potato', 'Cabbage', 'Amaranthus', 'Papaya', 'Banana - Green'],
            'Punjab': ['Tomato', 'Onion', 'Potato', 'Cabbage', 'Carrot', 'Cauliflower', 'Green Chilli']
        }
        
        # Realistic seasonal patterns for agricultural commodities
        self.seasonal_patterns = {
            'Karnataka': {
                1: 0.85, 2: 0.90, 3: 1.05, 4: 1.15, 5: 1.10, 6: 0.95, 7: 1.00
            },
            'Tamil Nadu': {
                1: 0.90, 2: 0.95, 3: 1.10, 4: 1.20, 5: 1.15, 6: 1.00, 7: 1.00
            },
            'Punjab': {
                1: 0.80, 2: 0.85, 3: 1.00, 4: 1.10, 5: 1.15, 6: 0.95, 7: 1.00
            }
        }

    async def analyze_existing_structure(self):
        """Analyze existing data structure for exact replication"""
        logger.info("Analyzing existing data structure for safety")
        
        await gcp_manager.initialize()
        collection_ref = gcp_manager.firestore.collection('daily_market_prices')
        
        # Get sample documents to extract exact structure
        docs = collection_ref.limit(5).stream()
        
        sample_structure = None
        for doc in docs:
            sample_structure = doc.to_dict()
            break
        
        if sample_structure:
            logger.info("Sample document structure analyzed", fields=list(sample_structure.keys()))
            return sample_structure
        else:
            raise Exception("No existing documents found to analyze structure")

    async def extract_commodity_patterns(self):
        """Extract patterns for specific commodities that enable trend analysis"""
        logger.info("Extracting commodity patterns for trend analysis")
        
        await gcp_manager.initialize()
        collection_ref = gcp_manager.firestore.collection('daily_market_prices')
        
        for state in self.target_states:
            logger.info(f"Analyzing {state} commodity patterns")
            
            state_data = {
                'commodities': {},
                'markets': set(),
                'districts': set()
            }
            
            # Get all documents for this state
            docs = collection_ref.where('state', '==', state).stream()
            
            for doc in docs:
                doc_data = doc.to_dict()
                
                commodity = doc_data.get('commodity', 'Unknown')
                market = doc_data.get('market', 'Unknown')
                district = doc_data.get('district', 'Unknown')
                
                # Focus only on trend commodities
                if commodity not in self.trend_commodities.get(state, []):
                    continue
                
                state_data['markets'].add(market)
                state_data['districts'].add(district)
                
                if commodity not in state_data['commodities']:
                    state_data['commodities'][commodity] = {
                        'prices': [],
                        'markets': set(),
                        'varieties': set(),
                        'grades': set(),
                        'districts': set(),
                        'sample_doc': copy.deepcopy(doc_data)  # Store exact structure
                    }
                
                # Extract price data (stored as strings)
                try:
                    modal_price = int(doc_data.get('modal_price', '0'))
                    min_price = int(doc_data.get('min_price', str(int(modal_price * 0.9))))
                    max_price = int(doc_data.get('max_price', str(int(modal_price * 1.1))))
                    
                    if modal_price > 0:
                        state_data['commodities'][commodity]['prices'].append({
                            'modal': modal_price,
                            'min': min_price,
                            'max': max_price
                        })
                except:
                    continue
                
                # Store metadata
                state_data['commodities'][commodity]['markets'].add(market)
                state_data['commodities'][commodity]['varieties'].add(doc_data.get('variety', 'Common'))
                state_data['commodities'][commodity]['grades'].add(doc_data.get('grade', 'Medium'))
                state_data['commodities'][commodity]['districts'].add(district)
            
            # Convert sets to lists
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
                f"Extracted {state} patterns",
                trend_commodities=len(state_data['commodities']),
                markets=len(state_data['markets'])
            )

    def calculate_realistic_price(self, base_price: int, state: str, month: int, day: int, commodity: str) -> int:
        """Calculate realistic price with seasonal and daily variations"""
        
        # Apply seasonal variation
        seasonal_multiplier = self.seasonal_patterns.get(state, {}).get(month, 1.0)
        seasonal_price = base_price * seasonal_multiplier
        
        # Add commodity-specific patterns
        commodity_patterns = {
            'Tomato': {'volatility': 0.15, 'trend': 'seasonal'},
            'Onion': {'volatility': 0.25, 'trend': 'high_variation'},
            'Potato': {'volatility': 0.10, 'trend': 'stable'},
            'Cabbage': {'volatility': 0.12, 'trend': 'seasonal'},
        }
        
        commodity_config = commodity_patterns.get(commodity, {'volatility': 0.10, 'trend': 'stable'})
        volatility = commodity_config['volatility']
        
        # Daily market fluctuations (more realistic patterns)
        if day <= 10:  # Early month - post-harvest or restocking
            daily_variation = random.uniform(0.95, 1.05)
        elif day <= 20:  # Mid month - normal trading
            daily_variation = random.uniform(0.92, 1.08)
        else:  # End month - clearing inventory
            daily_variation = random.uniform(0.88, 1.12)
        
        # Add random market noise based on commodity volatility
        noise = random.uniform(1 - volatility, 1 + volatility)
        
        final_price = seasonal_price * daily_variation * noise
        return max(50, int(final_price))  # Minimum price of ₹50

    def create_historical_document(self, sample_doc: Dict, state: str, date_obj: datetime, 
                                 commodity: str, market: str, prices: Dict[str, int]) -> Dict[str, Any]:
        """Create historical document with exact structure matching"""
        
        # Copy the sample document structure
        historical_doc = copy.deepcopy(sample_doc)
        
        # Update with historical data
        date_str = date_obj.strftime(DateFormats.ISO_DATE)
        arrival_date = date_obj.strftime("%d/%m/%Y")
        
        historical_doc.update({
            'state': state,
            'date': date_str,
            'market': market,
            'commodity': commodity,
            'arrival_date': arrival_date,
            'modal_price': str(prices['modal']),
            'min_price': str(prices['min']),
            'max_price': str(prices['max']),
            'data_source': 'Generated Historical Data for Trends',
            'stored_at': datetime.now(),
            'ttl': datetime.now() + timedelta(days=365)  # 1 year TTL
        })
        
        return historical_doc

    def create_document_id(self, state: str, date_str: str, market: str, commodity: str) -> str:
        """Create document ID matching existing format exactly"""
        clean_market = market.replace(Separators.SLASH, Separators.UNDERSCORE).replace(
            Separators.SPACE, Separators.UNDERSCORE
        )
        clean_commodity = commodity.replace(Separators.SLASH, Separators.UNDERSCORE).replace(
            Separators.SPACE, Separators.UNDERSCORE
        )
        
        return f"{state}{Separators.UNDERSCORE}{date_str}{Separators.UNDERSCORE}{clean_market}{Separators.UNDERSCORE}{clean_commodity}"

    async def generate_historical_data(self, test_mode: bool = False, preview_only: bool = True) -> Dict[str, Any]:
        """Generate historical data with focus on trend analysis"""
        
        if test_mode:
            # Test mode: only 1 week of data
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            logger.info("TEST MODE: Generating 1 week of data")
        else:
            # Full mode: 6 months of data
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30 * self.months_back)
            logger.info(f"FULL MODE: Generating {self.months_back} months of data")
        
        logger.info(f"Date range: {start_date} to {end_date}")
        
        generated_data = {}
        total_records = 0
        
        for state in self.target_states:
            if state not in self.current_data:
                logger.warning(f"No data patterns found for {state}, skipping")
                continue
            
            state_data = self.current_data[state]
            generated_data[state] = []
            
            logger.info(f"Generating historical data for {state}")
            
            # Generate data for each date
            current_date = start_date
            while current_date < end_date:
                # Skip future dates
                if current_date >= datetime.now().date():
                    current_date += timedelta(days=1)
                    continue
                
                date_str = current_date.strftime(DateFormats.ISO_DATE)
                
                # Generate for trend commodities only
                for commodity, commodity_data in state_data['commodities'].items():
                    if not commodity_data['prices']:
                        continue
                    
                    # Calculate average base price
                    avg_modal = sum(p['modal'] for p in commodity_data['prices']) / len(commodity_data['prices'])
                    avg_min = sum(p['min'] for p in commodity_data['prices']) / len(commodity_data['prices'])
                    avg_max = sum(p['max'] for p in commodity_data['prices']) / len(commodity_data['prices'])
                    
                    # Generate for 70-90% of available markets (realistic coverage)
                    available_markets = commodity_data['markets']
                    if not available_markets:
                        continue
                    
                    num_markets = max(1, int(len(available_markets) * random.uniform(0.7, 0.9)))
                    selected_markets = random.sample(available_markets, min(num_markets, len(available_markets)))
                    
                    for market in selected_markets:
                        # Generate realistic prices
                        modal_price = self.calculate_realistic_price(
                            avg_modal, state, current_date.month, current_date.day, commodity
                        )
                        min_price = self.calculate_realistic_price(
                            avg_min, state, current_date.month, current_date.day, commodity
                        )
                        max_price = self.calculate_realistic_price(
                            avg_max, state, current_date.month, current_date.day, commodity
                        )
                        
                        # Ensure logical price relationships
                        if min_price > modal_price:
                            min_price = int(modal_price * 0.9)
                        if max_price < modal_price:
                            max_price = int(modal_price * 1.1)
                        
                        prices = {
                            'modal': modal_price,
                            'min': min_price,
                            'max': max_price
                        }
                        
                        # Create document with exact structure
                        sample_doc = commodity_data['sample_doc']
                        historical_doc = self.create_historical_document(
                            sample_doc, state, current_date, commodity, market, prices
                        )
                        
                        # Add document ID for tracking
                        doc_id = self.create_document_id(state, date_str, market, commodity)
                        historical_doc['_doc_id'] = doc_id
                        
                        generated_data[state].append(historical_doc)
                        total_records += 1
                
                current_date += timedelta(days=1)
            
            logger.info(f"Generated {len(generated_data[state])} records for {state}")
        
        logger.info(f"Total records generated: {total_records}")
        
        if not preview_only:
            await self.upload_to_firestore(generated_data)
        
        return {
            'total_records': total_records,
            'states': {state: len(records) for state, records in generated_data.items()},
            'date_range': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'test_mode': test_mode,
            'sample_data': {
                state: records[:2] for state, records in generated_data.items()
            }
        }

    async def upload_to_firestore(self, generated_data: Dict[str, List[Dict]]):
        """Safely upload data in small batches with error handling"""
        logger.info("Starting safe upload to Firestore")
        
        collection_ref = gcp_manager.firestore.collection('daily_market_prices')
        batch_size = 100  # Smaller batches for safety
        total_uploaded = 0
        errors = []
        
        for state, records in generated_data.items():
            logger.info(f"Uploading {len(records)} records for {state}")
            
            for i in range(0, len(records), batch_size):
                try:
                    batch = gcp_manager.firestore.batch()
                    batch_records = records[i:i + batch_size]
                    
                    for record in batch_records:
                        doc_id = record.pop('_doc_id')  # Remove tracking field
                        doc_ref = collection_ref.document(doc_id)
                        batch.set(doc_ref, record)
                    
                    # Commit batch
                    batch.commit()
                    total_uploaded += len(batch_records)
                    
                    logger.info(f"Uploaded batch {i//batch_size + 1} for {state}: {len(batch_records)} records")
                    
                    # Small delay between batches for safety
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    error_msg = f"Failed to upload batch {i//batch_size + 1} for {state}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
        
        logger.info(f"Upload completed: {total_uploaded} records uploaded, {len(errors)} errors")
        
        if errors:
            logger.warning("Upload errors occurred", errors=errors[:5])  # Log first 5 errors
        
        return total_uploaded, errors

    async def preview_generation(self, test_mode: bool = False):
        """Show detailed preview of what will be generated"""
        mode_text = "TEST (1 week)" if test_mode else f"FULL ({self.months_back} months)"
        
        print(f"🔍 SAFE HISTORICAL DATA GENERATION - {mode_text}")
        print("=" * 60)
        
        await self.extract_commodity_patterns()
        
        total_estimated = 0
        
        for state in self.target_states:
            if state not in self.current_data:
                continue
                
            state_data = self.current_data[state]
            print(f"\n📊 {state} Trend Analysis Preparation:")
            print(f"  • Focus commodities: {len(state_data['commodities'])}")
            print(f"  • Available markets: {len(state_data['markets'])}")
            
            # Show commodity-market combinations for trend analysis
            trend_examples = []
            for commodity, comm_data in state_data['commodities'].items():
                if len(comm_data['markets']) >= 2:  # Good for comparison
                    markets = comm_data['markets'][:3]  # Show first 3 markets
                    avg_price = sum(p['modal'] for p in comm_data['prices']) / len(comm_data['prices'])
                    trend_examples.append(f"    • {commodity}: {markets} (avg ₹{avg_price:.0f})")
            
            if trend_examples:
                print("  • Trend analysis ready for:")
                for example in trend_examples[:5]:  # Show top 5
                    print(example)
            
            # Estimate records
            days = 7 if test_mode else (30 * self.months_back)
            estimated = sum(len(comm_data['markets']) for comm_data in state_data['commodities'].values()) * days * 0.8
            total_estimated += estimated
            print(f"  • Estimated records: {int(estimated):,}")
        
        print(f"\n📈 Trend Analysis Capabilities:")
        print(f"  • Query: 'tomato prices in Bangalore vs Mysore over 6 months'")
        print(f"  • Query: 'onion price trends in Tamil Nadu markets'")
        print(f"  • Query: 'seasonal variation of potato in Punjab'")
        
        print(f"\n⚡ Safety Features:")
        print(f"  • Exact document structure matching")
        print(f"  • Small batch uploads (100 records/batch)")
        print(f"  • Error handling and logging")
        print(f"  • Test mode available")
        
        print(f"\n📦 Total estimated records: {int(total_estimated):,}")
        print(f"💡 Run with --test flag to generate 1 week first!")


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Safe Historical Market Data Generator")
    parser.add_argument("--test", action="store_true", help="Generate 1 week test data")
    parser.add_argument("--preview", action="store_true", help="Show preview without generating")
    parser.add_argument("--generate", action="store_true", help="Generate and upload historical data")
    parser.add_argument("--months", type=int, default=6, help="Number of months to generate (default: 6)")
    
    args = parser.parse_args()
    
    generator = SafeHistoricalDataGenerator()
    generator.months_back = args.months
    
    if args.preview:
        await generator.preview_generation(test_mode=args.test)
    elif args.generate:
        await generator.extract_commodity_patterns()
        result = await generator.generate_historical_data(test_mode=args.test, preview_only=False)
        
        mode_text = "TEST" if args.test else "FULL"
        print(f"✅ {mode_text} HISTORICAL DATA GENERATION COMPLETED")
        print("=" * 60)
        print(f"📦 Total records created: {result['total_records']:,}")
        print(f"📅 Date range: {result['date_range']['start']} to {result['date_range']['end']}")
        print(f"🏛️ States:")
        for state, count in result['states'].items():
            print(f"  • {state}: {count:,} records")
        
        if args.test:
            print(f"\n🧪 Test completed successfully!")
            print(f"💡 Run without --test flag to generate full 6 months")
    else:
        print("❌ Please specify either --preview, --test, or --generate")
        print("Usage examples:")
        print("  python scripts/generate_historical_data_safe.py --preview")
        print("  python scripts/generate_historical_data_safe.py --test")
        print("  python scripts/generate_historical_data_safe.py --generate")


if __name__ == "__main__":
    asyncio.run(main()) 