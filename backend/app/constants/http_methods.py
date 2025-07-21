"""
HTTP Methods enum for type-safe API calls
"""

from enum import Enum


class HTTPMethod(Enum):
    """HTTP method constants"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
