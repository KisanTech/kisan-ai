from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.retrieval import VertexAiRagRetrieval
from vertexai.preview.rag import RagResource
from rag_agent.prompt import GOVERNMENT_SCHEMES_SYSTEM_PROMPT
from google.genai import types


rag_tool = VertexAiRagRetrieval(name="Government Policies Knowledge Base",
 description="India government schemas for agricultural policies",
 rag_resources=[RagResource(rag_corpus="projects/kisanai-466809/locations/us-central1/ragCorpora/2305843009213693952")]
)

generate_content_config = types.GenerateContentConfig(
    temperature=0.3,  # Lower temperature for more consistent market analysis
    top_p = 0.95,
    max_output_tokens = 65535,
)

root_agent = Agent(
    name="rag_agent",
    model="gemini-2.5-flash",
    description="Answers any questions on the government policies or schemas on agricultural",
    instruction=GOVERNMENT_SCHEMES_SYSTEM_PROMPT,
    tools=[rag_tool],
    generate_content_config=generate_content_config,
)