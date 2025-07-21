"""
API client for Data.gov.in market data
Production-ready with proper error handling
"""

from typing import Any

from app.constants import APIEndpoints
from app.core.config import settings
from app.utils.http_client import api_request
from app.utils.logger import logger


async def data_gov_request(
    resource_id: str, params: dict[str, Any] | None = None, timeout: int = 30
) -> dict[str, Any]:
    """
    Make request to Data.gov.in API with proper error handling

    Args:
        resource_id: The resource ID for the Data.gov.in dataset
        params: Query parameters (API key will be added automatically)
        timeout: Request timeout in seconds

    Returns:
        API response data

    Raises:
        Exception: When API call fails or returns non-200 status
    """

    if not settings.DATA_GOV_API_KEY:
        raise ValueError("DATA_GOV_API_KEY not configured")

    # Build full URL
    url = f"{APIEndpoints.DATA_GOV_BASE}/{resource_id}"

    # Prepare parameters
    request_params = params or {}
    request_params["api-key"] = settings.DATA_GOV_API_KEY

    try:
        logger.info(
            "Making Data.gov.in API request",
            resource_id=resource_id,
            params_count=len(request_params),
        )

        response = await api_request(url=url, params=request_params, timeout=timeout)

        logger.info("Data.gov.in API request successful", resource_id=resource_id)
        return response

    except Exception as e:
        logger.error("Data.gov.in API request failed", error=str(e), resource_id=resource_id)
        raise
