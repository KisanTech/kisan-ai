#!/usr/bin/env python3
"""
Government Schemes Setup Script
==============================

One-time setup script for Government Schemes RAG Agent.
This script demonstrates the decoupled approach where corpus setup
is separate from agent initialization.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from government_schemes_agent.corpus_setup import CorpusSetupManager
from government_schemes_agent.corpus_manager import CorpusManager
from government_schemes_agent.startup import setup_sample_documents


async def main():
    """Main setup function."""
    print("🚀 Government Schemes RAG Agent Setup")
    print("=" * 50)

    # Check environment
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT environment variable not set")
        print("Please set it and try again:")
        print("export GOOGLE_CLOUD_PROJECT=your-project-id")
        return 1

    print(f"📋 Project ID: {project_id}")
    print(f"📍 Location: {os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')}")

    try:
        # Step 1: Setup sample documents
        print("\n📄 Step 1: Setting up sample documents...")
        doc_success = await setup_sample_documents()
        if doc_success:
            print("✅ Sample documents created")
        else:
            print("⚠️ Sample documents setup failed")

        # Step 2: Check if corpus already exists
        print("\n🔍 Step 2: Checking existing corpus...")
        corpus_manager = CorpusManager(project_id=project_id)

        if corpus_manager.load_corpus_config():
            print("✅ Corpus configuration found")
            corpus_info = corpus_manager.get_corpus_info()
            print(f"   Status: {corpus_info['status']}")
            print(f"   Files: {corpus_info.get('file_count', 0)}")

            # Ask if user wants to recreate
            response = input("\n🤔 Corpus already exists. Recreate? (y/N): ").strip().lower()
            force_recreate = response in ["y", "yes"]
        else:
            print("📝 No existing corpus found")
            force_recreate = True

        # Step 3: Setup corpus if needed
        if force_recreate:
            print("\n🔧 Step 3: Setting up RAG corpus...")
            setup_manager = CorpusSetupManager(project_id=project_id)

            result = await setup_manager.setup_corpus(force_recreate=force_recreate)

            if result["success"]:
                print("✅ Corpus setup completed!")
                print(f"   Corpus Name: {result['corpus_name']}")
                print(f"   Files: {result.get('file_count', 0)}")
            else:
                print(f"❌ Corpus setup failed: {result.get('error', 'Unknown error')}")
                return 1
        else:
            print("⏭️ Skipping corpus setup")

        # Step 4: Verify agent can initialize
        print("\n🧪 Step 4: Testing agent initialization...")

        # Import and test agent
        from government_schemes_agent.agent import GovernmentSchemesAgent

        agent = GovernmentSchemesAgent()
        init_success = await agent.initialize()

        if init_success:
            print("✅ Agent initialized successfully!")

            # Test a simple query
            print("\n💬 Step 5: Testing sample query...")
            test_result = await agent.query_schemes("What is PM-KISAN scheme?")

            if test_result.get("success"):
                print("✅ Sample query successful!")
                print(f"   Source: {test_result.get('source', 'unknown')}")
                response_preview = test_result["response"][:100].replace("\n", " ")
                print(f"   Response: {response_preview}...")
            else:
                print(f"⚠️ Sample query failed: {test_result.get('error', 'Unknown error')}")
        else:
            print("❌ Agent initialization failed")
            return 1

        # Success summary
        print("\n🎉 Setup Complete!")
        print("=" * 50)
        print("✅ Government Schemes RAG Agent is ready to use")
        print("\n📚 Next steps:")
        print("1. Start the backend server:")
        print("   cd backend && uv run python -m uvicorn app.main:app --reload")
        print("\n2. Test the API:")
        print("   curl http://localhost:8000/api/v1/government-schemes/health")
        print("\n3. Try a query:")
        print("   curl -X POST http://localhost:8000/api/v1/government-schemes/query \\")
        print("     -H 'Content-Type: application/json' \\")
        print('     -d \'{"query": "What is PM-KISAN scheme?"}\'')

        return 0

    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Setup failed: {e}")
        return 1


if __name__ == "__main__":
    # Set default environment variables for development
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
    os.environ.setdefault("SCHEMES_DOCUMENTS_PATH", "./schemes_documents")

    exit_code = asyncio.run(main())
    sys.exit(exit_code)
