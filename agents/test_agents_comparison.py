"""
Agent Comparison Test Script
===========================

Tests both Simple and Specialized market agents with the same queries
and saves results for side-by-side comparison.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict, List

# Setup environment first
from setup_test_env import setup_environment

setup_environment()

# Import both agent types
from market_agent.agent import root_agent as specialized_agent
from market_agent_simple.agent import root_agent as simple_agent

# Test queries to run against both agents
TEST_QUERIES = [
    "What's the current price of tomatoes in Karnataka?",
    "How much money will I earn if I sell 100kg of carrots in Karnataka?",
    "Which market has the best price for onions in Karnataka?",
    "Show me all vegetable prices in Karnataka today",
    "Compare tomato prices across all markets in Karnataka",
    "What's the price range for potatoes in Karnataka?",
    "Calculate revenue for 50kg of beans in Karnataka",
    "What crops are available in Karnataka markets today?",
]


async def test_agent(agent, agent_name: str, query: str) -> Dict[str, Any]:
    """Test a single query against an agent and capture response details."""
    print(f"\n🤖 Testing {agent_name}: {query}")

    start_time = time.time()

    try:
        # Run the query
        response = await agent.send_message(query)
        end_time = time.time()

        return {
            "agent_name": agent_name,
            "query": query,
            "success": True,
            "response": str(response),
            "response_time_seconds": round(end_time - start_time, 2),
            "timestamp": datetime.now().isoformat(),
            "error": None,
        }

    except Exception as e:
        end_time = time.time()
        print(f"❌ Error with {agent_name}: {str(e)}")

        return {
            "agent_name": agent_name,
            "query": query,
            "success": False,
            "response": None,
            "response_time_seconds": round(end_time - start_time, 2),
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


async def run_comparison_tests():
    """Run all test queries against both agents and save results."""
    print("🚀 Starting Agent Comparison Tests")
    print("=" * 50)

    all_results = []

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n📝 Query {i}/{len(TEST_QUERIES)}: {query}")
        print("-" * 40)

        # Test both agents with the same query
        specialized_result = await test_agent(specialized_agent, "Specialized Agent", query)
        simple_result = await test_agent(simple_agent, "Simple Agent", query)

        # Group results for this query
        query_results = {
            "query_number": i,
            "query": query,
            "specialized_agent": specialized_result,
            "simple_agent": simple_result,
        }

        all_results.append(query_results)

        # Brief pause between queries
        await asyncio.sleep(1)

    # Save results to files
    save_results(all_results)
    print("\n✅ Comparison tests completed!")


def save_results(results: List[Dict[str, Any]]):
    """Save test results in both JSON and readable format."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save detailed JSON for programmatic analysis
    json_file = f"test_results_{timestamp}.json"
    with open(json_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"📄 Detailed results saved to: {json_file}")

    # Save readable comparison format
    readable_file = f"test_comparison_{timestamp}.md"
    with open(readable_file, "w") as f:
        f.write("# Market Agent Comparison Results\n\n")
        f.write(f"**Test Run**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for result in results:
            query = result["query"]
            q_num = result["query_number"]

            f.write(f"## Query {q_num}: {query}\n\n")

            # Specialized Agent Results
            spec = result["specialized_agent"]
            f.write("### 🔧 Specialized Agent (3 Tools)\n")
            f.write(f"**Success**: {spec['success']}\n")
            f.write(f"**Response Time**: {spec['response_time_seconds']}s\n\n")

            if spec["success"]:
                f.write("**Response**:\n```\n")
                f.write(spec["response"])
                f.write("\n```\n\n")
            else:
                f.write(f"**Error**: {spec['error']}\n\n")

            # Simple Agent Results
            simple = result["simple_agent"]
            f.write("### 🎯 Simple Agent (1 Tool)\n")
            f.write(f"**Success**: {simple['success']}\n")
            f.write(f"**Response Time**: {simple['response_time_seconds']}s\n\n")

            if simple["success"]:
                f.write("**Response**:\n```\n")
                f.write(simple["response"])
                f.write("\n```\n\n")
            else:
                f.write(f"**Error**: {simple['error']}\n\n")

            f.write("---\n\n")

    print(f"📖 Readable comparison saved to: {readable_file}")


def print_summary(results: List[Dict[str, Any]]):
    """Print a quick summary of test results."""
    print("\n📊 SUMMARY")
    print("=" * 30)

    spec_success = sum(1 for r in results if r["specialized_agent"]["success"])
    simple_success = sum(1 for r in results if r["simple_agent"]["success"])

    spec_avg_time = sum(r["specialized_agent"]["response_time_seconds"] for r in results) / len(
        results
    )
    simple_avg_time = sum(r["simple_agent"]["response_time_seconds"] for r in results) / len(
        results
    )

    print(f"Specialized Agent: {spec_success}/{len(results)} successful, avg {spec_avg_time:.1f}s")
    print(f"Simple Agent: {simple_success}/{len(results)} successful, avg {simple_avg_time:.1f}s")


if __name__ == "__main__":
    print("🧪 Market Agent Comparison Test")
    print(f"Testing {len(TEST_QUERIES)} queries against both agent types...")

    # Run the comparison
    asyncio.run(run_comparison_tests())
