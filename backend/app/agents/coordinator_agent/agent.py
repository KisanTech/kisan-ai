from google.adk.agents import Agent
from google.adk.tools import agent_tool
from google.genai import types

from app.agents.crop_diagnosis_agent.agent import root_agent as crop_diagnosis_agent
from app.agents.general_query_agent.agent import root_agent as general_query_agent
from app.agents.market_agent.agent import root_agent as market_agent
from app.agents.rag_agent.agent import root_agent as rag_agent

general_query_tool = agent_tool.AgentTool(agent=general_query_agent)
market_tool = agent_tool.AgentTool(agent=market_agent)
crop_diagnosis_tool = agent_tool.AgentTool(agent=crop_diagnosis_agent)
rag_tool = agent_tool.AgentTool(agent=rag_agent)

generate_content_config = types.GenerateContentConfig(
    temperature=0.3,  # Lower temperature for more consistent market analysis
    top_p=0.95,
    max_output_tokens=65535,
)

root_agent = Agent(
    name="coordinator_agent",
    model="gemini-2.5-flash",
    description=("Intent classifier and main router"),
    instruction=(
        "You are Kisan AI, an intelligent agricultural assistant and coordinator that helps farmers and agricultural stakeholders. "
        "Your role is to analyze user queries and route them to the most appropriate specialized agent based on the intent and content.\n\n"
        "**ROUTING GUIDELINES:**\n"
        "🌾 **Market Agent**: Route queries about crop prices, market rates, selling opportunities, price trends, revenue calculations, or market analysis\n"
        "🔬 **Crop Diagnosis Agent**: Route queries about plant diseases, pest problems, crop health issues, symptoms identification, or treatment recommendations\n"
        "🏛️ **RAG Agent**: Route queries about government schemes, agricultural policies, subsidies, loan programs, insurance, or regulatory information\n"
        "💬 **General Query Agent**: Route general farming questions, best practices, cultivation tips, seasonal advice, or other agricultural guidance\n\n"
        "**INSTRUCTIONS:**\n"
        "1. Carefully analyze each user query to understand the primary intent\n"
        "2. Select the most appropriate specialized agent based on the query type\n"
        "3. If a query spans multiple areas, choose the agent that best addresses the main concern\n"
        "4. Always be helpful, professional, and farmer-friendly in your interactions\n"
        "5. Ensure the user gets accurate and relevant information from the specialized agents"
    ),
    tools=[general_query_tool, market_tool, crop_diagnosis_tool, rag_tool],
    generate_content_config=generate_content_config,
)
