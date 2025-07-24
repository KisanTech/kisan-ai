"""
Kisan AI - AI-Powered Agricultural Assistant

A comprehensive agricultural assistance platform providing:
- AI-driven crop disease diagnosis
- Real-time market price intelligence
- Voice interface in Kannada
- Government scheme information

Built with FastAPI, Google Cloud Platform, and advanced AI models.
"""

# Load environment variables and setup credentials FIRST
import os

from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Convert relative credential paths to absolute paths for GCP
if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    cred_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    if not os.path.isabs(cred_path):
        # Convert relative path to absolute path
        abs_path = os.path.abspath(cred_path)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = abs_path
