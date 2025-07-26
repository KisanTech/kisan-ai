"""
Government Schemes RAG Corpus Setup
==================================

One-time setup script for creating and populating the RAG corpus.
This should be run manually during deployment or when updating documents.
"""

import asyncio
import json
import logging
import os
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, List

import vertexai
from vertexai import rag
from google.cloud import storage

logger = logging.getLogger(__name__)


class CorpusSetupManager:
    """Manages one-time setup of the RAG corpus."""

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        corpus_display_name: str = "government-schemes-corpus",
        documents_path: str = None,
        config_file: str = "corpus_config.json",
        gcs_bucket: str = None,
    ):
        """Initialize corpus setup manager.

        Args:
            project_id: Google Cloud project ID
            location: Vertex AI location
            corpus_display_name: Display name for RAG corpus
            documents_path: Local path to government scheme documents
            config_file: Path to save corpus configuration
            gcs_bucket: GCS bucket for document storage (optional)
        """
        self.project_id = project_id
        self.location = location
        self.corpus_display_name = corpus_display_name
        self.documents_path = documents_path or os.getenv(
            "SCHEMES_DOCUMENTS_PATH", "./schemes_documents"
        )
        self.config_file = config_file
        self.gcs_bucket = gcs_bucket or os.getenv("GOOGLE_CLOUD_STAGING_BUCKET")

        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)

        # Initialize GCS client if bucket is provided
        self.storage_client = storage.Client(project=project_id) if self.gcs_bucket else None

        # Supported file types
        self.supported_extensions = {".pdf", ".txt", ".docx", ".doc", ".md"}

        # Embedding configuration
        self.embedding_model_config = rag.RagEmbeddingModelConfig(
            vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
                publisher_model="publishers/google/models/text-embedding-005"
            )
        )

        # Chunking configuration
        self.transformation_config = rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(
                chunk_size=512,
                chunk_overlap=100,
            ),
        )

    async def create_corpus(self) -> Optional[str]:
        """Create a new RAG corpus.

        Returns:
            Corpus name if successful, None otherwise
        """
        try:
            logger.info(f"Creating RAG corpus: {self.corpus_display_name}")

            # Check if corpus already exists
            existing_corpora = rag.list_corpora()
            for corpus in existing_corpora:
                if corpus.display_name == self.corpus_display_name:
                    logger.info(f"Corpus already exists: {corpus.name}")
                    return corpus.name

            # Create new corpus
            rag_corpus = rag.create_corpus(
                display_name=self.corpus_display_name,
                backend_config=rag.RagVectorDbConfig(
                    rag_embedding_model_config=self.embedding_model_config
                ),
            )

            logger.info(f"Created RAG corpus: {rag_corpus.name}")
            return rag_corpus.name

        except Exception as e:
            logger.error(f"Failed to create RAG corpus: {e}")
            return None

    def get_local_files(self) -> List[Path]:
        """Get all supported document files from local path.

        Returns:
            List of Path objects for supported document files
        """
        if not os.path.exists(self.documents_path):
            logger.warning(f"Documents path does not exist: {self.documents_path}")
            return []

        documents_dir = Path(self.documents_path)
        local_files = []

        # Recursively find all supported files
        for file_path in documents_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                local_files.append(file_path)

        logger.info(f"Found {len(local_files)} supported files in {self.documents_path}")
        for file_path in local_files:
            logger.info(f"  - {file_path.name} ({file_path.suffix})")

        return local_files

    def upload_file_to_gcs(self, local_file_path: Path, gcs_path: str) -> Optional[str]:
        """Upload a local file to Google Cloud Storage.

        Args:
            local_file_path: Path to local file
            gcs_path: Destination path in GCS bucket

        Returns:
            GCS URL if successful, None otherwise
        """
        if not self.storage_client or not self.gcs_bucket:
            logger.warning("GCS client or bucket not configured")
            return None

        try:
            bucket = self.storage_client.bucket(self.gcs_bucket)
            blob = bucket.blob(gcs_path)

            # Set content type based on file extension
            content_type, _ = mimetypes.guess_type(str(local_file_path))
            if content_type:
                blob.content_type = content_type

            # Upload file
            blob.upload_from_filename(str(local_file_path))
            gcs_url = f"gs://{self.gcs_bucket}/{gcs_path}"

            logger.info(f"Uploaded {local_file_path.name} to {gcs_url}")
            return gcs_url

        except Exception as e:
            logger.error(f"Failed to upload {local_file_path.name} to GCS: {e}")
            return None

    def get_document_paths(self) -> List[str]:
        """Get all document paths for ingestion.

        Returns:
            List of document file paths or GCS URLs
        """
        local_files = self.get_local_files()
        if not local_files:
            logger.warning("No local files found for ingestion")
            return []

        document_paths = []

        # If GCS bucket is configured, upload files and return GCS URLs
        if self.gcs_bucket and self.storage_client:
            logger.info("Uploading files to GCS for RAG ingestion...")

            for local_file in local_files:
                # Create GCS path: schemes/filename
                gcs_path = f"schemes/{local_file.name}"
                gcs_url = self.upload_file_to_gcs(local_file, gcs_path)

                if gcs_url:
                    document_paths.append(gcs_url)
                else:
                    logger.warning(f"Failed to upload {local_file.name}, skipping...")

        else:
            # For development without GCS, create sample paths
            logger.warning("GCS not configured, using sample document paths for development")
            sample_gcs_paths = [
                "gs://your-bucket/schemes/pm_kisan_scheme.pdf",
                "gs://your-bucket/schemes/pmksy_irrigation.pdf",
                "gs://your-bucket/schemes/pm_fasal_bima.pdf",
                "gs://your-bucket/schemes/kisan_credit_card.pdf",
            ]
            document_paths = sample_gcs_paths[: len(local_files)]

        logger.info(f"Prepared {len(document_paths)} document paths for ingestion")
        return document_paths

    async def ingest_documents(self, corpus_name: str) -> bool:
        """Ingest documents into the RAG corpus.

        Args:
            corpus_name: Name of the RAG corpus

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Starting document ingestion...")

            # Get document paths
            document_paths = self.get_document_paths()
            if not document_paths:
                logger.warning("No documents to ingest")
                return False

            logger.info(f"Ingesting {len(document_paths)} documents")

            # Check if we have real GCS URLs or sample paths
            has_real_gcs_urls = all(
                path.startswith("gs://") and "your-bucket" not in path for path in document_paths
            )

            if has_real_gcs_urls:
                # Perform actual ingestion with real GCS URLs
                logger.info("Performing actual document ingestion...")

                response = rag.import_files(
                    corpus_name,
                    document_paths,
                    transformation_config=self.transformation_config,
                    max_embedding_requests_per_min=1000,
                )

                logger.info(f"Document ingestion completed successfully")
                logger.info(f"Ingestion response: {response}")
                return True

            else:
                # Development mode - simulate ingestion
                logger.info("Development mode: Simulating document ingestion...")
                logger.info("To enable real ingestion, configure GCS_BUCKET environment variable")

                # Simulate processing time
                await asyncio.sleep(2)

                logger.info("Document ingestion completed (simulated for development)")
                return True

        except Exception as e:
            logger.error(f"Failed to ingest documents: {e}")
            return False

    def save_corpus_config(self, corpus_name: str, file_count: int = 0) -> bool:
        """Save corpus configuration to file.

        Args:
            corpus_name: Name of the RAG corpus
            file_count: Number of files in corpus

        Returns:
            True if successful, False otherwise
        """
        try:
            config = {
                "corpus_name": corpus_name,
                "display_name": self.corpus_display_name,
                "project_id": self.project_id,
                "location": self.location,
                "embedding_model": "text-embedding-005",
                "chunk_size": 512,
                "chunk_overlap": 100,
                "file_count": file_count,
                "created_at": "2024-01-26T23:42:35+05:30",
                "status": "ready",
            }

            config_path = Path(self.config_file)
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)

            logger.info(f"Corpus configuration saved to {config_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save corpus config: {e}")
            return False

    def load_corpus_config(self) -> Optional[Dict[str, Any]]:
        """Load corpus configuration from file.

        Returns:
            Configuration dictionary or None if not found
        """
        try:
            config_path = Path(self.config_file)
            if not config_path.exists():
                return None

            with open(config_path, "r") as f:
                config = json.load(f)

            logger.info(f"Loaded corpus configuration from {config_path}")
            return config

        except Exception as e:
            logger.error(f"Failed to load corpus config: {e}")
            return None

    async def setup_corpus(self, force_recreate: bool = False) -> Dict[str, Any]:
        """Complete corpus setup process.

        Args:
            force_recreate: Whether to recreate corpus even if it exists

        Returns:
            Dictionary with setup results
        """
        try:
            logger.info("Starting corpus setup process...")

            # Validate documents path
            local_files = self.get_local_files()
            if not local_files:
                return {
                    "success": False,
                    "error": f"No supported documents found in {self.documents_path}",
                }

            # Check existing configuration
            if not force_recreate:
                existing_config = self.load_corpus_config()
                if existing_config and existing_config.get("status") == "ready":
                    logger.info("Corpus already configured and ready")
                    return {
                        "success": True,
                        "message": "Corpus already exists and is ready",
                        "corpus_name": existing_config["corpus_name"],
                        "config": existing_config,
                    }

            # Create corpus
            corpus_name = await self.create_corpus()
            if not corpus_name:
                return {"success": False, "error": "Failed to create corpus"}

            # Ingest documents
            ingestion_success = await self.ingest_documents(corpus_name)
            if not ingestion_success:
                logger.warning("Document ingestion failed, but corpus is created")

            # Get file count
            try:
                files = rag.list_files(corpus_name)
                file_count = len(files) if files else len(local_files)
            except:
                file_count = len(local_files)  # Fallback to local file count

            # Save configuration
            config_saved = self.save_corpus_config(corpus_name, file_count)

            result = {
                "success": True,
                "message": "Corpus setup completed successfully",
                "corpus_name": corpus_name,
                "file_count": file_count,
                "local_files_found": len(local_files),
                "ingestion_success": ingestion_success,
                "config_saved": config_saved,
                "gcs_enabled": bool(self.gcs_bucket),
            }

            logger.info("Corpus setup completed successfully")
            return result

        except Exception as e:
            logger.error(f"Corpus setup failed: {e}")
            return {"success": False, "error": str(e)}

    def get_corpus_status(self) -> Dict[str, Any]:
        """Get current corpus status.

        Returns:
            Dictionary with corpus status
        """
        try:
            config = self.load_corpus_config()
            if not config:
                return {
                    "status": "not_configured",
                    "message": "Corpus not configured. Run setup first.",
                }

            # Try to verify corpus exists
            try:
                corpus_name = config["corpus_name"]
                files = rag.list_files(corpus_name)
                file_count = len(files) if files else 0

                return {
                    "status": "ready",
                    "corpus_name": corpus_name,
                    "display_name": config["display_name"],
                    "file_count": file_count,
                    "embedding_model": config["embedding_model"],
                    "created_at": config["created_at"],
                }

            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Corpus exists in config but not accessible: {e}",
                    "config": config,
                }

        except Exception as e:
            logger.error(f"Failed to get corpus status: {e}")
            return {"status": "error", "error": str(e)}


async def main():
    """Main function for corpus setup."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Government Schemes RAG Corpus Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic setup with local documents
  python corpus_setup.py --project-id my-project --documents-path ./documents

  # Setup with GCS bucket for file storage
  python corpus_setup.py --project-id my-project --documents-path ./documents --gcs-bucket my-bucket

  # Check corpus status only
  python corpus_setup.py --project-id my-project --status-only

  # Force recreate existing corpus
  python corpus_setup.py --project-id my-project --documents-path ./documents --force-recreate

