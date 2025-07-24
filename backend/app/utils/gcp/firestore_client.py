"""
Firestore client for Project Kisan
Handles Firestore database connections and operations

Note: Typically accessed via GCPManager for singleton behavior.
Direct instantiation is possible for testing or special cases.
"""

from google.cloud import firestore
from google.cloud.firestore import Client

from app.core.config import settings
from app.utils.logger import logger


class FirestoreClient:
    """
    Dedicated Firestore client with connection management

    This class can be instantiated directly, but typically accessed
    via the global GCPManager for singleton behavior and resource efficiency.
    """

    def __init__(self):
        self._client: Client | None = None
        self._database_name = settings.FIRESTORE_DATABASE or "default"
        logger.debug("FirestoreClient instance created", database=self._database_name)

    @property
    def client(self) -> Client:
        """Get or create Firestore client (lazy initialization)"""
        if self._client is None:
            self._client = self._initialize_client()
        return self._client

    def _initialize_client(self) -> Client:
        """Initialize Firestore client with proper configuration"""
        try:
            if settings.GOOGLE_APPLICATION_CREDENTIALS:
                # Using service account credentials
                client = firestore.Client(
                    project=settings.GOOGLE_CLOUD_PROJECT, database=self._database_name
                )
                logger.info(
                    "Firestore client initialized with service account",
                    database=self._database_name,
                )
            else:
                # Using default application credentials
                client = firestore.Client(
                    project=settings.GOOGLE_CLOUD_PROJECT, database=self._database_name
                )
                logger.info(
                    "Firestore client initialized with default credentials",
                    database=self._database_name,
                )

            return client

        except Exception as e:
            logger.error("Failed to initialize Firestore client", error=str(e))
            raise

    def collection(self, collection_name: str):
        """Get a collection reference"""
        return self.client.collection(collection_name)

    def document(self, collection_name: str, document_id: str):
        """Get a document reference"""
        return self.client.collection(collection_name).document(document_id)

    def batch(self):
        """Create a new batch for batch operations"""
        return self.client.batch()

    def close(self):
        """Close the Firestore client"""
        if self._client:
            # Firestore client doesn't have explicit close method
            # But we can reset the reference
            self._client = None
            logger.info("Firestore client connection closed")
