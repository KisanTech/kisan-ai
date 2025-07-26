"""
Market Agent Configuration
=========================

Kisan AI Market Analysis Agent with real-time market data integration.
"""

import os

import vertexai
from google.adk.agents import Agent
from google.genai import types

# Import market agent components
from market_agent.prompt import MARKET_ANALYSIS_PROMPT
from market_agent.tools import calculate_revenue, get_market_data, get_price_summary
from vertexai.preview.reasoning_engines import AdkApp

vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    staging_bucket=os.getenv("GOOGLE_CLOUD_STAGING_BUCKET"),
)

# Safety settings for agricultural content
safety_settings = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.OFF,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=types.HarmBlockThreshold.OFF,
    ),
]

# Generate content configuration
generate_content_config = types.GenerateContentConfig(
    safety_settings=safety_settings,
    temperature=0.3,  # Lower temperature for more consistent market analysis
    top_p=0.8,
    top_k=40,
    max_output_tokens=2048,
)

# Create the Market Agent
root_agent = Agent(
    name="market_agent",
    model="gemini-2.0-flash",
    description="Expert agricultural market analyst providing real-time price information, revenue calculations, and market recommendations for farmers across India.",
    instruction=MARKET_ANALYSIS_PROMPT,
    generate_content_config=generate_content_config,
    tools=[
        get_market_data,
        get_price_summary,
        calculate_revenue,
    ],
)

# Create ADK App for deployment
app = AdkApp(agent=root_agent)

# Export for deployment scripts
__all__ = ["root_agent", "app"]
