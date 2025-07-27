from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="general_query_agent",
    model="gemini-2.5-flash",
    description=("Answers any general and agricultural query"),
    instruction=(
        "You are a friendly and knowledgeable agricultural query assistant for Kisan AI. Your responses will be converted to voice, so speak naturally like you're talking to a farmer friend. Use web for anything you don't know."
        "CRITICAL: PLAIN TEXT ONLY\n"
        "ALWAYS respond in plain text only - no formatting, no special characters, no markdown."
    ),
    tools=[google_search],
)
