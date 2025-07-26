"""
Government Schemes Agent Tools
=============================

RAG-powered tools for government scheme assistance including:
- Eligibility checking via corpus search
- Document validation
- Scheme categorization
- Application guidance
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
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


def _query_corpus(query: str) -> Optional[str]:
    """Query the RAG corpus for information.

    Args:
        query: Search query

    Returns:
        Retrieved context or None if failed
    """
    if not _corpus_manager or not _corpus_manager.is_ready():
        logger.error("Corpus manager not initialized or not ready")
        return None

    return _corpus_manager.query_corpus(query)


def check_scheme_eligibility(
    query: str,
    land_size: Optional[str] = None,
    crop_type: Optional[str] = None,
    location: Optional[str] = None,
    farmer_category: Optional[str] = None,
) -> Dict[str, Any]:
    """Check farmer eligibility for government schemes using RAG search.

    Args:
        query: Farmer's query about schemes
        land_size: Size of farmer's land (e.g., "2 acres", "0.5 hectares")
        crop_type: Type of crop grown (e.g., "rice", "wheat", "vegetables")
        location: Farmer's location (state/district)
        farmer_category: Category of farmer (small/marginal/medium/large)

    Returns:
        Dictionary with eligibility information from corpus
    """
    try:
        logger.info(f"Checking eligibility for query: {query}")

        # Build comprehensive search query
        search_parts = [query]

        if land_size:
            search_parts.append(f"land size {land_size}")
        if crop_type:
            search_parts.append(f"crop {crop_type}")
        if location:
            search_parts.append(f"location {location}")
        if farmer_category:
            search_parts.append(f"{farmer_category} farmer")

        # Add eligibility-specific terms
        search_parts.extend(
            ["eligibility criteria", "requirements", "who can apply", "farmer categories"]
        )

        eligibility_query = " ".join(search_parts)

        # Query corpus for eligibility information
        eligibility_context = _query_corpus(eligibility_query)

        if not eligibility_context:
            return {
                "error": "Unable to retrieve eligibility information from corpus",
                "eligible_schemes": [],
                "recommendations": ["Please ensure the corpus is properly initialized"],
            }

        # Also search for specific schemes mentioned in the query
        schemes_query = f"{query} schemes programs benefits"
        schemes_context = _query_corpus(schemes_query)

        return {
            "eligibility_information": eligibility_context,
            "scheme_details": schemes_context,
            "farmer_profile": {
                "land_size": land_size,
                "crop_type": crop_type,
                "location": location,
                "category": farmer_category,
            },
            "search_query": eligibility_query,
            "recommendations": [
                "Review the eligibility information above for applicable schemes",
                "Check specific requirements for schemes that interest you",
                "Prepare required documents as mentioned in the scheme details",
            ],
        }

    except Exception as e:
        logger.error(f"Error checking scheme eligibility: {e}")
        return {
            "error": str(e),
            "eligible_schemes": [],
            "recommendations": ["Please try again or contact support"],
        }


def get_scheme_categories() -> Dict[str, Any]:
    """Get available scheme categories using RAG search.

    Returns:
        Dictionary with scheme categories from corpus
    """
    try:
        logger.info("Retrieving scheme categories from corpus")

        # Query for scheme categories and types
        categories_query = (
            "government schemes categories types classification "
            "irrigation income support crop insurance credit subsidies technology "
            "PM-KISAN PMKSY Fasal Bima KCC agricultural schemes"
        )

        categories_context = _query_corpus(categories_query)

        if not categories_context:
            return {"error": "Unable to retrieve scheme categories from corpus", "categories": {}}

        # Also get a general overview of available schemes
        overview_query = "list of government schemes for farmers agricultural programs"
        overview_context = _query_corpus(overview_query)

        return {
            "categories_information": categories_context,
            "schemes_overview": overview_context,
            "search_query": categories_query,
            "recommendations": [
                "Browse through the categories to find schemes relevant to your needs",
                "Check eligibility criteria for schemes that interest you",
                "Contact local agricultural offices for application assistance",
            ],
        }

    except Exception as e:
        logger.error(f"Error retrieving scheme categories: {e}")
        return {
            "error": str(e),
            "categories": {},
            "recommendations": ["Please try again or contact support"],
        }


def validate_documents(scheme_type: str, available_documents: List[str]) -> Dict[str, Any]:
    """Validate documents for a scheme using RAG search.

    Args:
        scheme_type: Type of scheme (e.g., "PM-KISAN", "PMKSY")
        available_documents: List of documents farmer has

    Returns:
        Dictionary with document validation results from corpus
    """
    try:
        logger.info(f"Validating documents for scheme: {scheme_type}")

        # Query for document requirements
        docs_query = (
            f"{scheme_type} scheme required documents application documents "
            f"eligibility documents needed papers certificates"
        )

        docs_context = _query_corpus(docs_query)

        if not docs_context:
            return {
                "error": f"Unable to retrieve document requirements for {scheme_type}",
                "validation_result": "unknown",
            }

        # Also search for general document requirements
        general_docs_query = (
            "common documents required government schemes "
            "aadhaar land records bank account certificates"
        )

        general_context = _query_corpus(general_docs_query)

        return {
            "scheme_type": scheme_type,
            "available_documents": available_documents,
            "document_requirements": docs_context,
            "general_requirements": general_context,
            "search_query": docs_query,
            "recommendations": [
                "Compare your available documents with the requirements listed above",
                "Obtain any missing documents before applying",
                "Ensure all documents are valid and up-to-date",
                "Keep both original and photocopies ready",
            ],
        }

    except Exception as e:
        logger.error(f"Error validating documents: {e}")
        return {"error": str(e), "scheme_type": scheme_type, "validation_result": "error"}


def get_application_guidance(
    scheme_name: str, farmer_location: Optional[str] = None
) -> Dict[str, Any]:
    """Get application guidance for a scheme using RAG search.

    Args:
        scheme_name: Name of the scheme
        farmer_location: Farmer's location for local guidance

    Returns:
        Dictionary with application guidance from corpus
    """
    try:
        logger.info(f"Getting application guidance for: {scheme_name}")

        # Query for application process
        application_query = (
            f"{scheme_name} application process how to apply "
            f"application form online offline procedure steps"
        )

        if farmer_location:
            application_query += f" {farmer_location}"

        application_context = _query_corpus(application_query)

        if not application_context:
            return {
                "error": f"Unable to retrieve application guidance for {scheme_name}",
                "guidance": {},
            }

        # Also search for contact information and deadlines
        contact_query = (
            f"{scheme_name} contact information helpline office application deadline last date"
        )

        if farmer_location:
            contact_query += f" {farmer_location}"

        contact_context = _query_corpus(contact_query)

        return {
            "scheme_name": scheme_name,
            "farmer_location": farmer_location,
            "application_guidance": application_context,
            "contact_information": contact_context,
            "search_query": application_query,
            "recommendations": [
                "Follow the application steps mentioned above carefully",
                "Prepare all required documents before starting application",
                "Note important deadlines and contact information",
                "Keep application reference numbers for tracking",
            ],
        }

    except Exception as e:
        logger.error(f"Error getting application guidance: {e}")
        return {"error": str(e), "scheme_name": scheme_name, "guidance": {}}


def search_schemes_by_need(
    farmer_need: str, additional_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Search for schemes based on farmer's specific need using RAG.

    Args:
        farmer_need: Specific need (e.g., "irrigation", "loan", "crop insurance")
        additional_context: Additional farmer context (land size, crop, location)

    Returns:
        Dictionary with relevant schemes from corpus
    """
    try:
        logger.info(f"Searching schemes for need: {farmer_need}")

        # Build comprehensive search query
        search_parts = [farmer_need, "schemes", "programs", "benefits"]

        if additional_context:
            for key, value in additional_context.items():
                if value:
                    search_parts.append(f"{key} {value}")

        need_query = " ".join(search_parts)

        # Query corpus for relevant schemes
        schemes_context = _query_corpus(need_query)

        if not schemes_context:
            return {"error": f"Unable to find schemes for need: {farmer_need}", "schemes": []}

        # Also search for benefits and features
        benefits_query = f"{farmer_need} benefits features advantages support"
        benefits_context = _query_corpus(benefits_query)

        return {
            "farmer_need": farmer_need,
            "additional_context": additional_context,
            "relevant_schemes": schemes_context,
            "benefits_information": benefits_context,
            "search_query": need_query,
            "recommendations": [
                "Review the schemes listed above that match your needs",
                "Check eligibility criteria for each relevant scheme",
                "Compare benefits and choose the most suitable options",
                "Prepare required documents for application",
            ],
        }

    except Exception as e:
        logger.error(f"Error searching schemes by need: {e}")
        return {"error": str(e), "farmer_need": farmer_need, "schemes": []}


