"""
Google Cloud Translation Service for Kisan AI Backend.

This service provides text translation capabilities using Google Cloud Translation API v3.
Supports translation between multiple languages with automatic language detection.
"""

from typing import Any

import structlog
from google.api_core import exceptions as gcp_exceptions
from google.cloud import translate_v3 as translate

from app.core.config import settings

logger = structlog.get_logger("project-kisan.translation")


class TranslationService:
    """Google Cloud Translation service for text translation."""

    def __init__(self):
        """Initialize the Translation service."""
        self.project_id = settings.GOOGLE_CLOUD_PROJECT

        # Validate project ID
        if not self.project_id:
            logger.error(
                "Google Cloud project ID not configured. Please set GOOGLE_CLOUD_PROJECT in your environment.",
                help="Copy env.template to .env and set GOOGLE_CLOUD_PROJECT=your-project-id",
            )
            raise ValueError(
                "Google Cloud project ID is required for Translation service. "
                "Please set GOOGLE_CLOUD_PROJECT environment variable."
            )

        try:
            self.client = translate.TranslationServiceClient()
            self.location = "global"  # Use global location for translation
            self.parent = f"projects/{self.project_id}/locations/{self.location}"

            logger.info(
                "Translation service initialized successfully",
                project_id=self.project_id,
                location=self.location,
                parent=self.parent,
            )
        except Exception as e:
            logger.error(
                "Failed to initialize Translation service client",
                error=str(e),
                project_id=self.project_id,
                help="Ensure Google Cloud credentials are properly configured",
            )
            raise Exception(f"Translation service initialization failed: {str(e)}")

    async def translate_text(
        self, text: str, target_language: str, source_language: str | None = None
    ) -> dict[str, Any]:
        """
        Translate text from source language to target language.

        Args:
            text: Text to translate
            target_language: Target language code (e.g., 'en', 'hi', 'kn')
            source_language: Source language code. If None, auto-detect.

        Returns:
            Dict containing translated text and metadata
        """
        try:
            logger.info(
                "Starting text translation",
                text_length=len(text),
                source_language=source_language,
                target_language=target_language,
            )

            # Prepare the request
            request = {
                "parent": self.parent,
                "contents": [text],
                "target_language_code": target_language,
            }

            # Add source language if provided
            if source_language:
                request["source_language_code"] = source_language

            # Perform translation
            response = self.client.translate_text(request=request)

            # Extract results
            translation = response.translations[0]

            result = {
                "translated_text": translation.translated_text,
                "detected_language": translation.detected_language_code,
                "source_language": source_language or translation.detected_language_code,
                "target_language": target_language,
                "original_text": text,
            }

            logger.info(
                "Translation completed successfully",
                detected_language=result["detected_language"],
                target_language=target_language,
                translated_length=len(result["translated_text"]),
            )

            return result

        except gcp_exceptions.GoogleAPIError as e:
            logger.error(
                "Google Cloud Translation API error",
                error=str(e),
                error_code=e.code if hasattr(e, "code") else None,
            )
            raise Exception(f"Translation API error: {str(e)}")
        except Exception as e:
            logger.error(
                "Unexpected error during translation", error=str(e), error_type=type(e).__name__
            )
            raise Exception(f"Translation failed: {str(e)}")

    async def translate_batch(
        self, texts: list[str], target_language: str, source_language: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Translate multiple texts in a single batch request.

        Args:
            texts: List of texts to translate
            target_language: Target language code
            source_language: Source language code. If None, auto-detect.

        Returns:
            List of translation results
        """
        try:
            logger.info(
                "Starting batch translation",
                batch_size=len(texts),
                source_language=source_language,
                target_language=target_language,
            )

            # Prepare the request
            request = {
                "parent": self.parent,
                "contents": texts,
                "target_language_code": target_language,
            }

            # Add source language if provided
            if source_language:
                request["source_language_code"] = source_language

            # Perform batch translation
            response = self.client.translate_text(request=request)

            # Extract results
            results = []
            for i, translation in enumerate(response.translations):
                result = {
                    "translated_text": translation.translated_text,
                    "detected_language": translation.detected_language_code,
                    "source_language": source_language or translation.detected_language_code,
                    "target_language": target_language,
                    "original_text": texts[i],
                }
                results.append(result)

            logger.info(
                "Batch translation completed successfully",
                batch_size=len(results),
                target_language=target_language,
            )

            return results

        except gcp_exceptions.GoogleAPIError as e:
            logger.error(
                "Google Cloud Translation API error in batch",
                error=str(e),
                error_code=e.code if hasattr(e, "code") else None,
                batch_size=len(texts),
            )
            raise Exception(f"Batch translation API error: {str(e)}")
        except Exception as e:
            logger.error(
                "Unexpected error during batch translation",
                error=str(e),
                error_type=type(e).__name__,
                batch_size=len(texts),
            )
            raise Exception(f"Batch translation failed: {str(e)}")

    async def detect_language(self, text: str) -> dict[str, Any]:
        """
        Detect the language of the given text.

        Args:
            text: Text to analyze

        Returns:
            Dict containing detected language and confidence
        """
        try:
            logger.info("Starting language detection", text_length=len(text))

            # Prepare the request
            request = {
                "parent": self.parent,
                "content": text,
            }

            # Perform language detection
            response = self.client.detect_language(request=request)

            # Extract the most confident detection
            if response.languages:
                detection = response.languages[0]
                result = {
                    "language_code": detection.language_code,
                    "confidence": detection.confidence,
                    "text": text,
                }

                logger.info(
                    "Language detection completed",
                    detected_language=result["language_code"],
                    confidence=result["confidence"],
                )

                return result
            else:
                logger.warning("No language detected")
                return {"language_code": "unknown", "confidence": 0.0, "text": text}

        except gcp_exceptions.GoogleAPIError as e:
            logger.error(
                "Google Cloud Language Detection API error",
                error=str(e),
                error_code=e.code if hasattr(e, "code") else None,
            )
            raise Exception(f"Language detection API error: {str(e)}")
        except Exception as e:
            logger.error(
                "Unexpected error during language detection",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise Exception(f"Language detection failed: {str(e)}")

    async def get_supported_languages(
        self, target_language_code: str = "en"
    ) -> list[dict[str, str]]:
        """
        Get list of supported languages.

        Args:
            target_language_code: Language code for language names (default: 'en')

        Returns:
            List of supported languages with codes and names
        """
        try:
            logger.info("Fetching supported languages", target_language_code=target_language_code)

            # Prepare the request
            request = {
                "parent": self.parent,
                "display_language_code": target_language_code,
            }

            # Get supported languages
            response = self.client.get_supported_languages(request=request)

            # Extract language information
            languages = []
            for language in response.languages:
                languages.append(
                    {
                        "language_code": language.language_code,
                        "display_name": language.display_name,
                        "support_source": language.support_source,
                        "support_target": language.support_target,
                    }
                )

            logger.info(
                "Supported languages fetched successfully",
                total_languages=len(languages),
                target_language_code=target_language_code,
            )

            return languages

        except gcp_exceptions.GoogleAPIError as e:
            logger.error(
                "Google Cloud Get Supported Languages API error",
                error=str(e),
                error_code=e.code if hasattr(e, "code") else None,
            )
            raise Exception(f"Get supported languages API error: {str(e)}")
        except Exception as e:
            logger.error(
                "Unexpected error fetching supported languages",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise Exception(f"Failed to fetch supported languages: {str(e)}")


# Global instance
translation_service = TranslationService()
