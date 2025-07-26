"""
Government Schemes Corpus Manager
================================

Lightweight manager that references an existing RAG corpus.
Does not handle corpus creation - that's done separately via corpus_setup.py
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import vertexai
from vertexai import rag
from vertexai.generative_models import Tool

logger = logging.getLogger(__name__)


class CorpusManager:
    """Lightweight manager for existing RAG corpus."""

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        config_file: str = "corpus_config.json",
    ):
        """Initialize corpus manager.

        Args:
            project_id: Google Cloud project ID
            location: Vertex AI location
            config_file: Path to corpus configuration file
        """
        self.project_id = project_id
        self.location = location
        self.config_file = config_file

        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)

        # Corpus configuration
        self.corpus_config = None
        self.rag_retrieval_tool = None

        # Retrieval configuration
        self.rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=5,  # Retrieve top 5 most relevant chunks
            filter=rag.Filter(vector_distance_threshold=0.7),  # Similarity threshold
        )

    def load_corpus_config(self) -> bool:
        """Load corpus configuration from file.

        Returns:
            True if configuration loaded successfully, False otherwise
        """
        try:
            config_path = Path(self.config_file)
            if not config_path.exists():
                logger.error(f"Corpus configuration file not found: {config_path}")
                logger.info("Please run corpus_setup.py first to create the corpus")
                return False

            with open(config_path, "r") as f:
                self.corpus_config = json.load(f)

            if self.corpus_config.get("status") != "ready":
                logger.error("Corpus is not ready according to configuration")
                return False

            logger.info(f"Loaded corpus configuration: {self.corpus_config['corpus_name']}")
            return True

        except Exception as e:
            logger.error(f"Failed to load corpus configuration: {e}")
            return False

    def create_retrieval_tool(self) -> bool:
        """Create RAG retrieval tool from existing corpus.

        Returns:
            True if tool created successfully, False otherwise
        """
        try:
            if not self.corpus_config:
                logger.error("Corpus configuration not loaded")
                return False

            corpus_name = self.corpus_config["corpus_name"]

            # Verify corpus exists
            try:
                files = rag.list_files(corpus_name)
                logger.info(f"Corpus verified with {len(files) if files else 0} files")
            except Exception as e:
                logger.error(f"Failed to verify corpus {corpus_name}: {e}")
                return False

            # Create retrieval tool
            self.rag_retrieval_tool = Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_resources=[
                            rag.RagResource(
                                rag_corpus=corpus_name,
                            )
                        ],
                        rag_retrieval_config=self.rag_retrieval_config,
                    ),
                )
            )

            logger.info("RAG retrieval tool created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create retrieval tool: {e}")
            return False

    def initialize(self) -> bool:
        """Initialize the corpus manager.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing corpus manager...")

            # Load configuration
            if not self.load_corpus_config():
                return False

            # Create retrieval tool
            if not self.create_retrieval_tool():
                return False

            logger.info("Corpus manager initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize corpus manager: {e}")
            return False

    def query_corpus(self, query: str) -> Optional[str]:
        """Query the RAG corpus directly.

        Args:
            query: User query

        Returns:
            Retrieved context or None if failed
        """
        try:
            if not self.corpus_config:
                logger.error("Corpus not initialized")
                return None

            corpus_name = self.corpus_config["corpus_name"]

            # Direct context retrieval
            response = rag.retrieval_query(
                rag_resources=[
                    rag.RagResource(
                        rag_corpus=corpus_name,
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
            logger.error(f"Failed to query corpus: {e}")
            return None

    def get_retrieval_tool(self) -> Optional[Tool]:
        """Get the RAG retrieval tool.

        Returns:
            RAG retrieval tool or None if not initialized
        """
        return self.rag_retrieval_tool

    def get_corpus_info(self) -> Dict[str, Any]:
        """Get corpus information.

        Returns:
            Dictionary with corpus information
        """
        if not self.corpus_config:
            return {"status": "not_initialized", "message": "Corpus configuration not loaded"}

        try:
            corpus_name = self.corpus_config["corpus_name"]

            # Get current file count
            try:
                files = rag.list_files(corpus_name)
                current_file_count = len(files) if files else 0
            except:
                current_file_count = self.corpus_config.get("file_count", 0)

            return {
                "status": "ready",
                "corpus_name": corpus_name,
                "display_name": self.corpus_config["display_name"],
                "file_count": current_file_count,
                "embedding_model": self.corpus_config["embedding_model"],
                "chunk_size": self.corpus_config["chunk_size"],
                "chunk_overlap": self.corpus_config["chunk_overlap"],
                "top_k": self.rag_retrieval_config.top_k,
                "created_at": self.corpus_config["created_at"],
                "project_id": self.corpus_config["project_id"],
                "location": self.corpus_config["location"],
            }

        except Exception as e:
            logger.error(f"Failed to get corpus info: {e}")
            return {"status": "error", "error": str(e), "config": self.corpus_config}

    def is_ready(self) -> bool:
        """Check if corpus manager is ready for use.

        Returns:
            True if ready, False otherwise
        """
        return (
            self.corpus_config is not None
            and self.corpus_config.get("status") == "ready"
            and self.rag_retrieval_tool is not None
        )
