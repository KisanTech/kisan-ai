#!/usr/bin/env python3
"""
Market APIs Test Script
======================

Comprehensive testing script for Project Kisan market data APIs.
Tests functionality, data validation, and performance.

Usage: python test_market_apis.py
"""

import asyncio
import os
import sys
import time

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.v1.market_prices import get_current_prices, refresh_market_cache
from app.models.market import CacheRefreshResponse, MarketPricesResponse


class MarketAPITester:
    """Comprehensive market API testing suite"""

    def __init__(self):
        self.test_results = {"passed": 0, "failed": 0, "tests": []}

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

    async def test_cache_refresh_api(self):
        """Test cache refresh endpoint"""
        print("\n🔄 Testing Cache Refresh API...")

        try:
            start_time = time.time()
            result = await refresh_market_cache(state="Karnataka")
            latency = (time.time() - start_time) * 1000

            # Validate response type
            if isinstance(result, CacheRefreshResponse):
                self.log_test(
                    "Cache Refresh - Response Type",
                    True,
                    f"Correct response type: {type(result).__name__}",
                )
            else:
                self.log_test(
                    "Cache Refresh - Response Type",
                    False,
                    f"Wrong response type: {type(result).__name__}",
                )
                return

            # Validate response fields
            required_fields = ["status", "state", "records_cached", "refreshed_at"]
            for field in required_fields:
                if hasattr(result, field):
                    self.log_test(
                        f"Cache Refresh - {field} field",
                        True,
                        f"{field} present: {getattr(result, field)}",
                    )
                else:
                    self.log_test(
                        f"Cache Refresh - {field} field", False, f"Missing required field: {field}"
                    )

            # Validate data quality
            if result.records_cached > 0:
                self.log_test(
                    "Cache Refresh - Data Volume",
                    True,
                    f"Successfully cached {result.records_cached} records",
                )
            else:
                self.log_test("Cache Refresh - Data Volume", False, "No records cached")

            # Validate performance
            if latency < 10000:  # 10 seconds
                self.log_test("Cache Refresh - Performance", True, f"Completed in {latency:.2f}ms")
            else:
                self.log_test("Cache Refresh - Performance", False, f"Too slow: {latency:.2f}ms")

        except Exception as e:
            self.log_test("Cache Refresh - Exception", False, f"Error: {str(e)}")

    async def test_current_prices_api(self):
        """Test current prices endpoint with various parameters"""
        print("\n💰 Testing Current Prices API...")

        test_cases = [
            {
                "name": "No Filters",
                "params": {"crop": None, "market": None, "state": None},
                "expect_data": True,
            },
            {
                "name": "Filter by Crop",
                "params": {"crop": "Tomato", "market": None, "state": None},
                "expect_data": True,
            },
            {
                "name": "Filter by State",
                "params": {"crop": None, "market": None, "state": "Karnataka"},
                "expect_data": True,
            },
            {
                "name": "Non-existent Crop",
                "params": {"crop": "NonExistentCrop123", "market": None, "state": None},
                "expect_data": False,
            },
            {
                "name": "Filter by Market",
                "params": {"crop": None, "market": "Bangalore", "state": None},
                "expect_data": True,
            },
        ]

        for test_case in test_cases:
            await self._test_single_price_query(test_case)

    async def _test_single_price_query(self, test_case: dict):
        """Test a single price query"""
        test_name = f"Price Query - {test_case['name']}"

        try:
            start_time = time.time()
            result = await get_current_prices(**test_case["params"])
            latency = (time.time() - start_time) * 1000

            # Validate response type
            if not isinstance(result, MarketPricesResponse):
                self.log_test(
                    test_name + " - Type", False, f"Wrong response type: {type(result).__name__}"
                )
                return

            # Validate structure
            if hasattr(result, "prices") and hasattr(result, "metadata"):
                self.log_test(test_name + " - Structure", True, "Response has required fields")
            else:
                self.log_test(test_name + " - Structure", False, "Missing required fields")
                return

            # Validate data expectation
            has_data = len(result.prices) > 0
            if test_case["expect_data"]:
                if has_data:
                    self.log_test(
                        test_name + " - Data Present", True, f"Found {len(result.prices)} records"
                    )

                    # Validate first record if present
                    await self._validate_price_record(result.prices[0], test_name)
                else:
                    self.log_test(
                        test_name + " - Data Present", False, "Expected data but got empty results"
                    )
            else:
                if not has_data:
                    self.log_test(
                        test_name + " - No Data", True, "Correctly returned empty results"
                    )
                else:
                    self.log_test(
                        test_name + " - No Data",
                        False,
                        f"Expected no data but got {len(result.prices)} records",
                    )

            # Validate performance (should be fast due to caching)
            if latency < 1000:  # 1 second
                self.log_test(test_name + " - Performance", True, f"Fast response: {latency:.2f}ms")
            else:
                self.log_test(
                    test_name + " - Performance", False, f"Slow response: {latency:.2f}ms"
                )

        except Exception as e:
            self.log_test(test_name + " - Exception", False, f"Error: {str(e)}")

    async def _validate_price_record(self, record, test_context: str):
        """Validate individual price record data quality"""

        # Required fields
        required_fields = [
            "state",
            "district",
            "market",
            "commodity",
            "variety",
            "grade",
            "arrival_date",
            "min_price_rs",
            "max_price_rs",
            "modal_price_rs",
        ]

        for field in required_fields:
            if hasattr(record, field) and getattr(record, field) is not None:
                self.log_test(
                    f"{test_context} - {field}", True, f"{field}: {getattr(record, field)}"
                )
            else:
                self.log_test(f"{test_context} - {field}", False, f"Missing or null field: {field}")

        # Price validation
        prices = [record.min_price_rs, record.max_price_rs, record.modal_price_rs]

        # All prices should be positive
        all_positive = all(p > 0 for p in prices)
        self.log_test(
            f"{test_context} - Positive Prices", all_positive, f"All prices positive: {prices}"
        )

        # Min <= Modal <= Max
        price_order = record.min_price_rs <= record.modal_price_rs <= record.max_price_rs
        self.log_test(
            f"{test_context} - Price Order",
            price_order,
            f"Min({record.min_price_rs}) <= Modal({record.modal_price_rs}) <= "
            f"Max({record.max_price_rs})",
        )

        # Reasonable price range (₹0.1 to ₹10000 per kg)
        reasonable_range = all(0.1 <= p <= 10000 for p in prices)
        self.log_test(
            f"{test_context} - Price Range",
            reasonable_range,
            f"Prices in reasonable range: {prices}",
        )

        # Currency should be INR
        correct_currency = record.currency == "INR"
        self.log_test(
            f"{test_context} - Currency", correct_currency, f"Currency: {record.currency}"
        )

    async def test_data_consistency(self):
        """Test data consistency across multiple calls"""
        print("\n🔍 Testing Data Consistency...")

        try:
            # Make two identical calls
            result1 = await get_current_prices(crop="Tomato", state="Karnataka")
            await asyncio.sleep(0.1)  # Small delay
            result2 = await get_current_prices(crop="Tomato", state="Karnataka")

            # Should get same results (due to caching)
            same_count = len(result1.prices) == len(result2.prices)
            self.log_test(
                "Data Consistency - Count",
                same_count,
                f"Call 1: {len(result1.prices)}, Call 2: {len(result2.prices)}",
            )

            # Same source
            same_source = result1.metadata.source == result2.metadata.source
            self.log_test(
                "Data Consistency - Source",
                same_source,
                f"Both calls from: {result1.metadata.source}",
            )

        except Exception as e:
            self.log_test("Data Consistency - Exception", False, f"Error: {str(e)}")

    async def test_cache_functionality(self):
        """Test cache functionality and performance"""
        print("\n⚡ Testing Cache Functionality...")

        try:
            # First call (should populate cache)
            start_time = time.time()
            result1 = await get_current_prices(state="Karnataka")
            first_call_time = (time.time() - start_time) * 1000

            # Second call (should use cache)
            start_time = time.time()
            result2 = await get_current_prices(state="Karnataka")
            second_call_time = (time.time() - start_time) * 1000

            # Second call should be much faster
            cache_effective = second_call_time < first_call_time / 2
            self.log_test(
                "Cache Performance",
                cache_effective,
                f"First: {first_call_time:.2f}ms, Second: {second_call_time:.2f}ms",
            )

            # Should get same data
            same_data = len(result1.prices) == len(result2.prices)
            self.log_test(
                "Cache Data Integrity",
                same_data,
                f"Both calls returned {len(result1.prices)} records",
            )

            # Check cache age in metadata
            if (
                hasattr(result2.metadata, "cache_age_hours")
                and result2.metadata.cache_age_hours is not None
            ):
                self.log_test(
                    "Cache Age Tracking",
                    True,
                    f"Cache age: {result2.metadata.cache_age_hours} hours",
                )
            else:
                self.log_test("Cache Age Tracking", False, "Cache age not tracked")

        except Exception as e:
            self.log_test("Cache Functionality - Exception", False, f"Error: {str(e)}")

    async def analyze_data_quality(self):
        """Analyze overall data quality"""
        print("\n📊 Analyzing Data Quality...")

        try:
            # Get all data
            result = await get_current_prices(state="Karnataka")

            if not result.prices:
                self.log_test("Data Quality - No Data", False, "No data available for analysis")
                return

            # Analyze commodities
            commodities = {record.commodity for record in result.prices}
            self.log_test(
                "Data Quality - Commodity Variety",
                len(commodities) > 5,
                f"Found {len(commodities)} unique commodities",
            )

            # Analyze markets
            markets = {record.market for record in result.prices}
            self.log_test(
                "Data Quality - Market Variety",
                len(markets) > 3,
                f"Found {len(markets)} unique markets",
            )

            # Analyze price ranges
            all_prices = []
            for record in result.prices:
                all_prices.extend([record.min_price_rs, record.max_price_rs, record.modal_price_rs])

            min_price = min(all_prices)
            max_price = max(all_prices)
            avg_price = sum(all_prices) / len(all_prices)

            self.log_test(
                "Data Quality - Price Analysis",
                True,
                f"Price range: ₹{min_price:.2f} - ₹{max_price:.2f}, Average: ₹{avg_price:.2f}",
            )

            # Check for data freshness
            fresh_data = "2025" in result.prices[0].arrival_date
            self.log_test(
                "Data Quality - Freshness",
                fresh_data,
                f"Sample date: {result.prices[0].arrival_date}",
            )

        except Exception as e:
            self.log_test("Data Quality Analysis - Exception", False, f"Error: {str(e)}")

    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Starting Market APIs Test Suite")
        print("=" * 50)

        # Run all test categories
        await self.test_cache_refresh_api()
        await self.test_current_prices_api()
        await self.test_data_consistency()
        await self.test_cache_functionality()
        await self.analyze_data_quality()

        # Print summary
        self._print_summary()

    def _print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📋 TEST SUMMARY")
        print("=" * 50)

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
            print("\n🎉 ALL TESTS PASSED! Market APIs are working perfectly! ✨")
        else:
            print("\n⚠️  Some tests failed. Please review and fix issues.")


async def main():
    """Run the market API test suite"""
    tester = MarketAPITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
