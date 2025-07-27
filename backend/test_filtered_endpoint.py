#!/usr/bin/env python3
"""
Test Filtered Market Data Endpoint
==================================

Test the new /api/v1/market/filtered-data endpoint designed for Market Agent V3.
"""

import asyncio
import os
from datetime import datetime, timedelta

import aiohttp

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not available")

print("🧪 Testing Filtered Market Data Endpoint")
print("=" * 45)

# Backend configuration
BACKEND_URL = os.getenv("BACKEND_API_URL") or "http://localhost:8000"
ENDPOINT = f"{BACKEND_URL}/api/v1/market/filtered-data"


async def test_filtered_endpoint():
    """Test various filtering scenarios"""

    print(f"📡 Testing endpoint: {ENDPOINT}")
    print()

    # Test cases for Market Agent V3 scenarios
    test_cases = [
        {
            "name": "Basic State Filter - Karnataka",
            "params": {"state": "Karnataka"},
            "description": "Get all data for Karnataka (default 60 days)",
        },
        {
            "name": "State + Commodity Filter",
            "params": {"state": "Karnataka", "commodity": "tomato"},
            "description": "Get tomato data for Karnataka",
        },
        {
            "name": "State + Market Filter",
            "params": {"state": "Karnataka", "market": "bangalore"},
            "description": "Get Bangalore market data for Karnataka",
        },
        {
            "name": "Date Range Filter",
            "params": {
                "state": "Karnataka",
                "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d"),
            },
            "description": "Get Karnataka data for last 30 days",
        },
        {
            "name": "Multi-Filter Scenario",
            "params": {
                "state": "Karnataka",
                "commodity": "onion",
                "start_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d"),
            },
            "description": "Get onion data for Karnataka in last week",
        },
        {
            "name": "Tamil Nadu State",
            "params": {"state": "Tamil Nadu", "commodity": "tomato"},
            "description": "Get tomato data for Tamil Nadu",
        },
        {
            "name": "High Limit Test",
            "params": {"state": "Karnataka", "limit": 2000},
            "description": "Test higher limit for bulk data retrieval",
        },
    ]

    results = []

    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            print(f"🔍 Test {i}: {test_case['name']}")
            print(f"   Description: {test_case['description']}")
            print(f"   Parameters: {test_case['params']}")

            try:
                async with session.get(ENDPOINT, params=test_case["params"]) as response:
                    status = response.status
                    data = await response.json()

                    if status == 200:
                        success = data.get("success", False)
                        total_records = data.get("total_records", 0)
                        filters_applied = data.get("filters_applied", {})
                        date_range = data.get("date_range", {})

                        print(f"   ✅ SUCCESS: {total_records} records found")
                        print(f"   📊 Filters applied: {filters_applied}")
                        if date_range:
                            print(f"   📅 Date range: {date_range}")

                        # Sample a few records if available
                        if total_records > 0:
                            sample_records = data.get("data", [])[:3]
                            print("   📝 Sample records:")
                            for j, record in enumerate(sample_records, 1):
                                commodity = record.get("commodity", "N/A")
                                market = record.get("market", "N/A")
                                price = record.get("modal_price", 0)
                                date = record.get("date", "N/A")
                                print(
                                    f"      {j}. {commodity} in {market}: ₹{price}/tonne ({date})"
                                )

                        results.append(
                            {
                                "test": test_case["name"],
                                "status": "PASS",
                                "records": total_records,
                                "filters": filters_applied,
                            }
                        )
                    else:
                        error = data.get("detail", "Unknown error")
                        print(f"   ❌ FAILED: HTTP {status} - {error}")
                        results.append(
                            {
                                "test": test_case["name"],
                                "status": "FAIL",
                                "error": f"HTTP {status}: {error}",
                            }
                        )

            except Exception as e:
                print(f"   💥 EXCEPTION: {str(e)}")
                results.append({"test": test_case["name"], "status": "ERROR", "error": str(e)})

            print()

    return results


