"""
GCP Manager - coordinates all Google Cloud Platform services
Provides unified access to Firestore and Cloud Storage
"""

from app.utils.gcp.firestore_client import FirestoreClient
from app.utils.gcp.storage_client import CloudStorageClient
from app.utils.logger import logger


class GCPManager:
    """
    Unified manager for all GCP services

    Provides singleton access to Firestore and Cloud Storage clients.
    """

    def __init__(self):
        self._firestore_client: FirestoreClient | None = None
        self._storage_client: CloudStorageClient | None = None
        self._initialized = False

    @property
    def firestore(self) -> FirestoreClient:
        """Get Firestore client (singleton)"""
        if self._firestore_client is None:
            self._firestore_client = FirestoreClient()
        return self._firestore_client

    @property
    def storage(self) -> CloudStorageClient:
        """Get Cloud Storage client (singleton)"""
        if self._storage_client is None:
            self._storage_client = CloudStorageClient()
        return self._storage_client

    async def initialize(self) -> None:
        """
        Initialize all GCP services

        Args:
            test_connections: Whether to test connections during initialization
        """
        if self._initialized:
            logger.info("GCP services already initialized")
            return

        try:
            logger.info("Initializing Google Cloud Platform services")

            # Initialize clients (lazy loading will happen on first access)
            # This just ensures the manager is ready
            _ = self.firestore
            _ = self.storage

            self._initialized = True
            logger.info("GCP services initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize GCP services", error=str(e))
            raise

    def close(self) -> None:
        """Close all GCP service connections"""
        try:
            if self._firestore_client:
                self._firestore_client.close()

            if self._storage_client:
                self._storage_client.close()

            self._initialized = False
            logger.info("All GCP service connections closed")

        except Exception as e:
            logger.error("Error closing GCP connections", error=str(e))


# Global GCP manager instance (singleton pattern)
gcp_manager = GCPManager()
