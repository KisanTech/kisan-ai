from google.adk.agents import Agent
from google.adk.tools import agent_tool, google_search

from app.agents.general_query_agent.agent import root_agent as general_query_agent
from app.agents.market_agent.agent import root_agent as market_agent
from app.agents.crop_diagnosis_agent.agent import root_agent as crop_diagnosis_agent


general_query_tool = agent_tool.AgentTool(agent=general_query_agent)
market_tool = agent_tool.AgentTool(agent=market_agent)
crop_diagnosis_tool = agent_tool.AgentTool(agent=crop_diagnosis_agent)

root_agent = Agent(
    name="coordinator_agent",
    model="gemini-2.5-flash",
    description=(
        "Intent classifier and main router"
    ),
    instruction=(
        "You are a helpful Agricultural Assitant which can aswer user questions. If user ask for any crop or market pricing "
        "then you will forward it to market agent and if user ask for any general query then you will forward it to "
        "general query agent and if user ask for any crop diagnosis then you will forward it to crop diagnosis agent"
    ),
    # sub_agents=[market_agent, general_query_agent]
    tools=[general_query_tool, market_tool, crop_diagnosis_tool]
)