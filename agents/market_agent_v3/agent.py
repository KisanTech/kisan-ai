"""
Market Agent V3 - Simplified
============================

Smart agricultural market agent with one simple tool.
LLM handles parameter extraction, tool does targeted API calls.
"""

import os

import vertexai
from google.adk.agents import Agent
# Import market agent components
from market_agent_v3.prompt import MARKET_ANALYSIS_PROMPT_V3
from market_agent_v3.tools import get_market_data_smart

# Initialize Vertex AI
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    staging_bucket=os.getenv("GOOGLE_CLOUD_STAGING_BUCKET"),
)

# Create the V3 Market Agent with single smart tool
agent = Agent(
    name="market_agent",
    model="gemini-2.5-flash",
    description="Smart agricultural market agent with intelligent parameter extraction - LLM extracts filters, tool makes targeted API calls.",
    instruction=MARKET_ANALYSIS_PROMPT_V3,
    tools=[get_market_data_smart],
)
