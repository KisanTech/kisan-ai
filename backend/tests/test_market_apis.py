#!/usr/bin/env python3
"""
Market APIs Test Script
======================

Comprehensive testing script for Kisan AI market data APIs.
Tests the new simplified market service functionality, data validation, and performance.

Features tested:
- Data retrieval with auto-fetch from Data.gov.in
- Firestore storage and retrieval
- Price update functionality  
- Cache behavior (no redundant API calls)
- Data consistency and validation

Usage: python test_market_apis.py
"""

import asyncio
import os
import sys
import time
from datetime import date, datetime

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.constants import DateFormats, FieldNames
from app.services.market_service import market_service
from app.utils.gcp.gcp_manager import gcp_manager


class MarketAPITester:
    """Comprehensive market API testing suite for the new simplified endpoints"""

    def __init__(self):
        self.test_results = {"passed": 0, "failed": 0, "tests": []}
        self.test_state = "Karnataka"  # Default test state
        self.test_date = datetime.now().date()

    def log_test(self, test_name: str, passed: bool, message: str, data: dict = None):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}: {message}")

        self.test_results["tests"].append(
            {"name": test_name, "passed": passed, "message": message, "data": data}
        )

        if passed:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1

    async def setup_tests(self):
        """Initialize GCP services for testing"""
        print("\n🔧 Setting up test environment...")
        
        try:
            await gcp_manager.initialize()
            self.log_test("Setup - GCP Initialization", True, "GCP services initialized successfully")
        except Exception as e:
            self.log_test("Setup - GCP Initialization", False, f"Failed to initialize GCP: {str(e)}")
            return False
        
        return True

    async def test_data_gov_fetch_and_store(self):
        """Test fetching fresh data from Data.gov.in and storing in Firestore"""
        print("\n🌐 Testing Data.gov.in Fetch and Firestore Storage...")

        try:
            # Clear any existing data first (for clean test)
            await self._clear_test_data()
            
            # Call get_market_data - should fetch from Data.gov.in since no data exists
            start_time = time.time()
            result = await market_service.get_market_data(
                state=self.test_state,
                date=self.test_date
            )
            fetch_time = (time.time() - start_time) * 1000

            # Validate response structure
            if not isinstance(result, dict):
                self.log_test("Data Fetch - Response Type", False, f"Wrong response type: {type(result)}")
                return

            # Check if data was successfully fetched
            success = result.get(FieldNames.SUCCESS, False)
            source = result.get("source", "unknown")
            data = result.get("data", [])

            if success and source == "data_gov_api":
                self.log_test(
                    "Data Fetch - From Data.gov.in", 
                    True, 
                    f"Successfully fetched {len(data)} records from Data.gov.in"
                )
            else:
                self.log_test(
                    "Data Fetch - From Data.gov.in", 
                    False, 
                    f"Failed to fetch from Data.gov.in. Success: {success}, Source: {source}"
                )
                return

            # Validate data quality
            if len(data) > 0:
                self.log_test("Data Fetch - Data Volume", True, f"Retrieved {len(data)} records")
                await self._validate_market_record(data[0], "Data.gov.in Fetch")
            else:
                self.log_test("Data Fetch - Data Volume", False, "No records retrieved")

            # Test performance (first fetch should be slower)
            if fetch_time < 15000:  # 15 seconds max for external API
                self.log_test("Data Fetch - Performance", True, f"Fetch completed in {fetch_time:.2f}ms")
            else:
                self.log_test("Data Fetch - Performance", False, f"Too slow: {fetch_time:.2f}ms")

        except Exception as e:
            self.log_test("Data Fetch - Exception", False, f"Error: {str(e)}")

    async def test_firestore_cache_behavior(self):
        """Test that subsequent calls use Firestore cache instead of Data.gov.in"""
        print("\n💾 Testing Firestore Cache Behavior...")

        try:
            # First call - should use cached data from previous test
            start_time = time.time()
            result1 = await market_service.get_market_data(
                state=self.test_state,
                date=self.test_date
            )
            first_call_time = (time.time() - start_time) * 1000

            # Validate it used Firestore cache
            source1 = result1.get("source", "unknown")
            success1 = result1.get(FieldNames.SUCCESS, False)

            if success1 and source1 == "firestore":
                self.log_test(
                    "Cache Behavior - Firestore Source", 
                    True, 
                    f"Correctly used Firestore cache with {len(result1.get('data', []))} records"
                )
            else:
                self.log_test(
                    "Cache Behavior - Firestore Source", 
                    False, 
                    f"Expected Firestore source but got: {source1}"
                )

            # Second call - should also use cache
            start_time = time.time()
            result2 = await market_service.get_market_data(
                state=self.test_state,
                date=self.test_date
            )
            second_call_time = (time.time() - start_time) * 1000

            # Both calls should be fast (using cache)
            cache_performance = first_call_time < 2000 and second_call_time < 2000
            self.log_test(
                "Cache Behavior - Performance", 
                cache_performance,
                f"Cache calls: {first_call_time:.2f}ms, {second_call_time:.2f}ms"
            )

            # Data should be consistent
            data1 = result1.get("data", [])
            data2 = result2.get("data", [])
            consistent_data = len(data1) == len(data2)
            self.log_test(
                "Cache Behavior - Data Consistency", 
                consistent_data,
                f"Both calls returned {len(data1)} records"
            )

        except Exception as e:
            self.log_test("Cache Behavior - Exception", False, f"Error: {str(e)}")

    async def test_price_update_functionality(self):
        """Test the crop price update functionality"""
        print("\n💰 Testing Price Update Functionality...")

        try:
            # First get some data to find a record to update
            result = await market_service.get_market_data(
                state=self.test_state,
                date=self.test_date
            )

            data = result.get("data", [])
            if not data:
                self.log_test("Price Update - No Data", False, "No data available for price update test")
                return

            # Pick the first record for testing
            test_record = data[0]
            original_price = test_record.get(FieldNames.PRICE, 0)
            
            # Convert to float for calculation (handle string prices from API)
            try:
                original_price_num = float(original_price) if isinstance(original_price, str) else original_price
            except (ValueError, TypeError):
                original_price_num = 0
                
            new_price = original_price_num + 10.50  # Increase by 10.50

            # Update the price
            update_result = await market_service.update_crop_price(
                state=test_record.get(FieldNames.STATE),
                market=test_record.get(FieldNames.MARKET),
                commodity=test_record.get(FieldNames.COMMODITY),
                date=self.test_date,
                price=new_price,
                updated_by="test_script"
            )

            # Validate update result
            update_success = update_result.get(FieldNames.SUCCESS, False)
            if update_success:
                self.log_test(
                    "Price Update - Success", 
                    True, 
                    f"Updated {test_record.get(FieldNames.COMMODITY)} price from ₹{original_price_num} to ₹{new_price}"
                )

                # Verify the update by fetching data again
                verify_result = await market_service.get_market_data(
                    state=self.test_state,
                    date=self.test_date
                )
                
                # Find the updated record
                verify_data = verify_result.get("data", [])
                updated_record = None
                for record in verify_data:
                    if (record.get(FieldNames.COMMODITY) == test_record.get(FieldNames.COMMODITY) and
                        record.get(FieldNames.MARKET) == test_record.get(FieldNames.MARKET)):
                        updated_record = record
                        break

                if updated_record and updated_record.get(FieldNames.PRICE) == new_price:
                    self.log_test(
                        "Price Update - Verification", 
                        True, 
                        f"Price update verified in database: ₹{updated_record.get(FieldNames.PRICE)}"
                    )
                else:
                    self.log_test(
                        "Price Update - Verification", 
                        False, 
                        "Updated price not reflected in database"
                    )

            else:
                self.log_test(
                    "Price Update - Success", 
                    False, 
                    f"Failed to update price: {update_result.get(FieldNames.MESSAGE, 'Unknown error')}"
                )

        except Exception as e:
            self.log_test("Price Update - Exception", False, f"Error: {str(e)}")

    async def test_invalid_scenarios(self):
        """Test invalid scenarios and error handling"""
        print("\n⚠️  Testing Invalid Scenarios...")

        # Test non-existent state
        try:
            result = await market_service.get_market_data(
                state="NonExistentState",
                date=self.test_date
            )
            
            data = result.get("data", [])
            if len(data) == 0:
                self.log_test(
                    "Invalid Scenarios - Non-existent State", 
                    True, 
                    "Correctly returned empty data for non-existent state"
                )
            else:
                self.log_test(
                    "Invalid Scenarios - Non-existent State", 
                    False, 
                    f"Expected empty data but got {len(data)} records"
                )

        except Exception as e:
            self.log_test("Invalid Scenarios - Non-existent State", False, f"Error: {str(e)}")

        # Test price update for non-existent record
        try:
            update_result = await market_service.update_crop_price(
                state=self.test_state,
                market="NonExistentMarket",
                commodity="NonExistentCrop",
                date=self.test_date,
                price=100.0,
                updated_by="test_script"
            )

            update_success = update_result.get(FieldNames.SUCCESS, True)  # Should be False
            if not update_success:
                self.log_test(
                    "Invalid Scenarios - Non-existent Record Update", 
                    True, 
                    "Correctly failed to update non-existent record"
                )
            else:
                self.log_test(
                    "Invalid Scenarios - Non-existent Record Update", 
                    False, 
                    "Should have failed to update non-existent record"
                )

        except Exception as e:
            self.log_test("Invalid Scenarios - Non-existent Record Update", False, f"Error: {str(e)}")

    async def _validate_market_record(self, record: dict, context: str):
        """Validate individual market record structure and data quality"""
        
        # Check required fields
        required_fields = [FieldNames.STATE, FieldNames.MARKET, FieldNames.COMMODITY, FieldNames.PRICE]
        
        for field in required_fields:
            if field in record and record[field] is not None:
                self.log_test(
                    f"{context} - {field} Field", 
                    True, 
                    f"{field}: {record[field]}"
                )
            else:
                self.log_test(
                    f"{context} - {field} Field", 
                    False, 
                    f"Missing or null field: {field}"
                )

        # Validate price is non-negative (0 is valid for no trading data)
        price = record.get(FieldNames.PRICE, 0)
        
        # Convert to float if it's a string
        try:
            price_num = float(price) if isinstance(price, str) else price
            if isinstance(price_num, (int, float)) and price_num >= 0:
                self.log_test(
                    f"{context} - Price Validity", 
                    True, 
                    f"Valid price: ₹{price_num}"
                )
            else:
                self.log_test(
                    f"{context} - Price Validity", 
                    False, 
                    f"Invalid price: {price}"
                )
        except (ValueError, TypeError):
            self.log_test(
                f"{context} - Price Validity", 
                False, 
                f"Invalid price format: {price}"
            )

        # Check metadata fields
        metadata_fields = [FieldNames.STORED_AT, FieldNames.DATA_SOURCE]
        for field in metadata_fields:
            if field in record:
                self.log_test(
                    f"{context} - {field} Metadata", 
                    True, 
                    f"{field}: {record[field]}"
                )

    async def test_date_parameter_handling(self):
        """Test different date parameter scenarios"""
        print("\n📅 Testing Date Parameter Handling...")

        try:
            # Test with today's date (default)
            result_today = await market_service.get_market_data(state=self.test_state)
            
            today_success = result_today.get(FieldNames.SUCCESS, False)
            today_date = result_today.get(FieldNames.DATE, "")
            
            expected_date = datetime.now().date().strftime(DateFormats.ISO_DATE)
            correct_date = today_date == expected_date
            
            self.log_test(
                "Date Handling - Default (Today)", 
                today_success and correct_date,
                f"Used default date: {today_date}"
            )

            # Test with explicit date
            from datetime import timedelta
            yesterday = datetime.now().date() - timedelta(days=1)
            
            result_yesterday = await market_service.get_market_data(
                state=self.test_state,
                date=yesterday
            )
            
            yesterday_success = result_yesterday.get(FieldNames.SUCCESS, False)
            yesterday_date = result_yesterday.get(FieldNames.DATE, "")
            expected_yesterday = yesterday.strftime(DateFormats.ISO_DATE)
            
            self.log_test(
                "Date Handling - Explicit Date", 
                yesterday_success and yesterday_date == expected_yesterday,
                f"Used explicit date: {yesterday_date}"
            )

        except Exception as e:
            self.log_test("Date Handling - Exception", False, f"Error: {str(e)}")

    async def _clear_test_data(self):
        """Clear test data from Firestore (for clean testing)"""
        try:
            # This is a helper method to clear data for testing
            # In a real scenario, you might want to use a test database
            date_str = self.test_date.strftime(DateFormats.ISO_DATE)
            
            # Query and delete documents for the test date
            docs = gcp_manager.firestore.collection("daily_market_prices")\
                     .where(FieldNames.STATE, "==", self.test_state)\
                     .where(FieldNames.DATE, "==", date_str)\
                     .stream()
            
            deleted_count = 0
            for doc in docs:
                doc.reference.delete()
                deleted_count += 1
            
            if deleted_count > 0:
                print(f"🧹 Cleared {deleted_count} test records from Firestore")
            
        except Exception as e:
            print(f"⚠️  Could not clear test data: {str(e)}")

    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Starting Kisan AI Market APIs Test Suite")
        print("=" * 60)
        
        # Setup
        setup_success = await self.setup_tests()
        if not setup_success:
            print("❌ Setup failed. Cannot continue with tests.")
            return

        # Run all test categories
        await self.test_data_gov_fetch_and_store()
        await self.test_firestore_cache_behavior()
        await self.test_price_update_functionality()
        await self.test_date_parameter_handling()
        await self.test_invalid_scenarios()

        # Print summary
        self._print_summary()

    def _print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)

        total_tests = self.test_results["passed"] + self.test_results["failed"]
        pass_rate = (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0

        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📊 Pass Rate: {pass_rate:.1f}%")

        if self.test_results["failed"] > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.test_results["tests"]:
                if not test["passed"]:
                    print(f"  - {test['name']}: {test['message']}")

        # Overall status
        if self.test_results["failed"] == 0:
            print("\n🎉 ALL TESTS PASSED! Kisan AI Market APIs are working perfectly! ✨")
        else:
            print("\n⚠️  Some tests failed. Please review and fix issues.")

        print(f"\n🌾 Tested with state: {self.test_state}")
        print(f"📅 Tested with date: {self.test_date}")


async def main():
    """Run the market API test suite"""
    tester = MarketAPITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
