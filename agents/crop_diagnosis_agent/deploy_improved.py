import vertexai
import os
import logging
import time
from vertexai.preview import reasoning_engines
from vertexai import agent_engines
from dotenv import load_dotenv
from google.cloud import aiplatform

# It's good practice to import from the package structure
from crop_diagnosis_agent.agent import root_agent

# Initialize logging with more detailed format
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def validate_environment():
    """Validate all required environment variables and settings."""
    logger.info("🔧 Validating environment...")

    required_vars = {
        "GOOGLE_CLOUD_PROJECT": "Your Google Cloud Project ID",
        "GOOGLE_CLOUD_LOCATION": "Deployment region (e.g., us-central1)",
    }

    optional_vars = {"GOOGLE_CLOUD_STAGING_BUCKET": "Staging bucket for deployment artifacts"}

    missing_vars = []

    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            logger.info(f"✅ {var}: {value}")
        else:
            logger.error(f"❌ {var}: Missing ({description})")
            missing_vars.append(var)

    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            logger.info(f"✅ {var}: {value}")
        else:
            logger.warning(f"⚠️ {var}: Not set ({description})")

    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        logger.error("Please set these in your .env file or environment")
        return False

    return True


def check_existing_agents():
    """Check if agent with same name already exists."""
    logger.info("🔍 Checking for existing agents...")

    try:
        agents = agent_engines.list()
        existing_crop_agents = [
            agent for agent in agents if "crop_diagnosis" in agent.display_name.lower()
        ]

        if existing_crop_agents:
            logger.warning(f"⚠️ Found {len(existing_crop_agents)} existing crop diagnosis agent(s):")
            for agent in existing_crop_agents:
                logger.warning(f"  - {agent.display_name} ({agent.resource_name})")

            response = input("Do you want to continue and create another agent? (y/N): ")
            if response.lower() != "y":
                logger.info("❌ Deployment cancelled by user")
                return False
        else:
            logger.info("✅ No existing crop diagnosis agents found")

        return True

    except Exception as e:
        logger.warning(f"⚠️ Could not check existing agents: {e}")
        return True  # Continue anyway


def deploy_agent():
    """Deploy the agent with comprehensive error handling and status checking."""

    if not validate_environment():
        return False

    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    staging_bucket = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET")

    # Initialize Vertex AI
    logger.info("🚀 Initializing Vertex AI...")
    try:
        vertexai.init(
            project=project,
            location=location,
            staging_bucket=staging_bucket,
        )
        logger.info("✅ Vertex AI initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Vertex AI: {e}")
        logger.error("Check your authentication and project permissions")
        return False

    # Check existing agents
    if not check_existing_agents():
        return False

    # Wrap the agent
    logger.info("📦 Wrapping agent for deployment...")
    try:
        app = reasoning_engines.AdkApp(
            agent=root_agent,
            enable_tracing=True,
        )
        logger.info("✅ Agent wrapped successfully")
    except Exception as e:
        logger.error(f"❌ Failed to wrap agent: {e}")
        return False

    # Define requirements
    requirements_list = [
        "google-cloud-aiplatform[agent_engines,adk,langchain,ag2,llama_index]==1.88.0",
        "google-genai>=1.9.0",
        "google-adk==1.0.0",
        "python-dotenv>=1.0.0",
        "pydantic==2.10.6",
        "langchain>=0.1.0",
        "langgraph>=0.1.0",
    ]

    # Deploy the agent
    logger.info("🚀 Starting deployment to Vertex AI Agent Engine...")
    logger.info(f"📋 Requirements: {requirements_list}")

    try:
        deployment_start_time = time.time()

        remote_app = agent_engines.create(
            display_name="crop_diagnosis_agent",
            agent_engine=app,
            requirements=requirements_list,
        )

        deployment_time = time.time() - deployment_start_time
        logger.info(f"✅ Deployment initiated successfully in {deployment_time:.2f} seconds")
        logger.info(f"📍 Resource Name: {remote_app.resource_name}")

        # Wait for deployment to complete
        logger.info("⏳ Waiting for deployment to complete...")
        max_wait_time = 600  # 10 minutes
        wait_start = time.time()

        while time.time() - wait_start < max_wait_time:
            try:
                # Try to create a session to test if agent is ready
                session = remote_app.create_session(user_id="deployment-test")
                logger.info("✅ Agent is ready and responding!")
                break
            except Exception as e:
                logger.info(f"⏳ Agent not ready yet... ({e})")
                time.sleep(10)
        else:
            logger.warning("⚠️ Deployment may still be in progress after 5 minutes")

        # Test the deployment
        logger.info("🧪 Testing deployment...")
        try:
            test_start_time = time.time()
            session = remote_app.create_session(user_id="test-user-deployment")
            logger.info(f"✅ Session created: {session.get('id', 'Unknown')}")

            response_received = False
            for event in remote_app.stream_query(
                user_id="test-user-deployment",
                session_id=session["id"],
                message="Hello! Can you help me with crop diagnosis?",
            ):
                if event.get("content"):
                    test_time = time.time() - test_start_time
                    logger.info(
                        f"✅ Received response in {test_time:.2f}s: {event['content'][:100]}..."
                    )
                    response_received = True
                    break

            if response_received:
                logger.info("🎉 Deployment test SUCCESSFUL!")
                logger.info(f"🌐 Agent deployed and accessible at: {remote_app.resource_name}")

                # Provide usage instructions
                logger.info("\n📖 Usage Instructions:")
                logger.info("1. Access via Google Cloud Console: Vertex AI > Agent Engine")
                logger.info("2. Use the Python SDK to interact with the agent")
                logger.info("3. Resource name for API calls: " + remote_app.resource_name)

                return True
            else:
                logger.error("❌ Agent deployed but not responding correctly")
                return False

        except Exception as e:
            logger.error(f"❌ Deployment test failed: {e}")
            logger.info("Agent may still be deploying. Check manually in Google Cloud Console.")
            return False

    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        logger.error("Common issues:")
        logger.error("- Check your Google Cloud permissions")
        logger.error("- Verify Agent Engine API is enabled")
        logger.error("- Check quota limits in your project")
        logger.error("- Verify the region supports Agent Engine")
        return False


def main():
    """Main deployment function."""
    logger.info("🚀 Starting Google ADK Agent Deployment")
    logger.info("=" * 60)

    success = deploy_agent()

    logger.info("=" * 60)
    if success:
        logger.info("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
        logger.info("Your crop diagnosis agent is now live on Vertex AI Agent Engine")
    else:
        logger.error("❌ DEPLOYMENT FAILED")
        logger.error("Please check the logs above and fix any issues")
        logger.error("Run the check_deployment.py script to debug further")


if __name__ == "__main__":
    main()