async def test_error_scenarios():
    """Test error handling scenarios"""

    print("🚨 Testing Error Scenarios")
    print("-" * 30)

    error_test_cases = [
        {
            "name": "Missing State Parameter",
            "params": {"commodity": "tomato"},
            "expected_status": 422,
            "description": "Should fail without required state parameter",
        },
        {
            "name": "Invalid Date Format",
            "params": {"state": "Karnataka", "start_date": "invalid-date"},
            "expected_status": 400,
            "description": "Should fail with invalid date format",
        },
        {
            "name": "Start Date After End Date",
            "params": {"state": "Karnataka", "start_date": "2025-01-28", "end_date": "2025-01-27"},
            "expected_status": 400,
            "description": "Should fail when start_date > end_date",
        },
        {
            "name": "Excessive Limit",
            "params": {"state": "Karnataka", "limit": 10000},
            "expected_status": 400,
            "description": "Should fail with limit > 5000",
        },
    ]

    error_results = []

    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(error_test_cases, 1):
            print(f"🧪 Error Test {i}: {test_case['name']}")
            print(f"   Description: {test_case['description']}")
            print(f"   Parameters: {test_case['params']}")

            try:
                async with session.get(ENDPOINT, params=test_case["params"]) as response:
                    status = response.status
                    data = await response.json()

                    if status == test_case["expected_status"]:
                        print(f"   ✅ EXPECTED ERROR: HTTP {status}")
                        error_results.append({"test": test_case["name"], "status": "PASS"})
                    else:
                        print(
                            f"   ❌ UNEXPECTED: Expected {test_case['expected_status']}, got {status}"
                        )
                        error_results.append({"test": test_case["name"], "status": "FAIL"})

            except Exception as e:
                print(f"   💥 EXCEPTION: {str(e)}")
                error_results.append({"test": test_case["name"], "status": "ERROR"})

            print()

    return error_results


async def main():
    """Run comprehensive endpoint tests"""

    print("🎯 Testing the new filtered market data endpoint for Market Agent V3")
    print("This endpoint supports smart filtering by state, commodity, market, and date range.")
    print()

    try:
        # Test successful scenarios
        success_results = await test_filtered_endpoint()

        # Test error scenarios
        error_results = await test_error_scenarios()

        # Summary
        print("=" * 45)
        print("🎉 FILTERED ENDPOINT TEST RESULTS")
        print("=" * 45)

        # Success tests summary
        success_tests = [r for r in success_results if r["status"] == "PASS"]
        failed_tests = [r for r in success_results if r["status"] in ["FAIL", "ERROR"]]

        print(f"✅ Successful Tests: {len(success_tests)}/{len(success_results)}")

        for result in success_tests:
            records = result.get("records", 0)
            print(f"   • {result['test']}: {records:,} records")

        if failed_tests:
            print(f"\n❌ Failed Tests: {len(failed_tests)}")
            for result in failed_tests:
                error = result.get("error", "Unknown error")
                print(f"   • {result['test']}: {error}")

        # Error tests summary
        error_success = [r for r in error_results if r["status"] == "PASS"]
        print(f"\n🚨 Error Handling: {len(error_success)}/{len(error_results)} passed")

        # Overall assessment
        total_success = len(success_tests) + len(error_success)
        total_tests = len(success_results) + len(error_results)

        print(f"\n📊 Overall: {total_success}/{total_tests} tests passed")

        if total_success == total_tests:
            print("\n🚀 ENDPOINT READY FOR MARKET AGENT V3!")
            print("   ✅ All filtering scenarios work correctly")
            print("   ✅ Error handling is proper")
            print("   ✅ Ready for agent integration")
            print()
            print("📋 Next steps:")
            print("   1. Deploy the backend with this new endpoint")
            print("   2. Update Market Agent V3 to use /filtered-data")
            print("   3. Test agent queries like 'tomato price in Bangalore'")
        else:
            print("\n⚠️  Some tests failed - review before deployment")

    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
