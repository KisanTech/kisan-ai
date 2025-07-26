#!/usr/bin/env python3
"""
Test script for the updated corpus setup functionality.
Tests reading files from local path and importing them.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from corpus_setup import CorpusSetupManager

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def test_corpus_setup():
    """Test the corpus setup functionality."""

    # Configuration
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT environment variable not set")
        return False

    documents_path = "../scheme_documents"

    print("🧪 Testing Government Schemes Corpus Setup")
    print("=" * 50)
    print(f"Project ID: {project_id}")
    print(f"Documents Path: {documents_path}")
    print()

    # Create setup manager
    setup_manager = CorpusSetupManager(
        project_id=project_id,
        location="us-central1",
        corpus_display_name="test-government-schemes-corpus",
        documents_path=documents_path,
        # Note: Not setting GCS bucket for development testing
    )

    try:
        # Test 1: Check local files
        print("📁 Test 1: Checking local files...")
        local_files = setup_manager.get_local_files()
        print(f"Found {len(local_files)} local files:")
        for file_path in local_files:
            print(f"  ✓ {file_path.name} ({file_path.suffix})")

        if not local_files:
            print("❌ No local files found!")
            return False

        print()

        # Test 2: Get document paths
        print("🔗 Test 2: Getting document paths...")
        document_paths = setup_manager.get_document_paths()
        print(f"Generated {len(document_paths)} document paths:")
        for path in document_paths:
            print(f"  ✓ {path}")
        print()

        # Test 3: Check corpus status
        print("📊 Test 3: Checking corpus status...")
        status = setup_manager.get_corpus_status()
        print(f"Status: {status['status']}")
        if status.get("corpus_name"):
            print(f"Existing corpus: {status['corpus_name']}")
        print()

        # Test 4: Setup corpus (development mode)
        print("🚀 Test 4: Setting up corpus...")
        result = await setup_manager.setup_corpus(force_recreate=False)

        if result["success"]:
            print("✅ Corpus setup successful!")
            print(f"Corpus Name: {result['corpus_name']}")
            print(f"Local Files Found: {result.get('local_files_found', 0)}")
            print(f"File Count in Corpus: {result.get('file_count', 0)}")
            print(f"Ingestion Success: {result.get('ingestion_success', False)}")
            print(f"GCS Enabled: {result.get('gcs_enabled', False)}")

            if not result.get("gcs_enabled"):
                print("\n💡 Running in development mode (no GCS bucket configured)")
                print("   Document ingestion is simulated.")
        else:
            print(f"❌ Corpus setup failed: {result.get('error', 'Unknown error')}")
            return False

        print()

        # Test 5: Final status check
        print("🔍 Test 5: Final status check...")
        final_status = setup_manager.get_corpus_status()
        print(f"Final Status: {final_status['status']}")
        if final_status.get("corpus_name"):
            print(f"Corpus Name: {final_status['corpus_name']}")
            print(f"File Count: {final_status.get('file_count', 0)}")

        print("\n✅ All tests completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Detailed error information:")
        return False


async def main():
    """Main test function."""
    print("Starting corpus setup tests...\n")

    success = await test_corpus_setup()

    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
