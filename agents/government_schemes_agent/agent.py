"""
Government Schemes Agent
=======================

Kisan AI Government Schemes Agent with RAG-powered scheme information retrieval.
Uses pre-configured RAG corpus (setup via corpus_setup.py).
"""

import logging
import os
from typing import Any, Dict, Optional

import vertexai
from google.genai import types
from google.adk.agents import Agent

from .corpus_manager import CorpusManager
from .prompt import GOVERNMENT_SCHEMES_SYSTEM_PROMPT
from .tools import (
    check_scheme_eligibility,
    get_application_guidance,
    get_application_status,
    get_scheme_categories,
    search_schemes_by_need,
    set_corpus_manager,
    validate_documents,
)
from vertexai.generative_models import GenerativeModel
from vertexai.preview.reasoning_engines import AdkApp

# Setup logging
logger = logging.getLogger(__name__)

# Initialize Vertex AI
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
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
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=types.HarmBlockThreshold.OFF,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=types.HarmBlockThreshold.OFF,
    ),
]

# Generate content configuration
generate_content_config = types.GenerateContentConfig(
    safety_settings=safety_settings,
    temperature=0.2,
    top_p=0.8,
    top_k=40,
    max_output_tokens=2048,
)

# Initialize corpus manager
corpus_manager = None


def initialize_corpus_manager() -> bool:
    """Initialize the RAG corpus manager.

    Returns:
        True if initialization successful, False otherwise
    """
    global corpus_manager

    try:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

        if not project_id:
            logger.error("GOOGLE_CLOUD_PROJECT environment variable not set")
            return False

        logger.info("Initializing Government Schemes RAG corpus manager...")

        # Create and initialize corpus manager
        corpus_manager = CorpusManager(
            project_id=project_id, location=location, config_file="corpus_config.json"
        )

        # Initialize the corpus
        if not corpus_manager.initialize():
            logger.error("Failed to initialize corpus manager")
            return False

        # Set corpus manager for tools
        set_corpus_manager(corpus_manager)

        logger.info("Government Schemes RAG corpus manager initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Error initializing corpus manager: {e}")
        return False


# Initialize corpus manager on module load
if not initialize_corpus_manager():
    logger.warning("Corpus manager initialization failed - tools will return errors")

root_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="government_schemes_agent",
    description="AI-powered government schemes agent for farmers in India with RAG-powered knowledge",
    instruction=GOVERNMENT_SCHEMES_SYSTEM_PROMPT,
    generate_content_config=generate_content_config,
    tools=[
        check_scheme_eligibility,
        get_scheme_categories,
        validate_documents,
        get_application_guidance,
        get_application_status,
        search_schemes_by_need,
    ],
)

app = AdkApp(agent=root_agent)
