"""
Government Schemes RAG Service
=============================

Service layer for government schemes RAG agent integration.
"""

import logging
import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path

# Add agents directory to Python path
agents_path = Path(__file__).parent.parent.parent.parent / "agents"
sys.path.insert(0, str(agents_path))

from government_schemes_agent.agent import get_government_schemes_agent
from government_schemes_agent.tools import (
    check_scheme_eligibility,
    get_scheme_categories,
    validate_documents,
    get_application_status
)

logger = logging.getLogger("project-kisan")

class GovernmentRAGService:
    """Service for government schemes RAG operations."""
    
    def __init__(self):
        """Initialize the Government RAG Service."""
        self.agent = None
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the RAG service.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            if self.initialized:
                return True
            
            logger.info("Initializing Government RAG Service...")
            
            # Get the government schemes agent
            self.agent = await get_government_schemes_agent()
            
            if self.agent and self.agent.initialized:
                self.initialized = True
                logger.info("Government RAG Service initialized successfully")
                return True
            else:
                logger.error("Failed to initialize government schemes agent")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing Government RAG Service: {e}")
            return False
    
    async def query_schemes(
        self,
        query: str,
        language: str = "english",
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query government schemes using RAG.
        
        Args:
            query: User's query about government schemes
            language: Response language
            user_context: Additional user context
            
        Returns:
            Dictionary with query results
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            if not self.agent:
                return {
                    "success": False,
                    "error": "Government schemes agent not available",
                    "response": "Service temporarily unavailable. Please try again later.",
                    "source": "error",
                    "query": query
                }
            
            logger.info(f"Processing government scheme query: {query[:100]}...")
            
            # Query the agent
            result = await self.agent.query_schemes(query, user_context)
            
            # Add language and timestamp
            result["language"] = language
            result["timestamp"] = result.get("timestamp") or "now"
            
            return result
            
        except Exception as e:
            logger.error(f"Error querying government schemes: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "An error occurred while processing your query. Please try again.",
                "source": "error",
                "query": query,
                "language": language
            }
    
    async def check_eligibility(
        self,
        query: str,
        farmer_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check farmer eligibility for government schemes.
        
        Args:
            query: Farmer's query
            farmer_profile: Farmer's profile information
            
        Returns:
            Dictionary with eligibility results
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Checking eligibility for query: {query[:100]}...")
            
            if self.agent:
                # Use agent's eligibility checking
                result = await self.agent.check_eligibility(query, farmer_profile)
            else:
                # Fallback to direct tool usage
                eligibility_result = check_scheme_eligibility(
                    query=query,
                    land_size=farmer_profile.get("land_size"),
                    crop_type=farmer_profile.get("crop_type"),
                    location=farmer_profile.get("location"),
                    farmer_category=farmer_profile.get("farmer_category")
                )
                
                result = {
                    "success": True,
                    "eligible_schemes": eligibility_result.get("eligible_schemes", []),
                    "ineligible_schemes": eligibility_result.get("ineligible_schemes", []),
                    "farmer_profile": farmer_profile,
                    "recommendations": eligibility_result.get("recommendations", []),
                    "query": query
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking eligibility: {e}")
            return {
                "success": False,
                "error": str(e),
                "eligible_schemes": [],
                "ineligible_schemes": [],
                "farmer_profile": farmer_profile,
                "recommendations": [],
                "query": query
            }
    
    def get_scheme_categories(self) -> Dict[str, Any]:
        """Get available scheme categories.
        
        Returns:
            Dictionary with scheme categories
        """
        try:
            logger.info("Getting scheme categories")
            return get_scheme_categories()
            
        except Exception as e:
            logger.error(f"Error getting scheme categories: {e}")
            return {
                "error": str(e),
                "categories": {},
                "total_categories": 0
            }
    
    def validate_documents(
        self,
        scheme_type: str,
        available_documents: list
    ) -> Dict[str, Any]:
        """Validate documents for a scheme.
        
        Args:
            scheme_type: Type of scheme
            available_documents: List of available documents
            
        Returns:
            Dictionary with validation results
        """
        try:
            logger.info(f"Validating documents for scheme: {scheme_type}")
            return validate_documents(scheme_type, available_documents)
            
        except Exception as e:
            logger.error(f"Error validating documents: {e}")
            return {
                "valid": False,
                "error": str(e),
                "scheme_type": scheme_type,
                "required_documents": [],
                "available_documents": available_documents,
                "missing_documents": [],
                "extra_documents": [],
                "completion_percentage": 0
            }
    
    def get_application_status(
        self,
        application_id: str,
        scheme_type: str
    ) -> Dict[str, Any]:
        """Get application status.
        
        Args:
            application_id: Application reference number
            scheme_type: Type of scheme
            
        Returns:
            Dictionary with application status
        """
        try:
            logger.info(f"Getting application status: {application_id}")
            return get_application_status(application_id, scheme_type)
            
        except Exception as e:
            logger.error(f"Error getting application status: {e}")
            return {
                "error": str(e),
                "application_id": application_id,
                "scheme_type": scheme_type,
                "status": "unknown",
                "last_updated": "now",
                "next_steps": [],
                "contact_info": {}
            }
    
    async def get_corpus_status(self) -> Dict[str, Any]:
        """Get RAG corpus status.
        
        Returns:
            Dictionary with corpus status
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            if self.agent:
                return self.agent.get_corpus_status()
            else:
                return {
                    "status": "not_initialized",
                    "error": "Agent not available"
                }
                
        except Exception as e:
            logger.error(f"Error getting corpus status: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def refresh_corpus(self, force_reimport: bool = False) -> Dict[str, Any]:
        """Refresh the RAG corpus with latest documents.
        
        Note: Corpus refresh is now handled separately via corpus_setup.py
        This method returns information about the manual process.
        
        Args:
            force_reimport: Whether to force reimport all documents
            
        Returns:
            Dictionary with refresh information
        """
        try:
            return {
                "success": False,
                "message": "Corpus refresh is now handled separately. Please use corpus_setup.py script.",
                "instructions": [
                    "1. Navigate to agents/government_schemes_agent/",
                    "2. Run: python corpus_setup.py --project-id YOUR_PROJECT_ID",
                    "3. Use --force-recreate flag to force reimport",
                    "4. Restart the backend service to pick up changes"
                ]
            }
                
        except Exception as e:
            logger.error(f"Error in refresh corpus: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

# Global service instance
_government_rag_service = None

async def get_government_rag_service() -> GovernmentRAGService:
    """Get or create the government RAG service instance.
    
    Returns:
        GovernmentRAGService instance
    """
    global _government_rag_service
    
    if _government_rag_service is None:
        _government_rag_service = GovernmentRAGService()
        await _government_rag_service.initialize()
    
    return _government_rag_service
