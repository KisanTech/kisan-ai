"""
Government Schemes Agent Startup
===============================

Initialization and startup procedures for the government schemes RAG agent.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, Any

from government_schemes_agent.agent import GovernmentSchemesAgent
from government_schemes_agent.rag_manager import GovernmentSchemesRAGManager

logger = logging.getLogger(__name__)


async def initialize_government_schemes_agent() -> Dict[str, Any]:
    """Initialize the government schemes agent with all components.

    Returns:
        Dictionary with initialization status and details
    """
    try:
        logger.info("Starting Government Schemes Agent initialization...")

        # Check environment variables
        required_env_vars = ["GOOGLE_CLOUD_PROJECT"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]

        if missing_vars:
            error_msg = f"Missing required environment variables: {missing_vars}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "missing_env_vars": missing_vars}

        # Create schemes documents directory if it doesn't exist
        schemes_path = os.getenv("SCHEMES_DOCUMENTS_PATH", "./schemes_documents")
        Path(schemes_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Schemes documents directory: {schemes_path}")

        # Initialize the agent
        agent = GovernmentSchemesAgent()
        initialization_success = await agent.initialize()

        if not initialization_success:
            return {"success": False, "error": "Failed to initialize Government Schemes Agent"}

        # Get corpus status
        corpus_status = agent.get_corpus_status()

        logger.info("Government Schemes Agent initialization completed successfully")

        return {
            "success": True,
            "agent_status": "initialized",
            "corpus_status": corpus_status,
            "schemes_documents_path": schemes_path,
            "project_id": os.getenv("GOOGLE_CLOUD_PROJECT"),
            "location": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        }

    except Exception as e:
        logger.error(f"Failed to initialize Government Schemes Agent: {e}")
        return {"success": False, "error": str(e)}


async def setup_sample_documents():
    """Set up sample government scheme documents for testing.

    This creates sample documents in the schemes directory for development
    and testing purposes.
    """
    try:
        schemes_path = os.getenv("SCHEMES_DOCUMENTS_PATH", "./schemes_documents")
        schemes_dir = Path(schemes_path)
        schemes_dir.mkdir(parents=True, exist_ok=True)

        # Sample scheme documents content
        sample_documents = {
            "pm_kisan_scheme.txt": """
PM-KISAN (Pradhan Mantri Kisan Samman Nidhi Yojana)

Objective:
To provide income support to all landholding farmer families across the country to supplement their financial needs for procuring various inputs related to agriculture and allied activities as well as domestic needs.

Eligibility:
- All landholding farmer families having cultivable land holding
- Excludes institutional land holders
- Excludes farmers who are income tax payers

Benefits:
- Financial benefit of Rs. 6000 per year
- Amount transferred in three equal installments of Rs. 2000 each
- Direct transfer to farmer's bank account

Required Documents:
- Aadhaar Card
- Land ownership documents
- Bank account details
- Mobile number linked to Aadhaar

Application Process:
1. Visit pmkisan.gov.in
2. Click on "Farmers Corner"
3. Select "New Farmer Registration"
4. Fill required details
5. Upload documents
6. Submit application

Contact Information:
- Helpline: 155261
- Email: pmkisan-ict@gov.in
- Website: https://pmkisan.gov.in/
            """,
            "pmksy_irrigation_scheme.txt": """
PMKSY (Pradhan Mantri Krishi Sinchayee Yojana)

Objective:
To achieve convergence of investments in irrigation at the field level, expand cultivated area under assured irrigation, improve on-farm water use efficiency, and introduce sustainable water conservation practices.

Components:
1. Accelerated Irrigation Benefits Programme (AIBP)
2. Har Khet Ko Pani (HKKP)
3. Per Drop More Crop (PDMC)

Micro Irrigation (Drip/Sprinkler):
- Subsidy: Up to 90% for small and marginal farmers
- Subsidy: Up to 80% for other farmers
- Minimum area: 0.5 acres

Eligibility:
- All categories of farmers
- Individual farmers, groups, cooperatives
- Land ownership or lease agreement required

Benefits:
- Water saving: 40-60%
- Fertilizer saving: 25-50%
- Increased crop yield: 20-50%
- Reduced labor cost

Required Documents:
- Aadhaar Card
- Land ownership/lease documents
- Bank account details
- Soil health card
- Survey number details

Application Process:
1. Visit pmksy.gov.in
2. Select "Micro Irrigation"
3. Online application form
4. Upload required documents
5. Technical inspection
6. Approval and subsidy release

Contact Information:
- Helpline: 1800-180-1551
- Website: https://pmksy.gov.in/microIrrigation/
            """,
            "pm_fasal_bima_yojana.txt": """
PM Fasal Bima Yojana (Pradhan Mantri Fasal Bima Yojana)

Objective:
To provide insurance coverage and financial support to farmers in the event of failure of any of the notified crop as a result of natural calamities, pests & diseases.

Coverage:
- Pre-sowing risks
- Standing crop risks
- Post-harvest risks
- Localized calamities

Premium Rates:
- Kharif crops: 2% of sum insured
- Rabi crops: 1.5% of sum insured
- Annual commercial/horticultural crops: 5% of sum insured