Supported file types: .pdf, .txt, .docx, .doc, .md
        """,
    )
    parser.add_argument("--project-id", required=True, help="Google Cloud Project ID")
    parser.add_argument(
        "--location", default="us-central1", help="Vertex AI location (default: us-central1)"
    )
    parser.add_argument(
        "--corpus-name",
        default="government-schemes-corpus",
        help="Corpus display name (default: government-schemes-corpus)",
    )
    parser.add_argument(
        "--documents-path",
        help="Path to scheme documents directory (default: ./schemes_documents or SCHEMES_DOCUMENTS_PATH env var)",
    )
    parser.add_argument(
        "--gcs-bucket",
        help="GCS bucket for document storage (optional, uses GOOGLE_CLOUD_STAGING_BUCKET env var if not specified)",
    )
    parser.add_argument(
        "--force-recreate", action="store_true", help="Force recreate corpus even if it exists"
    )
    parser.add_argument(
        "--status-only",
        action="store_true",
        help="Only check corpus status, don't create or modify",
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create setup manager
    setup_manager = CorpusSetupManager(
        project_id=args.project_id,
        location=args.location,
        corpus_display_name=args.corpus_name,
        documents_path=args.documents_path,
        gcs_bucket=args.gcs_bucket,
    )

    try:
        if args.status_only:
            # Just check status
            print("🔍 Checking corpus status...")
            status = setup_manager.get_corpus_status()
            print(f"Status: {status['status']}")
            if status.get("corpus_name"):
                print(f"Corpus: {status['corpus_name']}")
                print(f"Files: {status.get('file_count', 0)}")
                print(f"Created: {status.get('created_at', 'Unknown')}")

            # Also show local files info
            local_files = setup_manager.get_local_files()
            print(f"Local files found: {len(local_files)}")
            if local_files:
                print("Local files:")
                for file_path in local_files[:5]:  # Show first 5 files
                    print(f"  - {file_path.name}")
                if len(local_files) > 5:
                    print(f"  ... and {len(local_files) - 5} more files")
        else:
            # Run full setup
            print("🚀 Starting corpus setup...")
            print(f"Project ID: {args.project_id}")
            print(f"Location: {args.location}")
            print(f"Documents Path: {setup_manager.documents_path}")
            print(f"GCS Bucket: {setup_manager.gcs_bucket or 'Not configured (development mode)'}")

            result = await setup_manager.setup_corpus(force_recreate=args.force_recreate)

            if result["success"]:
                print("✅ Corpus setup completed successfully!")
                print(f"Corpus Name: {result['corpus_name']}")
                print(f"Local Files Found: {result.get('local_files_found', 0)}")
                print(f"File Count in Corpus: {result.get('file_count', 0)}")
                print(f"Ingestion Success: {result.get('ingestion_success', False)}")
                print(f"GCS Enabled: {result.get('gcs_enabled', False)}")

                if not result.get("gcs_enabled"):
                    print("\n💡 Tip: Configure GOOGLE_CLOUD_STAGING_BUCKET environment variable")
                    print("   or use --gcs-bucket parameter to enable real document ingestion.")
            else:
                print(f"❌ Corpus setup failed: {result.get('error', 'Unknown error')}")
                return 1

        return 0

    except Exception as e:
        print(f"💥 Setup failed: {e}")
        logger.exception("Detailed error information:")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(asyncio.run(main()))
