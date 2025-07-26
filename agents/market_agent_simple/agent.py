"""
Simplified Market Agent Configuration
====================================

Minimal approach - just one tool, LLM does all analysis.
"""

import os

import vertexai
from google.adk.agents import Agent
from google.genai import types
from market_agent_simple.prompt import MARKET_ANALYSIS_PROMPT

# Import simplified tools
from market_agent_simple.tools import get_market_data
from vertexai.preview.reasoning_engines import AdkApp

# Initialize Vertex AI
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    staging_bucket=os.getenv("GOOGLE_CLOUD_STAGING_BUCKET"),
)

# Create the Simple Market Agent (only one tool)
root_agent = Agent(
    name="simple_market_agent",
    model="gemini-2.0-flash",
    description="Simple agricultural market analyst with minimal tools - LLM does all analysis.",
    instruction=MARKET_ANALYSIS_PROMPT,
    tools=[get_market_data],  # Only one tool!
)

# Create ADK App for deployment
app = AdkApp(agent=root_agent)

__all__ = ["root_agent", "app"]