Eligibility:
- All farmers growing notified crops
- Compulsory for loanee farmers
- Voluntary for non-loanee farmers

Sum Insured:
- Scale of finance per hectare for the crop
- Average yield of last 7 years
- Minimum support price or market price

Required Documents:
- Aadhaar Card
- Land records (Khata/Khatauni)
- Bank account details
- Sowing certificate
- Loan sanction letter (for loanee farmers)

Application Process:
1. Visit pmfby.gov.in
2. Farmer registration
3. Select crop and area
4. Premium calculation
5. Payment of farmer's share
6. Policy issuance

Claims Process:
- Crop cutting experiments by government
- Yield data analysis
- Claim calculation based on threshold yield
- Direct transfer to farmer's account

Contact Information:
- Helpline: 1800-200-7710
- Website: https://pmfby.gov.in/
- Email: support@pmfby.gov.in
            """,
            "kisan_credit_card.txt": """
Kisan Credit Card (KCC) Scheme

Objective:
To provide adequate and timely credit support from the banking system under a single window to the farmers for their cultivation and other needs.

Features:
- Flexible credit facility
- Simple documentation
- Built-in cost escalation
- Conversion/rescheduling facility
- Insurance coverage

Eligibility:
- All farmers including tenant farmers
- Individual/joint borrowers
- Self Help Groups
- Joint Liability Groups

Credit Limit:
- Based on operational land holding
- Scale of finance for crops
- Consumption needs
- Asset maintenance

Interest Rate:
- 7% per annum (with interest subvention)
- 4% per annum for prompt repaying farmers
- Additional 3% interest subvention

Required Documents:
- Application form
- Identity proof (Aadhaar)
- Address proof
- Land ownership documents
- Income proof

Benefits:
- Hassle-free credit
- Flexible repayment
- Lower interest rates
- Insurance coverage
- ATM facility

Application Process:
1. Visit nearest bank branch
2. Fill KCC application form
3. Submit required documents
4. Bank verification
5. Credit limit sanction
6. Card issuance

Repayment:
- Flexible repayment schedule
- Aligned with crop harvesting
- Revolving credit facility

Contact Information:
- Contact nearest bank branch
- NABARD helpline: 1800-180-1551
- Website: https://www.nabard.org/
            """,
        }

        # Create sample documents
        for filename, content in sample_documents.items():
            file_path = schemes_dir / filename
            if not file_path.exists():
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content.strip())
                logger.info(f"Created sample document: {file_path}")

        logger.info(f"Sample documents setup completed in {schemes_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to setup sample documents: {e}")
        return False


def check_environment() -> Dict[str, Any]:
    """Check if the environment is properly configured.

    Returns:
        Dictionary with environment check results
    """
    try:
        env_status = {
            "google_cloud_project": os.getenv("GOOGLE_CLOUD_PROJECT"),
            "google_cloud_location": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
            "schemes_documents_path": os.getenv("SCHEMES_DOCUMENTS_PATH", "./schemes_documents"),
            "staging_bucket": os.getenv("GOOGLE_CLOUD_STAGING_BUCKET"),
        }

        # Check if documents directory exists
        schemes_path = env_status["schemes_documents_path"]
        documents_exist = os.path.exists(schemes_path)

        if documents_exist:
            # Count documents in directory
            doc_count = len(
                [f for f in os.listdir(schemes_path) if f.endswith((".txt", ".pdf", ".docx"))]
            )
        else:
            doc_count = 0

        return {
            "environment_variables": env_status,
            "documents_directory_exists": documents_exist,
            "document_count": doc_count,
            "ready_for_initialization": bool(env_status["google_cloud_project"]),
        }

    except Exception as e:
        logger.error(f"Error checking environment: {e}")
        return {"error": str(e), "ready_for_initialization": False}


# Main initialization function
async def main():
    """Main function to initialize the government schemes agent."""
    try:
        # Check environment
        env_check = check_environment()
        print("Environment Check:")
        print(
            f"  Google Cloud Project: {env_check['environment_variables']['google_cloud_project']}"
        )
        print(f"  Documents Directory: {env_check['documents_directory_exists']}")
        print(f"  Document Count: {env_check['document_count']}")
        print(f"  Ready for Initialization: {env_check['ready_for_initialization']}")

        if not env_check["ready_for_initialization"]:
            print("❌ Environment not ready. Please set GOOGLE_CLOUD_PROJECT environment variable.")
            return

        # Setup sample documents if directory is empty
        if env_check["document_count"] == 0:
            print("📄 Setting up sample documents...")
            await setup_sample_documents()

        # Initialize agent
        print("🚀 Initializing Government Schemes Agent...")
        result = await initialize_government_schemes_agent()

        if result["success"]:
            print("✅ Government Schemes Agent initialized successfully!")
            print(f"  Corpus Status: {result['corpus_status']['status']}")
            print(f"  File Count: {result['corpus_status'].get('file_count', 0)}")
        else:
            print(f"❌ Initialization failed: {result['error']}")

    except Exception as e:
        logger.error(f"Error in main initialization: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
