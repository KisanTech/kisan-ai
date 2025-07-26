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
                    state=target_state,
                    date=date_str,
                    records=len(existing_data),
                )
                return {
                    FieldNames.SUCCESS: True,
                    FieldNames.DATA: existing_data,
                    FieldNames.SOURCE: "firestore",
                    FieldNames.STATE: target_state,
                    FieldNames.DATE: date_str,
                    FieldNames.TOTAL_RECORDS: len(existing_data),
                }

            # Data doesn't exist, fetch from Data.gov.in
            logger.info(
                "Data not found in Firestore, fetching from Data.gov.in",
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
                return {
                    FieldNames.SUCCESS: True,
                    FieldNames.DATA: fresh_data,
                    FieldNames.SOURCE: "data_gov_api",
                    FieldNames.STATE: target_state,
                    FieldNames.DATE: date_str,
                    FieldNames.TOTAL_RECORDS: len(fresh_data),
                }

            # No data available anywhere
            return {
                FieldNames.SUCCESS: False,
                FieldNames.DATA: [],
                FieldNames.SOURCE: "none",
                FieldNames.STATE: target_state,
                FieldNames.DATE: date_str,
                FieldNames.TOTAL_RECORDS: 0,
                FieldNames.ERROR: "No data available from any source",
            }

        except Exception as e:
            logger.error(
                "Failed to get market data", error=str(e), state=target_state, date=date_str
            )
            return {
                FieldNames.SUCCESS: False,
                FieldNames.DATA: [],
                FieldNames.SOURCE: "error",
                FieldNames.STATE: target_state,
                FieldNames.DATE: date_str,
                FieldNames.TOTAL_RECORDS: 0,
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

    async def _get_recent_data(
        self, state: str, limit: int = 100, offset: int = 0
    ) -> dict:
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


# Global market service instance
market_service = MarketService()
