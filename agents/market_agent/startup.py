"""
Market Agent Startup Script
===========================

Handles agent initialization including cache loading at startup.
"""

import asyncio
import logging
import os

from market_agent.cache_manager import initialize_cache

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def startup_agent():
    """Initialize the market agent with full cache loading"""
    logger.info("🚀 Starting Market Agent initialization...")

    # Check environment variables
    backend_url = os.getenv("BACKEND_API_URL")
    if not backend_url:
        logger.error("❌ BACKEND_API_URL environment variable not set!")
        return False

    logger.info(f"📡 Backend URL: {backend_url}")

    # Initialize cache with all historical data
    logger.info("📦 Loading market data cache...")
    success = await initialize_cache()

    if success:
        logger.info("✅ Market Agent startup complete!")
        logger.info("🎯 Agent ready to serve trend analysis queries with full historical data!")
        return True
    else:
        logger.error("❌ Market Agent startup failed - cache initialization error")
        return False


def run_startup():
    """Run startup in event loop"""
    return asyncio.run(startup_agent())


if __name__ == "__main__":
    run_startup()
