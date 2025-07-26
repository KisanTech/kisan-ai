"""
Test Script for Government Schemes RAG Agent
==========================================

This script tests the government schemes RAG agent functionality.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from government_schemes_agent.startup import (
    initialize_government_schemes_agent,
    setup_sample_documents,
    check_environment,
)
from government_schemes_agent.agent import get_government_schemes_agent
from government_schemes_agent.tools import (
    check_scheme_eligibility,
    get_scheme_categories,
    validate_documents,
)


async def test_environment_setup():
    """Test environment setup and configuration."""
    print("🔧 Testing Environment Setup...")

    env_check = check_environment()
    print(f"  Google Cloud Project: {env_check['environment_variables']['google_cloud_project']}")
    print(f"  Documents Directory: {env_check['documents_directory_exists']}")
    print(f"  Document Count: {env_check['document_count']}")
    print(f"  Ready: {env_check['ready_for_initialization']}")

    if not env_check["ready_for_initialization"]:
        print("❌ Environment not ready. Please set GOOGLE_CLOUD_PROJECT.")
        return False

    print("✅ Environment setup OK")
    return True


async def test_sample_documents():
    """Test sample document creation."""
    print("\n📄 Testing Sample Documents...")

    success = await setup_sample_documents()
    if success:
        print("✅ Sample documents created successfully")

        # List created documents
        schemes_path = os.getenv("SCHEMES_DOCUMENTS_PATH", "./schemes_documents")
        if os.path.exists(schemes_path):
            docs = [f for f in os.listdir(schemes_path) if f.endswith(".txt")]
            print(f"  Created {len(docs)} sample documents:")
            for doc in docs:
                print(f"    - {doc}")
        return True
    else:
        print("❌ Failed to create sample documents")
        return False


async def test_agent_initialization():
    """Test agent initialization."""
    print("\n🚀 Testing Agent Initialization...")

    try:
        result = await initialize_government_schemes_agent()

        if result["success"]:
            print("✅ Agent initialized successfully")
            print(f"  Corpus Status: {result['corpus_status']['status']}")
            print(f"  File Count: {result['corpus_status'].get('file_count', 0)}")
            return True
        else:
            print(f"❌ Agent initialization failed: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Agent initialization error: {e}")
        return False


async def test_tools():
    """Test individual tools."""
    print("\n🔧 Testing Tools...")

    # Test scheme categories
    print("  Testing scheme categories...")
    categories = get_scheme_categories()
    if categories.get("categories"):
        print(f"    ✅ Found {categories['total_categories']} categories")
    else:
        print(f"    ❌ Categories error: {categories.get('error', 'Unknown')}")

    # Test eligibility checking
    print("  Testing eligibility checking...")
    eligibility = check_scheme_eligibility(
        query="Which schemes am I eligible for?",
        land_size="2 acres",
        crop_type="rice",
        farmer_category="small",
    )

    if eligibility.get("eligible_schemes"):
        print(f"    ✅ Found {len(eligibility['eligible_schemes'])} eligible schemes")
        for scheme in eligibility["eligible_schemes"][:2]:  # Show first 2
            print(f"      - {scheme['scheme_name']}")
    else:
        print(f"    ❌ Eligibility check error: {eligibility.get('error', 'Unknown')}")

    # Test document validation
    print("  Testing document validation...")
    validation = validate_documents(
        scheme_type="pm_kisan", available_documents=["aadhaar_card", "land_records", "bank_account"]
    )

    if validation.get("valid") is not None:
        status = "✅ Valid" if validation["valid"] else "⚠️ Missing documents"
        print(f"    {status} (Completion: {validation.get('completion_percentage', 0):.0f}%)")
    else:
        print(f"    ❌ Validation error: {validation.get('error', 'Unknown')}")


async def test_agent_queries():
    """Test agent query functionality."""
    print("\n💬 Testing Agent Queries...")

    try:
        agent = await get_government_schemes_agent()

        if not agent or not agent.initialized:
            print("❌ Agent not available for testing")
            return False

        # Test queries
        test_queries = [
            {
                "query": "I need subsidy for drip irrigation",
                "description": "English irrigation query",
            },
            {
                "query": "मुझे धान की फसल के लिए बीमा चाहिए",
                "description": "Hindi crop insurance query",
            },
            {"query": "What is PM-KISAN scheme?", "description": "Scheme information query"},
        ]

        for i, test_case in enumerate(test_queries, 1):
            print(f"  Query {i}: {test_case['description']}")
            print(f"    Input: {test_case['query'][:50]}...")

            try:
                result = await agent.query_schemes(test_case["query"])

                if result.get("success"):
                    response_preview = result["response"][:100].replace("\n", " ")
                    print(f"    ✅ Response: {response_preview}...")
                    print(f"    Source: {result.get('source', 'unknown')}")
                else:
                    print(f"    ❌ Query failed: {result.get('error', 'Unknown error')}")

            except Exception as e:
                print(f"    ❌ Query error: {e}")

        return True

    except Exception as e:
        print(f"❌ Agent query test error: {e}")
        return False


async def test_corpus_status():
    """Test RAG corpus status."""
    print("\n📊 Testing Corpus Status...")

    try:
        agent = await get_government_schemes_agent()

        if agent:
            status = agent.get_corpus_status()
            print(f"  Status: {status.get('status', 'unknown')}")
            print(f"  Files: {status.get('file_count', 0)}")
            print(f"  Model: {status.get('embedding_model', 'unknown')}")
            print(f"  Chunk Size: {status.get('chunk_size', 'unknown')}")
            print("✅ Corpus status retrieved")
            return True
        else:
            print("❌ Agent not available")
            return False

    except Exception as e:
        print(f"❌ Corpus status error: {e}")
        return False


async def run_comprehensive_test():
    """Run comprehensive test suite."""
    print("🧪 Government Schemes RAG Agent - Comprehensive Test Suite")
    print("=" * 60)

    test_results = []

    # Run all tests
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Sample Documents", test_sample_documents),
        ("Agent Initialization", test_agent_initialization),
        ("Tools Testing", test_tools),
        ("Agent Queries", test_agent_queries),
        ("Corpus Status", test_corpus_status),
    ]

    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            test_results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed / total * 100:.1f}%)")

    if passed == total:
        print("🎉 All tests passed! Government Schemes RAG Agent is ready.")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")

    return passed == total


async def main():
    """Main test function."""
    try:
        success = await run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Set up environment for testing
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "test-project")
    os.environ.setdefault("SCHEMES_DOCUMENTS_PATH", "./schemes_documents")

    asyncio.run(main())
