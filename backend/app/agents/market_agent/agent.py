import os

import vertexai
from google.adk.agents import Agent

# Import market agent components
from app.agents.market_agent.prompt import MARKET_ANALYSIS_PROMPT_V3
from app.agents.market_agent.tools import get_market_data_smart

# Initialize Vertex AI
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    staging_bucket=os.getenv("GOOGLE_CLOUD_STAGING_BUCKET"),
)

# Create the V3 Market Agent with single smart tool
root_agent = Agent(
    name="market_agent",
    model="gemini-2.5-flash",
    description="Smart agricultural market agent with intelligent parameter extraction - LLM extracts filters, tool makes targeted API calls.",
    instruction=MARKET_ANALYSIS_PROMPT_V3,
    tools=[get_market_data_smart],
)