def get_application_status(application_id: str, scheme_type: str) -> Dict[str, Any]:
    """Get application status for a government scheme using RAG search.

    Args:
        application_id: Application reference number
        scheme_type: Type of scheme

    Returns:
        Dictionary with application status information from corpus
    """
    try:
        logger.info(f"Checking application status: {application_id} for {scheme_type}")

        # Query for application status and tracking information
        status_query = (
            f"{scheme_type} application status tracking "
            f"how to check status application number {application_id}"
        )

        status_context = _query_corpus(status_query)

        # Also search for general status checking procedures
        general_status_query = (
            "government scheme application status check tracking portal online status verification"
        )

        general_context = _query_corpus(general_status_query)

        return {
            "application_id": application_id,
            "scheme_type": scheme_type,
            "status_information": status_context,
            "general_tracking_info": general_context,
            "search_query": status_query,
            "recommendations": [
                "Use the official portal mentioned above to check real-time status",
                "Keep your application reference number handy",
                "Contact the helpline if status is not updated for long",
                "Visit local agriculture office for urgent queries",
            ],
            "note": "For real-time status, please use the official government portals mentioned in the information above.",
        }

    except Exception as e:
        logger.error(f"Error getting application status: {e}")
        return {
            "error": str(e),
            "application_id": application_id,
            "scheme_type": scheme_type,
            "recommendations": ["Please try again or contact support"],
        }
