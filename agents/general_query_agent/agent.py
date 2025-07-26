from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="general_query_agent",
    model="gemini-2.5-flash",
    description=(
        "Answers any general and agricultural query"
    ),
    instruction=(
        "You are a helpful agent who can answer user questions. Use web for anything you don't know."
    ),
    tools=[google_search],
)