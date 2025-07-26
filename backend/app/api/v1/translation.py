"""
Google Cloud Translation API endpoints for Kisan AI Backend.

This module provides REST API endpoints for text translation, language detection,
and supported languages using Google Cloud Translation API v3.
"""


import structlog
from fastapi import APIRouter, HTTPException, status

from app.models.translation import (
    BatchTranslationRequest,
    BatchTranslationResponse,
    LanguageDetectionRequest,
    LanguageDetectionResponse,
    SupportedLanguage,
    SupportedLanguagesResponse as TranslationSupportedLanguagesResponse,
    TranslationRequest,
    TranslationResponse,
)
from app.services.translation_service import translation_service

logger = structlog.get_logger("project-kisan.api.translation")

router = APIRouter()


@router.post(
    "/translate",
    response_model=TranslationResponse,
    summary="Translate text",
    description="Translate text from source language to target language using Google Cloud Translation API",
    response_description="Translation result with detected language information",
)
async def translate_text(request: TranslationRequest) -> TranslationResponse:
    """
    Translate text from source language to target language.

    - **text**: Text to translate (max 30,000 characters)
    - **target_language**: Target language code (e.g., 'en', 'hi', 'kn')
    - **source_language**: Source language code (optional, auto-detect if not provided)
    """
    try:
        logger.info(
            "Translation request received",
            text_length=len(request.text),
            source_language=request.source_language,
            target_language=request.target_language,
        )

        # Perform translation
        result = await translation_service.translate_text(
            text=request.text,
            target_language=request.target_language,
            source_language=request.source_language,
        )

        # Convert to response model
        response = TranslationResponse(**result)

        logger.info(
            "Translation completed successfully",
            detected_language=response.detected_language,
            target_language=response.target_language,
        )

        return response

    except Exception as e:
        logger.error(
            "Translation failed",
            error=str(e),
            error_type=type(e).__name__,
            source_language=request.source_language,
            target_language=request.target_language,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}",
        )


@router.post(
    "/translate/batch",
    response_model=BatchTranslationResponse,
    summary="Translate multiple texts",
    description="Translate multiple texts in a single batch request for better performance",
    response_description="Batch translation results",
)
async def translate_batch(request: BatchTranslationRequest) -> BatchTranslationResponse:
    """
    Translate multiple texts in a single batch request.

    - **texts**: List of texts to translate (max 100 items, each max 30,000 characters)
    - **target_language**: Target language code
    - **source_language**: Source language code (optional, auto-detect if not provided)
    """
    try:
        logger.info(
            "Batch translation request received",
            batch_size=len(request.texts),
            source_language=request.source_language,
            target_language=request.target_language,
        )

        # Perform batch translation
        results = await translation_service.translate_batch(
            texts=request.texts,
            target_language=request.target_language,
            source_language=request.source_language,
        )

        # Convert to response models
        translations = [TranslationResponse(**result) for result in results]

        response = BatchTranslationResponse(
            translations=translations, total_count=len(translations)
        )

        logger.info(
            "Batch translation completed successfully",
            batch_size=len(translations),
            target_language=request.target_language,
        )

        return response

    except Exception as e:
        logger.error(
            "Batch translation failed",
            error=str(e),
            error_type=type(e).__name__,
            batch_size=len(request.texts),
            source_language=request.source_language,
            target_language=request.target_language,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch translation failed: {str(e)}",
        )


@router.post(
    "/detect-language",
    response_model=LanguageDetectionResponse,
    summary="Detect text language",
    description="Detect the language of the provided text using Google Cloud Translation API",
    response_description="Detected language with confidence score",
)
async def detect_language(request: LanguageDetectionRequest) -> LanguageDetectionResponse:
    """
    Detect the language of the provided text.

    - **text**: Text to analyze for language detection (max 30,000 characters)
    """
    try:
        logger.info("Language detection request received", text_length=len(request.text))

        # Perform language detection
        result = await translation_service.detect_language(text=request.text)

        # Convert to response model
        response = LanguageDetectionResponse(**result)

        logger.info(
            "Language detection completed successfully",
            detected_language=response.language_code,
            confidence=response.confidence,
        )

        return response

    except Exception as e:
        logger.error("Language detection failed", error=str(e), error_type=type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Language detection failed: {str(e)}",
        )


@router.get(
    "/languages",
    response_model=TranslationSupportedLanguagesResponse,
    summary="Get supported languages",
    description="Get list of all languages supported by Google Cloud Translation API",
    response_description="List of supported languages with their capabilities",
)
async def get_supported_languages(
    display_language: str = "en",
) -> TranslationSupportedLanguagesResponse:
    """
    Get list of supported languages for translation.

    - **display_language**: Language code for displaying language names (default: 'en')
    """
    try:
        logger.info("Supported languages request received", display_language=display_language)

        # Get supported languages
        languages_data = await translation_service.get_supported_languages(
            target_language_code=display_language
        )

        # Convert to response models
        languages = [SupportedLanguage(**lang) for lang in languages_data]

        response = TranslationSupportedLanguagesResponse(
            languages=languages, total_count=len(languages), display_language_code=display_language
        )

        logger.info(
            "Supported languages fetched successfully",
            total_languages=len(languages),
            display_language=display_language,
        )

        return response

    except Exception as e:
        logger.error(
            "Failed to fetch supported languages",
            error=str(e),
            error_type=type(e).__name__,
            display_language=display_language,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch supported languages: {str(e)}",
        )


@router.get(
    "/health",
    summary="Translation service health check",
    description="Check if the translation service is operational",
    response_description="Service health status",
)
async def translation_health_check():
    """Health check endpoint for translation service."""
    try:
        # Simple health check by detecting language of a test text
        test_result = await translation_service.detect_language("Hello")

        return {
            "status": "healthy",
            "service": "translation",
            "timestamp": "2025-07-26T19:04:25+05:30",
            "test_detection": {
                "language": test_result["language_code"],
                "confidence": test_result["confidence"],
            },
        }

    except Exception as e:
        logger.error(
            "Translation service health check failed", error=str(e), error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Translation service is unhealthy: {str(e)}",
        )
