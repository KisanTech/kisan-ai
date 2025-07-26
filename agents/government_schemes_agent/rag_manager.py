"""
RAG Manager for Government Schemes
=================================

Manages the RAG corpus for government scheme documents including:
- Document ingestion and processing
- Corpus creation and management
- Retrieval configuration
- Document chunking and embedding
"""

import logging
import os
import glob
from pathlib import Path
from typing import List, Optional, Dict, Any
import asyncio

import vertexai
from vertexai import rag
from vertexai.generative_models import GenerativeModel, Tool
import PyPDF2
import docx
from google.cloud import storage

logger = logging.getLogger(__name__)


class GovernmentSchemesRAGManager:
    """Manages RAG corpus for government schemes documents."""

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        corpus_display_name: str = "government-schemes-corpus",
        documents_path: str = None,
    ):
        """Initialize RAG manager.

        Args:
            project_id: Google Cloud project ID
            location: Vertex AI location
            corpus_display_name: Display name for RAG corpus
            documents_path: Local path to government scheme documents
        """
        self.project_id = project_id
        self.location = location
        self.corpus_display_name = corpus_display_name
        self.documents_path = documents_path or os.getenv(
            "SCHEMES_DOCUMENTS_PATH", "./schemes_documents"
        )

        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)

        # RAG corpus reference
        self.rag_corpus = None
        self.rag_retrieval_tool = None

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

        # Retrieval configuration
        self.rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=5,  # Retrieve top 5 most relevant chunks
            filter=rag.Filter(vector_distance_threshold=0.7),  # Similarity threshold
        )

    async def initialize_corpus(self) -> bool:
        """Initialize or get existing RAG corpus.

        Returns:
            bool: True if corpus is ready, False otherwise
        """
        try:
            # Try to get existing corpus first
            existing_corpora = rag.list_corpora()
            for corpus in existing_corpora:
                if corpus.display_name == self.corpus_display_name:
                    self.rag_corpus = corpus
                    logger.info(f"Found existing RAG corpus: {corpus.name}")
                    break

            # Create new corpus if not found
            if not self.rag_corpus:
                logger.info(f"Creating new RAG corpus: {self.corpus_display_name}")
                self.rag_corpus = rag.create_corpus(
                    display_name=self.corpus_display_name,
                    backend_config=rag.RagVectorDbConfig(
                        rag_embedding_model_config=self.embedding_model_config
                    ),
                )
                logger.info(f"Created RAG corpus: {self.rag_corpus.name}")

            # Create retrieval tool
            self._create_retrieval_tool()

            return True

        except Exception as e:
            logger.error(f"Failed to initialize RAG corpus: {e}")
            return False

    def _create_retrieval_tool(self):
        """Create RAG retrieval tool for the agent."""
        self.rag_retrieval_tool = Tool.from_retrieval(
            retrieval=rag.Retrieval(
                source=rag.VertexRagStore(
                    rag_resources=[
                        rag.RagResource(
                            rag_corpus=self.rag_corpus.name,
                        )
                    ],
                    rag_retrieval_config=self.rag_retrieval_config,
                ),
            )
        )
        logger.info("Created RAG retrieval tool")

    async def ingest_documents(self, force_reimport: bool = False) -> bool:
        """Ingest government scheme documents into RAG corpus.

        Args:
            force_reimport: Whether to reimport all documents even if already imported

        Returns:
            bool: True if ingestion successful, False otherwise
        """
        try:
            if not self.rag_corpus:
                logger.error("RAG corpus not initialized")
                return False

            # Get document paths
            document_paths = self._get_document_paths()
            if not document_paths:
                logger.warning(f"No documents found in {self.documents_path}")
                return False

            logger.info(f"Found {len(document_paths)} documents to ingest")

            # Check if documents are already imported
            if not force_reimport:
                existing_files = rag.list_files(self.rag_corpus.name)
                if existing_files:
                    logger.info(f"Found {len(existing_files)} existing files in corpus")
                    return True

            # Process and upload documents
            processed_paths = []
            for doc_path in document_paths:
                try:
                    # For local files, we need to upload to GCS first
                    gcs_path = await self._upload_to_gcs(doc_path)
                    if gcs_path:
                        processed_paths.append(gcs_path)
                except Exception as e:
                    logger.error(f"Failed to process document {doc_path}: {e}")
                    continue

            if not processed_paths:
                logger.error("No documents could be processed")
                return False

            # Import files to RAG corpus
            logger.info(f"Importing {len(processed_paths)} documents to RAG corpus")
            rag.import_files(
                self.rag_corpus.name,
                processed_paths,
                transformation_config=self.transformation_config,
                max_embedding_requests_per_min=1000,
            )

            logger.info("Successfully imported documents to RAG corpus")
            return True

        except Exception as e:
            logger.error(f"Failed to ingest documents: {e}")
            return False

    def _get_document_paths(self) -> List[str]:
        """Get all document paths from the schemes directory.

        Returns:
            List of document file paths
        """
        if not os.path.exists(self.documents_path):
            logger.warning(f"Documents path does not exist: {self.documents_path}")
            return []

        # Supported file extensions
        extensions = ["*.pdf", "*.txt", "*.docx", "*.doc"]
        document_paths = []

        for ext in extensions:
            pattern = os.path.join(self.documents_path, "**", ext)
            document_paths.extend(glob.glob(pattern, recursive=True))

        return document_paths

    async def _upload_to_gcs(self, local_path: str) -> Optional[str]:
        """Upload local document to Google Cloud Storage.

        Args:
            local_path: Path to local document

        Returns:
            GCS path if successful, None otherwise
        """
        try:
            # For this implementation, we'll assume documents are already in GCS
            # or use Google Drive links. In production, you'd implement actual GCS upload

            # For now, return the local path (this would need to be a GCS path in production)
            # This is a placeholder - in real implementation, upload to GCS bucket
            logger.warning(f"Document upload not implemented for: {local_path}")
            logger.info("Please ensure documents are available in GCS or Google Drive")

            # Return None to skip this document for now
            return None

        except Exception as e:
            logger.error(f"Failed to upload {local_path} to GCS: {e}")
            return None

    def query_schemes(self, query: str) -> Optional[str]:
        """Query the RAG corpus for relevant government schemes.

        Args:
            query: User query about government schemes

        Returns:
            Retrieved context or None if failed
        """
        try:
            if not self.rag_corpus:
                logger.error("RAG corpus not initialized")
                return None

            # Direct context retrieval
            response = rag.retrieval_query(
                rag_resources=[
                    rag.RagResource(
                        rag_corpus=self.rag_corpus.name,
                    )
                ],
                text=query,
                rag_retrieval_config=self.rag_retrieval_config,
            )

            # Extract and format retrieved contexts
            contexts = []
            if hasattr(response, "contexts") and response.contexts:
                for context in response.contexts:
                    if hasattr(context, "text"):
                        contexts.append(context.text)

            return "\n\n".join(contexts) if contexts else None

        except Exception as e:
            logger.error(f"Failed to query RAG corpus: {e}")
            return None

    def get_retrieval_tool(self) -> Optional[Tool]:
        """Get the RAG retrieval tool for the agent.

        Returns:
            RAG retrieval tool or None if not initialized
        """
        return self.rag_retrieval_tool

    def get_corpus_info(self) -> Dict[str, Any]:
        """Get information about the RAG corpus.

        Returns:
            Dictionary with corpus information
        """
        if not self.rag_corpus:
            return {"status": "not_initialized"}

        try:
            files = rag.list_files(self.rag_corpus.name)
            return {
                "status": "ready",
                "corpus_name": self.rag_corpus.name,
                "display_name": self.rag_corpus.display_name,
                "file_count": len(files) if files else 0,
                "embedding_model": "text-embedding-005",
                "chunk_size": 512,
                "chunk_overlap": 100,
                "top_k": self.rag_retrieval_config.top_k,
            }
        except Exception as e:
            logger.error(f"Failed to get corpus info: {e}")
            return {"status": "error", "error": str(e)}
