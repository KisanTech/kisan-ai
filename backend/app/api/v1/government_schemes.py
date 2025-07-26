"""
Government Schemes API Endpoints
===============================

FastAPI endpoints for government schemes RAG functionality.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.government_schemes import (
    SchemeQueryRequest,
    SchemeQueryResponse,
    EligibilityCheckRequest,
    EligibilityCheckResponse,
    DocumentValidationRequest,
    DocumentValidationResult,
    ApplicationStatusRequest,
    ApplicationStatus,
    SchemeCategoriesResponse,
    CorpusStatusResponse,
    CorpusRefreshRequest,
    CorpusRefreshResponse
)
from app.services.government_rag_service import get_government_rag_service

logger = logging.getLogger("project-kisan")

router = APIRouter(prefix="/government-schemes", tags=["Government Schemes"])

@router.post("/query", response_model=SchemeQueryResponse)
async def query_government_schemes(request: SchemeQueryRequest) -> SchemeQueryResponse:
    """Query government schemes using RAG.
    
    This endpoint allows farmers to ask questions about government schemes
    and get relevant information using RAG (Retrieval-Augmented Generation).
    
    Args:
        request: Query request with user's question and context
        
    Returns:
        SchemeQueryResponse with relevant scheme information
        
    Example:
        ```
        POST /api/v1/government-schemes/query
        {
            "query": "मुझे ड्रिप सिंचाई के लिए सब्सिडी चाहिए",
            "language": "hindi",
            "user_context": {
                "location": "Punjab",
                "crop_type": "wheat"
            }
        }
        ```
    """
    try:
        logger.info(f"Government scheme query: {request.query[:100]}...")
        
        # Get the RAG service
        rag_service = await get_government_rag_service()
        
        # Query schemes
        result = await rag_service.query_schemes(
            query=request.query,
            language=request.language,
            user_context=request.user_context
        )
        
        return SchemeQueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in government scheme query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process government scheme query: {str(e)}"
        )

@router.post("/eligibility-check", response_model=EligibilityCheckResponse)
async def check_scheme_eligibility(request: EligibilityCheckRequest) -> EligibilityCheckResponse:
    """Check farmer eligibility for government schemes.
    
    This endpoint checks which government schemes a farmer is eligible for
    based on their profile information.
    
    Args:
        request: Eligibility check request with farmer profile
        
    Returns:
        EligibilityCheckResponse with eligible and ineligible schemes
        
    Example:
        ```
        POST /api/v1/government-schemes/eligibility-check
        {
            "query": "Which schemes am I eligible for?",
            "farmer_profile": {
                "land_size": "2 acres",
                "crop_type": "rice",
                "location": "Punjab",
                "farmer_category": "small"
            }
        }
        ```
    """
    try:
        logger.info(f"Eligibility check for: {request.farmer_profile}")
        
        # Get the RAG service
        rag_service = await get_government_rag_service()
        
        # Check eligibility
        result = await rag_service.check_eligibility(
            query=request.query,
            farmer_profile=request.farmer_profile.dict()
        )
        
        return EligibilityCheckResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in eligibility check: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check scheme eligibility: {str(e)}"
        )

@router.get("/categories", response_model=SchemeCategoriesResponse)
async def get_scheme_categories() -> SchemeCategoriesResponse:
    """Get available government scheme categories.
    
    This endpoint returns all available scheme categories with their
    descriptions and associated schemes.
    
    Returns:
        SchemeCategoriesResponse with scheme categories
        
    Example:
        ```
        GET /api/v1/government-schemes/categories
        ```
    """
    try:
        logger.info("Getting scheme categories")
        
        # Get the RAG service
        rag_service = await get_government_rag_service()
        
        # Get categories
        result = rag_service.get_scheme_categories()
        
        return SchemeCategoriesResponse(**result)
        
    except Exception as e:
        logger.error(f"Error getting scheme categories: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scheme categories: {str(e)}"
        )

@router.post("/validate-documents", response_model=DocumentValidationResult)
async def validate_scheme_documents(request: DocumentValidationRequest) -> DocumentValidationResult:
    """Validate documents for a government scheme.
    
    This endpoint checks if a farmer has all required documents
    for a specific government scheme.
    
    Args:
        request: Document validation request
        
    Returns:
        DocumentValidationResult with validation status
        
    Example:
        ```
        POST /api/v1/government-schemes/validate-documents
        {
            "scheme_type": "pm_kisan",
            "available_documents": [
                "aadhaar_card",
                "land_records",
                "bank_account"
            ]
        }
        ```
    """
    try:
        logger.info(f"Validating documents for scheme: {request.scheme_type}")
        
        # Get the RAG service
        rag_service = await get_government_rag_service()
        
        # Validate documents
        result = rag_service.validate_documents(
            scheme_type=request.scheme_type,
            available_documents=request.available_documents
        )
        
        return DocumentValidationResult(**result)
        
    except Exception as e:
        logger.error(f"Error validating documents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate documents: {str(e)}"
        )

@router.post("/application-status", response_model=ApplicationStatus)
async def get_application_status(request: ApplicationStatusRequest) -> ApplicationStatus:
    """Get application status for a government scheme.
    
    This endpoint retrieves the current status of a farmer's
    government scheme application.
    
    Args:
        request: Application status request
        
    Returns:
        ApplicationStatus with current status information
        
    Example:
        ```
        POST /api/v1/government-schemes/application-status
        {
            "application_id": "PM123456789",
            "scheme_type": "pm_kisan"
        }
        ```
    """
    try:
        logger.info(f"Getting application status: {request.application_id}")
        
        # Get the RAG service
        rag_service = await get_government_rag_service()
        
        # Get application status
        result = rag_service.get_application_status(
            application_id=request.application_id,
            scheme_type=request.scheme_type
        )
        
        return ApplicationStatus(**result)
        
    except Exception as e:
        logger.error(f"Error getting application status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get application status: {str(e)}"
        )

@router.get("/corpus-status", response_model=CorpusStatusResponse)
async def get_corpus_status() -> CorpusStatusResponse:
    """Get RAG corpus status.
    
    This endpoint returns the current status of the government schemes
    RAG corpus including file count and health information.
    
    Returns:
        CorpusStatusResponse with corpus status
        
    Example:
        ```
        GET /api/v1/government-schemes/corpus-status
        ```
    """
    try:
        logger.info("Getting corpus status")
        
        # Get the RAG service
        rag_service = await get_government_rag_service()
        
        # Get corpus status
        corpus_status = await rag_service.get_corpus_status()
        
        return CorpusStatusResponse(corpus_status=corpus_status)
        
    except Exception as e:
        logger.error(f"Error getting corpus status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get corpus status: {str(e)}"
        )

@router.post("/refresh-corpus", response_model=CorpusRefreshResponse)
async def refresh_corpus(
    request: CorpusRefreshRequest,
    background_tasks: BackgroundTasks
) -> CorpusRefreshResponse:
    """Refresh the RAG corpus with latest documents.
    
    This endpoint triggers a refresh of the government schemes RAG corpus,
    optionally forcing a complete reimport of all documents.
    
    Args:
        request: Corpus refresh request
        background_tasks: FastAPI background tasks
        
    Returns:
        CorpusRefreshResponse with refresh status
        
    Example:
        ```
        POST /api/v1/government-schemes/refresh-corpus
        {
            "force_reimport": false
        }
        ```
    """
    try:
        logger.info(f"Refreshing corpus (force_reimport={request.force_reimport})")
        
        # Get the RAG service
        rag_service = await get_government_rag_service()
        
        # Start corpus refresh in background
        async def refresh_task():
            await rag_service.refresh_corpus(force_reimport=request.force_reimport)
        
        background_tasks.add_task(refresh_task)
        
        return CorpusRefreshResponse(
            success=True,
            message="Corpus refresh started in background"
        )
        
    except Exception as e:
        logger.error(f"Error refreshing corpus: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh corpus: {str(e)}"
        )

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for government schemes service.
    
    Returns:
        Dictionary with service health status
    """
    try:
        # Get the RAG service
        rag_service = await get_government_rag_service()
        
        # Check if service is initialized
        service_status = "healthy" if rag_service.initialized else "initializing"
        
        # Get corpus status
        corpus_status = await rag_service.get_corpus_status()
        
        return {
            "status": service_status,
            "service": "government_schemes_rag",
            "corpus_status": corpus_status.get("status", "unknown"),
            "corpus_files": corpus_status.get("file_count", 0),
            "timestamp": "now"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "government_schemes_rag",
            "error": str(e),
            "timestamp": "now"
        }
