"""
Government Schemes Agent Tools
=============================

Simple RAG-powered tools for government scheme assistance:
- List corpus files
- Search corpus for information
"""

import logging
from typing import Dict, List, Any, Optional
from .corpus_manager import CorpusManager

logger = logging.getLogger(__name__)

# Initialize corpus manager (will be set by agent)
_corpus_manager: Optional[CorpusManager] = None


def set_corpus_manager(corpus_manager: CorpusManager) -> None:
    """Set the corpus manager for RAG operations.

    Args:
        corpus_manager: Initialized CorpusManager instance
    """
    global _corpus_manager
    _corpus_manager = corpus_manager
    logger.info("Corpus manager set for tools")


def list_corpus_files() -> Dict[str, Any]:
    """List all files available in the RAG corpus.

    Returns:
        Dictionary with information about available corpus files
    """
    try:
        if not _corpus_manager or not _corpus_manager.is_ready():
            return {
                "error": "Corpus manager not initialized or not ready",
                "files": [],
                "status": "not_ready"
            }

        # Get corpus information and files
        corpus_info = _corpus_manager.get_corpus_info()
        corpus_files = _corpus_manager.get_corpus_files()
        
        if corpus_files is None:
            corpus_files = []
        
        return {
            "status": "ready",
            "total_files": len(corpus_files),
            "files": corpus_files,
            "corpus_ready": _corpus_manager.is_ready(),
            "corpus_name": corpus_info.get("corpus_name"),
            "created_at": corpus_info.get("created_at"),
            "recommendations": [
                "Use search_corpus() to find specific information",
                "Browse file names to understand available content",
                "Files contain government scheme guidelines and procedures"
            ]
        }

    except Exception as e:
        logger.error(f"Error listing corpus files: {e}")
        return {
            "error": str(e),
            "files": [],
            "status": "error",
            "recommendations": ["Please try again or contact support"]
        }


def search_corpus(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Search the RAG corpus for information related to government schemes.

    Args:
        query: Search query for government scheme information
        max_results: Maximum number of results to return

    Returns:
        Dictionary with search results from the corpus
    """
    try:
        if not _corpus_manager or not _corpus_manager.is_ready():
            return {
                "error": "Corpus manager not initialized or not ready",
                "results": [],
                "status": "not_ready"
            }

        logger.info(f"Searching corpus for: {query}")

        # Query the corpus
        search_results = _corpus_manager.query_corpus(query, max_results=max_results)

        if not search_results:
            return {
                "query": query,
                "results": [],
                "status": "no_results",
                "recommendations": [
                    "Try using different keywords",
                    "Use broader search terms",
                    "Check if the corpus contains relevant documents"
                ]
            }

        return {
            "query": query,
            "results": search_results,
            "status": "success",
            "total_results": len(search_results) if isinstance(search_results, list) else 1,
            "recommendations": [
                "Review the search results above for relevant information",
                "Try more specific queries for detailed information",
                "Use list_corpus_files() to see all available documents"
            ]
        }

    except Exception as e:
        logger.error(f"Error searching corpus: {e}")
        return {
            "error": str(e),
            "query": query,
            "results": [],
            "status": "error",
            "recommendations": ["Please try again or contact support"]
        }
