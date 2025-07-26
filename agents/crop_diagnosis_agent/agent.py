import vertexai
import os
from google.genai import types
from google.adk.agents import Agent
from google.adk.tools import google_search
from vertexai.preview.reasoning_engines import AdkApp
from crop_diagnosis_agent.prompt import CROP_HEALTH_ANALYSIS_PROMPT, INDIAN_AGRICULTURE_CONTEXT

from agents.government_schemes_agent.prompt import GOVERNMENT_SCHEMES_SYSTEM_PROMPT

vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    staging_bucket=os.getenv("GOOGLE_CLOUD_STAGING_BUCKET"),
)

safety_settings = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.OFF,
    ),
]
generate_content_config = types.GenerateContentConfig(
    safety_settings=safety_settings,
)

root_agent = Agent(
    name="crop_diagnosis_agent",
    model="gemini-2.0-flash",
    description="Advanced AI agronomist specializing in crop disease diagnosis with localized treatment recommendations",
    instruction=GOVERNMENT_SCHEMES_SYSTEM_PROMPT,
    generate_content_config=generate_content_config,
    tools=[],
)

app = AdkApp(agent=root_agent)
