"""
Format constants for consistent formatting across the application
"""


class DateFormats:
    """Date format constants"""

    # Standard ISO date format for API requests and storage
    ISO_DATE = "%Y-%m-%d"

    # ISO datetime format for timestamps
    ISO_DATETIME = "%Y-%m-%dT%H:%M:%S"

    # ISO datetime with timezone
    ISO_DATETIME_TZ = "%Y-%m-%dT%H:%M:%S%z"

    # Human readable formats
    DISPLAY_DATE = "%B %d, %Y"  # January 24, 2025
    DISPLAY_DATETIME = "%B %d, %Y at %I:%M %p"  # January 24, 2025 at 2:30 PM


class Separators:
    """Separator constants for document IDs and keys"""

    UNDERSCORE = "_"
    DASH = "-"
    SPACE = " "
    SLASH = "/"


class DocumentLimits:
    """Firestore and API limits"""

    FIRESTORE_BATCH_LIMIT = 500
    DATA_GOV_QUERY_LIMIT = 1000
    MARKET_DATA_TTL_DAYS = 30
    DATA_STALE_HOURS = 6


class FieldNames:
    """Standard field names for consistency"""

    # Core entity fields
    STATE = "state"
    DATE = "date"
    MARKET = "market"
    COMMODITY = "commodity"
    PRICE = "modal_price"

    # Metadata fields
    STORED_AT = "stored_at"
    LAST_UPDATED = "last_updated"
    UPDATED_BY = "updated_by"
    DATA_SOURCE = "data_source"
    TTL = "ttl"

    # Status fields
    SUCCESS = "success"
    ERROR = "error"
    MESSAGE = "message"

    # Response fields
    DATA = "data"
    SOURCE = "source"
    TOTAL_RECORDS = "total_records"
    OLD_PRICE = "old_price"
    NEW_PRICE = "new_price"
