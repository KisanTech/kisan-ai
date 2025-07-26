import os

import vertexai
from crop_diagnosis_agent.prompt import CROP_HEALTH_ANALYSIS_PROMPT
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.genai import types
from vertexai.preview.reasoning_engines import AdkApp

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
    temperature=0.4,
    safety_settings=safety_settings,
)

root_agent = Agent(
    name="crop_diagnosis_agent",
    model="gemini-2.0-flash",
    description="Advanced AI assistant specializing in crop disease diagnosis with localized treatment recommendations",
    instruction=CROP_HEALTH_ANALYSIS_PROMPT,
    generate_content_config=generate_content_config,
    tools=[],
)

app = AdkApp(agent=root_agent)
