"""
HTTP client for external API calls
"""

from typing import Any

import aiohttp

from app.constants import HTTPMethod
from app.utils.logger import logger


async def api_request(
    url: str,
    method: HTTPMethod | str = HTTPMethod.GET,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    json_data: dict[str, Any] | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    """
    Make HTTP request with proper error handling and logging

    Args:
        url: Target URL
        method: HTTP method (enum or string)
        headers: Optional headers
        params: Query parameters
        json_data: JSON body data
        timeout: Request timeout in seconds

    Returns:
        JSON response data

    Raises:
        aiohttp.ClientError: For HTTP-related errors
        ValueError: For invalid responses
    """

    # Default headers
    request_headers = {"User-Agent": "ProjectKisan-AI/1.0", "Accept": "application/json"}

    # Merge custom headers
    if headers:
        request_headers.update(headers)

    # Convert enum to string if needed
    http_method = method.value if isinstance(method, HTTPMethod) else str(method).upper()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=http_method,
                url=url,
                headers=request_headers,
                params=params,
                json=json_data,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as response:
                # Log response status for debugging
                logger.debug("HTTP response", method=http_method, url=url, status=response.status)

                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    raise ValueError(f"Resource not found: {url}")
                elif response.status == 401:
                    raise ValueError("Authentication failed - check API key")
                elif response.status == 429:
                    raise ValueError("API rate limit exceeded")
                elif response.status >= 500:
                    raise ValueError(f"Server error: {response.status}")
                else:
                    response.raise_for_status()

    except aiohttp.ClientTimeout:
        logger.error("Request timeout", url=url, timeout=timeout)
        raise ValueError(f"Request timeout after {timeout} seconds")
    except aiohttp.ClientError as e:
        logger.error("HTTP client error", error=str(e), url=url)
        raise
    except Exception as e:
        logger.error("Unexpected error in HTTP request", error=str(e), url=url)
        raise
