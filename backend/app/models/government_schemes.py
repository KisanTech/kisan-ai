"""
Government Schemes Models
========================

Pydantic models for government schemes API requests and responses.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SchemeQueryRequest(BaseModel):
    """Request model for government scheme queries."""

    query: str = Field(..., description="User's query about government schemes")
    language: str | None = Field(
        "english", description="Response language (hindi, english, kannada)"
    )
    user_context: dict[str, Any] | None = Field(None, description="Additional user context")


class FarmerProfile(BaseModel):
    """Farmer profile information for eligibility checking."""

    land_size: str | None = Field(None, description="Size of farmer's land (e.g., '2 acres')")
    crop_type: str | None = Field(None, description="Type of crop grown")
    location: str | None = Field(None, description="Farmer's location (state/district)")
    farmer_category: str | None = Field(
        None, description="Farmer category (small/marginal/medium/large)"
    )


class EligibilityCheckRequest(BaseModel):
    """Request model for scheme eligibility checking."""

    query: str = Field(..., description="Farmer's query about schemes")
    farmer_profile: FarmerProfile = Field(..., description="Farmer's profile information")


class DocumentValidationRequest(BaseModel):
    """Request model for document validation."""

    scheme_type: str = Field(..., description="Type of scheme")
    available_documents: list[str] = Field(..., description="List of documents farmer has")


class ApplicationStatusRequest(BaseModel):
    """Request model for application status checking."""

    application_id: str = Field(..., description="Application reference number")
    scheme_type: str = Field(..., description="Type of scheme")


class SchemeInfo(BaseModel):
    """Information about a government scheme."""

    scheme_id: str = Field(..., description="Unique scheme identifier")
    scheme_name: str = Field(..., description="Official scheme name")
    description: str | None = Field(None, description="Brief description of the scheme")
    eligibility: list[str] | None = Field(None, description="Eligibility criteria")
    benefits: list[str] | None = Field(None, description="Key benefits")
    required_documents: list[str] | None = Field(None, description="Required documents")
    application_process: list[str] | None = Field(None, description="Application steps")
    portal_url: str | None = Field(None, description="Official portal URL")
    helpline: str | None = Field(None, description="Helpline number")


class EligibilityResult(BaseModel):
    """Result of eligibility check for a scheme."""

    scheme_id: str = Field(..., description="Scheme identifier")
    scheme_name: str = Field(..., description="Scheme name")
    eligible: bool = Field(..., description="Whether farmer is eligible")
    reasons: list[str] = Field(..., description="Reasons for eligibility/ineligibility")
    required_documents: list[str] = Field(..., description="Required documents for the scheme")


class DocumentValidationResult(BaseModel):
    """Result of document validation."""

    valid: bool = Field(..., description="Whether all required documents are available")
    scheme_type: str = Field(..., description="Type of scheme")
    required_documents: list[str] = Field(..., description="Required documents")
    available_documents: list[str] = Field(..., description="Available documents")
    missing_documents: list[str] = Field(..., description="Missing documents")
    extra_documents: list[str] = Field(..., description="Extra documents")
    completion_percentage: float = Field(..., description="Percentage of documents available")
    recommendations: list[str] | None = Field(
        None, description="Recommendations for missing documents"
    )


class ApplicationStatus(BaseModel):
    """Application status information."""

    application_id: str = Field(..., description="Application reference number")
    scheme_type: str = Field(..., description="Type of scheme")
    status: str = Field(..., description="Current status")
    submitted_date: str | None = Field(None, description="Submission date")
    last_updated: str = Field(..., description="Last update timestamp")
    next_steps: list[str] = Field(..., description="Next steps in the process")
    contact_info: dict[str, str] = Field(..., description="Contact information")
    note: str | None = Field(None, description="Additional notes")


class CorpusStatus(BaseModel):
    """RAG corpus status information."""

    status: str = Field(..., description="Corpus status")
    corpus_name: str | None = Field(None, description="Corpus name")
    display_name: str | None = Field(None, description="Display name")
    file_count: int = Field(0, description="Number of files in corpus")
    embedding_model: str | None = Field(None, description="Embedding model used")
    chunk_size: int | None = Field(None, description="Chunk size for documents")
    chunk_overlap: int | None = Field(None, description="Chunk overlap")
    top_k: int | None = Field(None, description="Top K retrieval setting")
    error: str | None = Field(None, description="Error message if any")


class SchemeQueryResponse(BaseModel):
    """Response model for government scheme queries."""

    success: bool = Field(..., description="Whether the query was successful")
    response: str = Field(..., description="Generated response text")
    source: str = Field(
        ..., description="Source of the response (rag_model, rag_retrieval, fallback)"
    )
    query: str = Field(..., description="Original query")
    user_context: dict[str, Any] | None = Field(None, description="User context")
    retrieved_context: str | None = Field(None, description="Retrieved context from RAG")
    error: str | None = Field(None, description="Error message if any")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class EligibilityCheckResponse(BaseModel):
    """Response model for eligibility checking."""

    success: bool = Field(..., description="Whether the check was successful")
    eligible_schemes: list[EligibilityResult] = Field(
        ..., description="Schemes farmer is eligible for"
    )
    ineligible_schemes: list[EligibilityResult] = Field(
        ..., description="Schemes farmer is not eligible for"
    )
    farmer_profile: FarmerProfile = Field(..., description="Farmer profile used for checking")
    recommendations: list[str] = Field(..., description="Recommendations based on eligibility")
    error: str | None = Field(None, description="Error message if any")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class SchemeCategoriesResponse(BaseModel):
    """Response model for scheme categories."""

    categories: dict[str, dict[str, Any]] = Field(..., description="Available scheme categories")
    total_categories: int = Field(..., description="Total number of categories")
    last_updated: str = Field(..., description="Last update timestamp")
    error: str | None = Field(None, description="Error message if any")


class CorpusStatusResponse(BaseModel):
    """Response model for corpus status."""

    corpus_status: CorpusStatus = Field(..., description="RAG corpus status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class CorpusRefreshRequest(BaseModel):
    """Request model for corpus refresh."""

    force_reimport: bool = Field(False, description="Whether to force reimport all documents")


class CorpusRefreshResponse(BaseModel):
    """Response model for corpus refresh."""

    success: bool = Field(..., description="Whether refresh was successful")
    message: str = Field(..., description="Status message")
    corpus_status: CorpusStatus | None = Field(None, description="Updated corpus status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
