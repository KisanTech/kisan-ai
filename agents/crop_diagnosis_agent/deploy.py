import vertexai
import os
import logging
from vertexai.preview import reasoning_engines
from vertexai import agent_engines
from dotenv import load_dotenv

# It's good practice to import from the package structure
# This assumes you run the script from the parent 'agents' directory
from crop_diagnosis_agent.agent import root_agent

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Vertex AI
# Ensure environment variables are set before running
logger.info("Initializing Vertex AI...")

project = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")
staging_bucket = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET")

logger.info(f"Project: {project}")
logger.info(f"Location: {location}")
logger.info(f"Staging Bucket: {staging_bucket}")

try:
    vertexai.init(
        project=project,
        location=location,
        staging_bucket=staging_bucket,
    )
    logger.info("Vertex AI initialized successfully.")
except Exception as e:
    logger.error(
        f"Failed to initialize Vertex AI. Please check your environment variables and permissions. Error: {e}"
    )
    exit()


# Wrap the agent to make it deployable to Agent Engine
logger.info("Wrapping agent to make it deployable to Agent Engine...")
app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)
logger.info("Agent wrapped.")

# All dependencies from your pyproject.toml must be listed here.
# The versions should match to ensure consistency.
requirements_list = [
    "google-cloud-aiplatform[agent_engines,adk,langchain,ag2,llama_index]==1.88.0",
    "google-genai>=1.9.0",
    "google-adk==1.0.0",
    "python-dotenv>=1.0.0",
    "pydantic==2.10.6",
    "langchain>=0.1.0",
    "langgraph>=0.1.0",
]

# Deploy the agent engine to the cloud
logger.info(f"Deploying agent engine with the following requirements: {requirements_list}")
try:
    remote_app = agent_engines.create(
        display_name="crop_diagnosis_agent",  # A display name is recommended
        agent_engine=app,
        requirements=requirements_list,
    )
    logger.info("Agent engine deployment process started.")
    logger.info(
        f"Agent deployed to Vertex AI successfully under resource name: {remote_app.resource_name}"
    )

    # Test the deployment
    logger.info("Testing deployment with a sample query...")
    session = remote_app.create_session(user_id="test-user-123")
    for event in remote_app.stream_query(
        user_id="test-user-123",
        session_id=session["id"],
        message="hello!",
    ):
        if event.get("content", None):
            logger.info(f"Received response: {event['content']}")
    logger.info("Test query completed.")

except Exception as e:
    logger.error(f"Deployment failed. Error: {e}")
