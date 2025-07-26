"""
Market Data Service
Handles data storage, retrieval, and price updates
"""

from datetime import (
    date as date_type,
    datetime,
    timedelta,
)

from app.constants import (
    APIEndpoints,
    DateFormats,
    DocumentLimits,
    FieldNames,
    MarketData,
    Separators,
)
from app.utils.api_client import data_gov_request
from app.utils.gcp.gcp_manager import gcp_manager
from app.utils.logger import log_latency, logger


class MarketService:
    def __init__(self):
        self.daily_prices_collection = "daily_market_prices"

    @log_latency("get_market_data")
    async def get_market_data(
        self, state: str, date: date_type | None = None, limit: int = 100, offset: int = 0
    ) -> dict:
        """
        Get market data for a specific state and date with pagination
        If no date provided, returns most recent available data from Firestore
        Fetches from Data.gov.in if not available in Firestore
        """
        target_state = state or MarketData.DEFAULT_STATE

        # If no date provided, get most recent available data
        if date is None:
            return await self._get_recent_data(target_state, limit, offset)

        target_date = date
        date_str = target_date.strftime(DateFormats.ISO_DATE)

        try:
            # Check if data exists in Firestore with pagination
            existing_data = await self._get_stored_data(target_state, date_str, limit, offset)

            if existing_data:
                logger.info(
                    "Retrieved market data from Firestore",
                    count=len(existing_data),
                    state=target_state,
                    date=date_str,
                    limit=limit,
                    offset=offset,
                )
                return {
                    FieldNames.SUCCESS: True,
                    FieldNames.DATA: existing_data,
                    FieldNames.SOURCE: "Firestore",
                    FieldNames.STATE: target_state,
                    FieldNames.DATE: date_str,
                    FieldNames.TOTAL_RECORDS: len(existing_data),
                }

            # If no data in Firestore, fetch from Data.gov.in API (only for current/recent dates)
            logger.info(
                "No data found in Firestore, fetching from Data.gov.in",
                state=target_state,
                date=date_str,
            )

            fresh_data = await self._fetch_from_data_gov(target_state)
            if fresh_data:
                await self._store_data(target_state, date_str, fresh_data)
                logger.info(
                    "Fetched and stored fresh market data",
                    state=target_state,
                    date=date_str,
                    records=len(fresh_data),
                )
                # Apply pagination to fetched data
                paginated_data = fresh_data[offset : offset + limit]
                return {
                    FieldNames.SUCCESS: True,
                    FieldNames.DATA: paginated_data,
                    FieldNames.SOURCE: "Data.gov.in",
                    FieldNames.STATE: target_state,
                    FieldNames.DATE: date_str,
                    FieldNames.TOTAL_RECORDS: len(paginated_data),
                }

            return {
                FieldNames.SUCCESS: True,
                FieldNames.DATA: [],
                FieldNames.SOURCE: "None",
                FieldNames.STATE: target_state,
                FieldNames.DATE: date_str,
                FieldNames.TOTAL_RECORDS: 0,
            }

        except Exception as e:
            logger.error(
                "Failed to get market data", error=str(e), state=target_state, date=date_str
            )
            return {
                FieldNames.SUCCESS: False,
                FieldNames.DATA: [],
                FieldNames.SOURCE: "Error",
                FieldNames.STATE: target_state,
                FieldNames.DATE: date_str,
                FieldNames.TOTAL_RECORDS: 0,
                FieldNames.ERROR: str(e),
            }

    @log_latency("get_filtered_market_data")
    async def get_filtered_market_data(
        self,
        state: str,
        commodity: str | None = None,
        market: str | None = None,
        start_date: date_type | None = None,
        end_date: date_type | None = None,
        limit: int = 1000,
    ) -> dict:
        """
        Get filtered market data for Market Agent V3

        Args:
            state: State name (required)
            commodity: Commodity/crop name (optional)
            market: Market name (optional)
            start_date: Start date for range (optional)
            end_date: End date for range (optional)
            limit: Maximum records to return

        Returns:
            Filtered market data matching the criteria
        """
        try:
            # Set default date range if not provided (last 60 days for Agent V3)
            if start_date is None and end_date is None:
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=60)
            elif start_date is None:
                start_date = end_date - timedelta(days=60)
            elif end_date is None:
                end_date = datetime.now().date()

            # Build filters dict for logging
            filters_applied = {
                "state": state,
                "commodity": commodity,
                "market": market,
                "start_date": start_date.strftime(DateFormats.ISO_DATE) if start_date else None,
                "end_date": end_date.strftime(DateFormats.ISO_DATE) if end_date else None,
                "limit": limit,
            }

            logger.info("Fetching filtered market data", **filters_applied)

            # Get Firestore collection reference
            collection_ref = gcp_manager.firestore.collection(self.daily_prices_collection)

            # Start building the query
            query = collection_ref

            # Filter by state (required)
            query = query.where(FieldNames.STATE, "==", state)

            # Note: Commodity filtering is done in post-processing for case-insensitive matching

            # Note: Market filtering is done in post-processing for case-insensitive matching

            # Filter by date range
            if start_date:
                start_date_str = start_date.strftime(DateFormats.ISO_DATE)
                query = query.where(FieldNames.DATE, ">=", start_date_str)

            if end_date:
                end_date_str = end_date.strftime(DateFormats.ISO_DATE)
                query = query.where(FieldNames.DATE, "<=", end_date_str)

            # Order by date (most recent first) and limit results
            query = query.order_by(FieldNames.DATE, direction="DESCENDING")
            query = query.limit(limit)

            # Execute query
            docs = query.stream()

            # Process results
            filtered_data = []
            for doc in docs:
                doc_data = doc.to_dict()

                # Additional filtering for partial matches (since Firestore has limited string matching)
                if (
                    commodity
                    and commodity.lower() not in doc_data.get(FieldNames.COMMODITY, "").lower()
                ):
                    continue

                if market and market.lower() not in doc_data.get(FieldNames.MARKET, "").lower():
                    continue

                filtered_data.append(doc_data)

            # Sort by date again to ensure consistency (descending - most recent first)
            filtered_data.sort(key=lambda x: x.get(FieldNames.DATE, ""), reverse=True)

            logger.info(
                "Successfully retrieved filtered market data",
                total_records=len(filtered_data),
                **filters_applied,
            )

            return {
                FieldNames.SUCCESS: True,
                FieldNames.DATA: filtered_data,
                FieldNames.TOTAL_RECORDS: len(filtered_data),
                "filters_applied": filters_applied,
                "date_range": {
                    "start_date": start_date.strftime(DateFormats.ISO_DATE) if start_date else None,
                    "end_date": end_date.strftime(DateFormats.ISO_DATE) if end_date else None,
                    "days": (end_date - start_date).days if start_date and end_date else None,
                },
            }

        except Exception as e:
            logger.error(
                "Failed to get filtered market data",
                error=str(e),
                state=state,
                commodity=commodity,
                market=market,
                start_date=start_date,
                end_date=end_date,
            )
            return {
                FieldNames.SUCCESS: False,
                FieldNames.DATA: [],
                FieldNames.TOTAL_RECORDS: 0,
                "filters_applied": filters_applied if "filters_applied" in locals() else {},
                FieldNames.ERROR: str(e),
            }

    async def update_crop_price(
        self,
        state: str,
        market: str,
        commodity: str,
        date: date_type,
        price: float,
        updated_by: str = "api",
    ) -> dict:
        """
        Update price for a specific crop - direct document access
        Natural key: state + date + market + crop = unique document
        """
        date_str = date.strftime(DateFormats.ISO_DATE)

        try:
            # Create direct document ID using natural key
            doc_id = self._create_document_id(state, date_str, market, commodity)
            doc_ref = gcp_manager.firestore.document(self.daily_prices_collection, doc_id)

            # Get the existing document
            doc = doc_ref.get()

            if doc.exists:
                # Update existing record
                doc_data = doc.to_dict()
                old_price = doc_data.get(FieldNames.PRICE, 0)

                # Update the price and metadata
                doc_ref.update(
                    {
                        FieldNames.PRICE: price,
                        FieldNames.LAST_UPDATED: datetime.now(),
                        FieldNames.UPDATED_BY: updated_by,
                    }
                )

                logger.info(
                    "Updated crop price",
                    state=state,
                    market=market,
                    commodity=commodity,
                    old_price=old_price,
                    new_price=price,
                    date=date_str,
                )

                return {
                    FieldNames.SUCCESS: True,
                    FieldNames.MESSAGE: f"Updated {commodity} price in {market}",
                    FieldNames.OLD_PRICE: old_price,
                    FieldNames.NEW_PRICE: price,
                    FieldNames.STATE: state,
                    FieldNames.MARKET: market,
                    FieldNames.COMMODITY: commodity,
                    FieldNames.DATE: date_str,
                }
            else:
                return {
                    FieldNames.SUCCESS: False,
                    FieldNames.MESSAGE: (
                        f"No record found for {commodity} in {market}, {state} on {date_str}"
                    ),
                    FieldNames.STATE: state,
                    FieldNames.MARKET: market,
                    FieldNames.COMMODITY: commodity,
                    FieldNames.DATE: date_str,
                }

        except Exception as e:
            logger.error(
                "Failed to update crop price",
                error=str(e),
                state=state,
                market=market,
                commodity=commodity,
                date=date_str,
            )
            return {
                FieldNames.SUCCESS: False,
                FieldNames.MESSAGE: f"Failed to update price: {str(e)}",
                FieldNames.STATE: state,
                FieldNames.MARKET: market,
                FieldNames.COMMODITY: commodity,
                FieldNames.DATE: date_str,
                FieldNames.ERROR: str(e),
            }

    async def _get_recent_data(self, state: str, limit: int = 100, offset: int = 0) -> dict:
        """Get most recent available data for a state (all dates)"""
        try:
            # Simple query - get all data for this state, then sort in Python
            # This avoids needing a composite index
            query = (
                gcp_manager.firestore.collection(self.daily_prices_collection)
                .where(FieldNames.STATE, "==", state)
                .limit(limit * 3)  # Get more records to find recent ones
            )

            docs = query.stream()

            # Collect all data and sort by date in Python
            all_records = []
            for doc in docs:
                doc_data = doc.to_dict()
                if doc_data and FieldNames.DATE in doc_data:
                    all_records.append(doc_data)

            # Sort by date descending in Python
            all_records.sort(key=lambda x: x.get(FieldNames.DATE, ""), reverse=True)

            # Apply limit and offset after sorting
            start_idx = offset
            end_idx = offset + limit
            all_data = all_records[start_idx:end_idx]

            latest_date = all_records[0].get(FieldNames.DATE, "unknown") if all_records else None

            if all_data:
                logger.info(
                    "Retrieved recent market data from Firestore",
                    state=state,
                    latest_date=latest_date,
                    records=len(all_data),
                )
                return {
                    FieldNames.SUCCESS: True,
                    FieldNames.DATA: all_data,
                    FieldNames.SOURCE: "firestore",
                    FieldNames.STATE: state,
                    FieldNames.DATE: latest_date or "recent",
                    FieldNames.TOTAL_RECORDS: len(all_data),
                }
            else:
                # No data in Firestore, try fetching fresh data
                logger.info(
                    "No recent data found in Firestore, fetching from Data.gov.in",
                    state=state,
                )
                fresh_data = await self._fetch_from_data_gov(state)
                if fresh_data:
                    # Store the fresh data with current date
                    current_date = datetime.now().date()
                    date_str = current_date.strftime(DateFormats.ISO_DATE)
                    await self._store_data(state, date_str, fresh_data)

                    return {
                        FieldNames.SUCCESS: True,
                        FieldNames.DATA: fresh_data[:limit],  # Apply limit
                        FieldNames.SOURCE: "data_gov_api",
                        FieldNames.STATE: state,
                        FieldNames.DATE: date_str,
                        FieldNames.TOTAL_RECORDS: len(fresh_data[:limit]),
                    }
                else:
                    return {
                        FieldNames.SUCCESS: False,
                        FieldNames.DATA: [],
                        FieldNames.SOURCE: "none",
                        FieldNames.STATE: state,
                        FieldNames.DATE: "recent",
                        FieldNames.TOTAL_RECORDS: 0,
                        FieldNames.ERROR: "No recent data available from any source",
                    }

        except Exception as e:
            logger.error(
                "Failed to get recent data",
                error=str(e),
                state=state,
                limit=limit,
                offset=offset,
            )
            return {
                FieldNames.SUCCESS: False,
                FieldNames.DATA: [],
                FieldNames.SOURCE: "error",
                FieldNames.STATE: state,
                FieldNames.DATE: "recent",
                FieldNames.TOTAL_RECORDS: 0,
                FieldNames.ERROR: str(e),
            }

    async def _get_stored_data(
        self, state: str, date_str: str, limit: int = 100, offset: int = 0
    ) -> list[dict]:
        """Get crop records for a specific state and date with pagination"""
        try:
            # Query with pagination
            query = (
                gcp_manager.firestore.collection(self.daily_prices_collection)
                .where(FieldNames.STATE, "==", state)
                .where(FieldNames.DATE, "==", date_str)
                .order_by(FieldNames.COMMODITY)  # Consistent ordering for pagination
                .limit(limit)
                .offset(offset)
            )

            docs = query.stream()

            all_data = []
            for doc in docs:
                doc_data = doc.to_dict()
                if doc_data:
                    all_data.append(doc_data)

            return all_data

        except Exception as e:
            logger.error(
                "Failed to get stored data",
                error=str(e),
                state=state,
                date=date_str,
                limit=limit,
                offset=offset,
            )
            return []

    async def _fetch_from_data_gov(self, state: str) -> list[dict]:
        """Fetch fresh data from Data.gov.in API"""
        try:
            market_data = await data_gov_request(
                resource_id=APIEndpoints.DATA_GOV_MANDI_RESOURCE_ID,
                params={
                    f"filters[{FieldNames.STATE}]": state,
                    "format": "json",
                    "limit": DocumentLimits.DATA_GOV_QUERY_LIMIT,
                },
            )

            if not market_data or "records" not in market_data:
                logger.warning("No market data found", state=state)
                return []

            # Clean and return the data
            all_prices = []
            for record in market_data["records"]:
                record[FieldNames.STATE] = state
                all_prices.append(record)

            return all_prices

        except Exception as e:
            logger.error("Failed to fetch from Data.gov.in", error=str(e), state=state)
            return []

    async def _store_data(self, state: str, date_str: str, data: list[dict]) -> None:
        """
        Store each crop as a separate document
        Document ID: state_date_market_crop
        One document = One crop price record
        """
        try:
            batch = gcp_manager.firestore.batch()

            # Calculate TTL (30 days from now)
            ttl_time = datetime.now() + timedelta(days=DocumentLimits.MARKET_DATA_TTL_DAYS)

            for record in data:
                # Create unique document ID using natural key
                commodity = record.get(FieldNames.COMMODITY, "unknown")
                market = record.get(FieldNames.MARKET, "unknown")

                # Create document ID and reference
                doc_id = self._create_document_id(state, date_str, market, commodity)
                doc_ref = gcp_manager.firestore.document(self.daily_prices_collection, doc_id)

                # Store individual crop record with metadata
                document_data = {
                    **record,  # All original data from Data.gov.in
                    FieldNames.STATE: state,
                    FieldNames.DATE: date_str,
                    FieldNames.MARKET: market,
                    FieldNames.COMMODITY: commodity,
                    FieldNames.STORED_AT: datetime.now(),
                    FieldNames.TTL: ttl_time,  # Firestore TTL field
                    FieldNames.DATA_SOURCE: "Data.gov.in",
                }

                batch.set(doc_ref, document_data)

            # Commit all crop records
            batch.commit()

            logger.info(
                "Data stored in Firestore with TTL", state=state, date=date_str, records=len(data)
            )

        except Exception as e:
            logger.error("Failed to store data", error=str(e), state=state, date=date_str)
            raise

    def _create_document_id(self, state: str, date_str: str, market: str, commodity: str) -> str:
        """
        Create a consistent document ID using natural key
        Format: state_date_market_commodity
        """
        # Clean names for document ID (replace special characters)
        clean_market = market.replace(Separators.SLASH, Separators.UNDERSCORE).replace(
            Separators.SPACE, Separators.UNDERSCORE
        )
        clean_commodity = commodity.replace(Separators.SLASH, Separators.UNDERSCORE).replace(
            Separators.SPACE, Separators.UNDERSCORE
        )

        return (
            f"{state}{Separators.UNDERSCORE}{date_str}{Separators.UNDERSCORE}"
            f"{clean_market}{Separators.UNDERSCORE}{clean_commodity}"
        )

    @log_latency("get_bulk_market_data")
    async def get_bulk_market_data(
        self,
        date: date_type | None = None,
        states: list[str] | None = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> dict:
        """
        Get market data for multiple states or all states for a specific date.

        This method is optimized for bulk data loading and cache initialization.
        Returns data organized by state for easy processing.

        Args:
            date: Target date (defaults to today if None)
            states: List of state names (defaults to all available states if None)
            limit: Maximum records to return per query
            offset: Number of records to skip

        Returns:
            dict: {
                "success": bool,
                "data": {
                    "state_name": [records...],
                    "state_name": [records...],
                    ...
                },
                "total_records": int,
                "states_included": [state_names],
                "date": str,
                "source": str
            }
        """
        if date is None:
            date = datetime.now().date()

        date_str = date.strftime(DateFormats.ISO_DATE)

        # Define target states
        if states is None:
            # Default to our main states if none specified
            target_states = ["Karnataka", "Tamil Nadu", "Punjab"]
        else:
            target_states = states

        logger.info(
            "Getting bulk market data",
            date=date_str,
            states=target_states,
            limit=limit,
            offset=offset,
        )

        try:
            result_data = {}
            total_records = 0

            # Get data for each state
            for state in target_states:
                try:
                    # Get data for this state using existing method
                    state_result = await self.get_market_data(
                        state=state, date=date, limit=limit, offset=offset
                    )

                    if state_result.get(FieldNames.SUCCESS, False):
                        state_data = state_result.get(FieldNames.DATA, [])
                        result_data[state] = state_data
                        total_records += len(state_data)
                    else:
                        # State had no data or error - include empty list
                        result_data[state] = []

                except Exception as e:
                    logger.error(f"Error getting data for {state}", error=str(e))
                    result_data[state] = []

            logger.info(
                "Bulk market data retrieved successfully",
                total_records=total_records,
                states_count=len(target_states),
                date=date_str,
            )

            return {
                FieldNames.SUCCESS: True,
                FieldNames.DATA: result_data,
                FieldNames.TOTAL_RECORDS: total_records,
                "states_included": target_states,
                FieldNames.DATE: date_str,
                FieldNames.SOURCE: "bulk_firestore",
            }

        except Exception as e:
            logger.error(
                "Failed to get bulk market data", error=str(e), date=date_str, states=target_states
            )
            return {
                FieldNames.SUCCESS: False,
                "error": f"Failed to get bulk market data: {str(e)}",
                FieldNames.DATA: {},
                FieldNames.TOTAL_RECORDS: 0,
                "states_included": [],
                FieldNames.DATE: date_str,
                FieldNames.SOURCE: "error",
            }


# Global market service instance
market_service = MarketService()
