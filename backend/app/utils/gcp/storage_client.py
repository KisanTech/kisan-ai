"""
Cloud Storage client for Project Kisan
Handles Cloud Storage bucket connections and operations

Note: Typically accessed via GCPManager for singleton behavior.
Direct instantiation is possible for testing or special cases.
"""

from google.cloud import storage
from google.cloud.storage import (
    Bucket,
    Client as StorageClient,
)

from app.core.config import settings
from app.utils.logger import logger


class CloudStorageClient:
    """
    Dedicated Cloud Storage client with bucket management

    This class can be instantiated directly, but typically accessed
    via the global GCPManager for singleton behavior and resource efficiency.
    """

    def __init__(self):
        self._client: StorageClient | None = None
        self._bucket: Bucket | None = None
        self._bucket_name = settings.CLOUD_STORAGE_BUCKET
        logger.debug("CloudStorageClient instance created", bucket=self._bucket_name)

    @property
    def client(self) -> StorageClient:
        """Get or create Storage client"""
        if self._client is None:
            self._client = self._initialize_client()
        return self._client

    @property
    def bucket(self) -> Bucket:
        """Get or create bucket reference"""
        if self._bucket is None:
            if not self._bucket_name:
                raise ValueError("Cloud Storage bucket name not configured")
            self._bucket = self.client.bucket(self._bucket_name)
        return self._bucket

    def _initialize_client(self) -> StorageClient:
        """Initialize Cloud Storage client with proper configuration"""
        try:
            if settings.GOOGLE_APPLICATION_CREDENTIALS:
                # Using service account credentials
                client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
                logger.info(
                    "Cloud Storage client initialized with service account",
                    project=settings.GOOGLE_CLOUD_PROJECT,
                )
            else:
                # Using default application credentials
                client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
                logger.info(
                    "Cloud Storage client initialized with default credentials",
                    project=settings.GOOGLE_CLOUD_PROJECT,
                )

            return client

        except Exception as e:
            logger.error("Failed to initialize Cloud Storage client", error=str(e))
            raise

    def get_blob(self, blob_name: str):
        """Get a blob reference"""
        return self.bucket.blob(blob_name)

    def upload_blob(self, source_data: bytes, destination_blob_name: str, content_type: str = None):
        """Upload data to a blob"""
        try:
            blob = self.bucket.blob(destination_blob_name)
            # Set content type properly before upload
            if content_type:
                blob.content_type = content_type
            # Upload the data
            blob.upload_from_string(source_data, content_type=content_type)
            logger.info("Uploaded blob", blob_name=destination_blob_name, bucket=self._bucket_name)
            return blob
        except Exception as e:
            logger.error("Failed to upload blob", error=str(e), blob_name=destination_blob_name)
            raise

    def download_blob(self, blob_name: str) -> bytes:
        """Download data from a blob"""
        try:
            blob = self.bucket.blob(blob_name)
            data = blob.download_as_bytes()
            logger.info("Downloaded blob", blob_name=blob_name, bucket=self._bucket_name)
            return data
        except Exception as e:
            logger.error("Failed to download blob", error=str(e), blob_name=blob_name)
            raise

    def delete_blob(self, blob_name: str):
        """Delete a blob"""
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            logger.info("Deleted blob", blob_name=blob_name, bucket=self._bucket_name)
        except Exception as e:
            logger.error("Failed to delete blob", error=str(e), blob_name=blob_name)
            raise

    def list_blobs(self, prefix: str = None) -> list:
        """List blobs in the bucket"""
        try:
            blobs = list(self.client.list_blobs(self.bucket, prefix=prefix))
            logger.info("Listed blobs", count=len(blobs), bucket=self._bucket_name, prefix=prefix)
            return blobs
        except Exception as e:
            logger.error("Failed to list blobs", error=str(e), bucket=self._bucket_name)
            raise

    def close(self):
        """Close the Cloud Storage client"""
        if self._client:
            # Cloud Storage client doesn't have explicit close method
            # But we can reset the references
            self._client = None
            self._bucket = None
            logger.info("Cloud Storage client connection closed")
