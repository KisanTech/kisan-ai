"""
Speech-to-Text API endpoints using Google Cloud Speech API with latest models
"""


from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.models.speech import (
    AudioValidationResponse,
    AvailableVoicesResponse,
    SpeechToTextRequest,
    SpeechToTextResponse,
    SupportedLanguagesResponse,
    TextToSpeechRequest,
    TextToSpeechResponse,
)
from app.services.speech_service import speech_service
from app.utils.logger import logger

router = APIRouter(prefix="/speech", tags=["speech"])


@router.post(
    "/transcribe",
    response_model=SpeechToTextResponse,
    summary="Convert speech to text using Google Chirp model",
    description="Transcribe base64 encoded audio data to text using Google Cloud Speech API with Chirp model for better accuracy in Indian languages",
)
async def transcribe_speech(request: SpeechToTextRequest) -> SpeechToTextResponse:
    """
    Transcribe speech to text using Google Cloud Speech API

    Args:
        request: Speech-to-text request containing base64 audio data and parameters

    Returns:
        Transcription results with confidence scores and word-level timing

    Raises:
        HTTPException: If transcription fails or invalid parameters provided
    """
    try:
        logger.info(
            "Speech transcription request received",
            language=request.language_code,
            encoding=request.audio_encoding,
            sample_rate=request.sample_rate,
            use_latest_model=request.use_latest_model,
            audio_size=len(request.audio_data),
        )

        # Validate audio data
        if not request.audio_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Audio data is required"
            )

        # Perform transcription
        result = await speech_service.transcribe_audio(
            base64_audio=request.audio_data,
            language_code=request.language_code,
            audio_encoding=request.audio_encoding,
            sample_rate=request.sample_rate,
            use_latest_model=request.use_latest_model,
        )

        # Check if transcription was successful
        if not result.get("success", False):
            error_msg = result.get("error", "Unknown transcription error")
            logger.error("Speech transcription failed", error=error_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transcription failed: {error_msg}",
            )

        # Return successful response
        response = SpeechToTextResponse(**result)

        logger.info(
            "Speech transcription completed successfully",
            transcript_length=len(response.full_transcript),
            confidence=response.average_confidence,
            results_count=len(response.results),
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error in speech transcription",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during transcription",
        )


@router.get(
    "/languages",
    response_model=SupportedLanguagesResponse,
    summary="Get supported languages for speech recognition",
    description="Retrieve list of supported languages for Google Cloud Speech API",
)
async def get_supported_languages() -> SupportedLanguagesResponse:
    """
    Get list of supported languages for speech recognition

    Returns:
        Dictionary of supported language codes and recommendations
    """
    try:
        result = await speech_service.get_supported_languages()
        return SupportedLanguagesResponse(**result)
    except Exception as e:
        logger.error(
            "Error retrieving supported languages",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve supported languages",
        )


@router.post(
    "/validate-audio",
    response_model=AudioValidationResponse,
    summary="Validate audio format and get recommendations",
    description="Validate base64 encoded audio data and provide optimization recommendations",
)
async def validate_audio_format(audio_data: str) -> AudioValidationResponse:
    """
    Validate audio format and provide recommendations

    Args:
        audio_data: Base64 encoded audio data to validate

    Returns:
        Validation results and optimization recommendations

    Raises:
        HTTPException: If validation fails
    """
    try:
        if not audio_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Audio data is required for validation",
            )

        result = await speech_service.validate_audio_format(audio_data)
        return AudioValidationResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error validating audio format",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate audio format",
        )


@router.get(
    "/health",
    summary="Health check for speech service",
    description="Check if Google Cloud Speech API is accessible and configured correctly",
)
async def speech_health_check():
    """
    Health check for speech service

    Returns:
        Service health status and configuration info
    """
    try:
        # Basic health check - verify service initialization
        supported_languages = await speech_service.get_supported_languages()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "service": "Google Cloud Speech API",
                "model": "Chirp",
                "supported_languages_count": len(supported_languages["supported_languages"]),
                "default_language": supported_languages["default_language"],
                "timestamp": "2025-07-26T17:28:30+05:30",
            },
        )
    except Exception as e:
        logger.error(
            "Speech service health check failed",
            error=str(e),
            error_type=type(e).__name__,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "Google Cloud Speech API",
                "error": str(e),
                "timestamp": "2025-07-26T17:28:30+05:30",
            },
        )


@router.post(
    "/synthesize",
    response_model=TextToSpeechResponse,
    summary="Convert text to speech using Google Cloud TTS",
    description="Convert text to speech using Google Cloud Text-to-Speech API with support for multiple Indian languages and voice customization",
)
async def synthesize_speech(request: TextToSpeechRequest) -> TextToSpeechResponse:
    """
    Convert text to speech using Google Cloud Text-to-Speech API

    Args:
        request: Text-to-speech request containing text and voice parameters

    Returns:
        Audio data in base64 format with metadata

    Raises:
        HTTPException: If synthesis fails or invalid parameters provided
    """
    try:
        logger.info(
            "Text-to-speech synthesis request received",
            text_length=len(request.text),
            language=request.language_code,
            voice_name=request.voice_name,
            gender=request.gender,
            encoding=request.audio_encoding,
            use_latest_model=request.use_latest_model,
        )

        # Validate text input
        if not request.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Text input cannot be empty"
            )

        if len(request.text) > 5000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text input too long. Maximum 5000 characters allowed.",
            )

        # Call the speech service
        result = await speech_service.text_to_speech(
            text=request.text,
            language_code=request.language_code,
            voice_name=request.voice_name,
            gender=request.gender,
            audio_encoding=request.audio_encoding,
            speaking_rate=request.speaking_rate,
            pitch=request.pitch,
            volume_gain_db=request.volume_gain_db,
            use_latest_model=request.use_latest_model,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Text-to-speech synthesis failed: {result.get('error', 'Unknown error')}",
            )

        logger.info(
            "Text-to-speech synthesis completed successfully",
            audio_size_bytes=result["audio_size_bytes"],
            estimated_duration=result.get("estimated_duration_seconds"),
        )

        return TextToSpeechResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Text-to-speech synthesis failed",
            error=str(e),
            error_type=type(e).__name__,
            text_length=len(request.text) if request.text else 0,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text-to-speech synthesis failed: {str(e)}",
        )


@router.get(
    "/voices",
    response_model=AvailableVoicesResponse,
    summary="Get available voices for text-to-speech",
    description="Retrieve list of available voices from Google Cloud Text-to-Speech API, optionally filtered by language",
)
async def get_available_voices(language_code: str | None = None) -> AvailableVoicesResponse:
    """
    Get list of available voices for text-to-speech

    Args:
        language_code: Optional language code to filter voices (e.g., 'hi', 'en')

    Returns:
        List of available voices with their properties

    Raises:
        HTTPException: If fetching voices fails
    """
    try:
        logger.info("Available voices request received", language_filter=language_code)

        # Call the speech service
        result = await speech_service.get_available_voices(language_code=language_code)

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch available voices: {result['error']}",
            )

        logger.info(
            "Available voices fetched successfully",
            total_voices=result["total_voices"],
            languages_count=len(result["languages_supported"]),
        )

        return AvailableVoicesResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to fetch available voices",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch available voices: {str(e)}",
        )


@router.get(
    "/tts/health",
    summary="Text-to-Speech service health check",
    description="Check the health status of the Google Cloud Text-to-Speech service",
)
async def tts_health_check():
    """
    Health check for text-to-speech service

    Returns:
        Service health status and configuration info
    """
    try:
        logger.info("TTS health check requested")

        # Test TTS service with a simple request
        test_result = await speech_service.text_to_speech(
            text="Test",
            language_code="en-US",
            audio_encoding="MP3",
        )

        if test_result["success"]:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "healthy",
                    "service": "Google Cloud Text-to-Speech API",
                    "features": {
                        "chirp_support": True,
                        "supported_languages": [
                            "hi-IN",
                            "en-US",
                            "kn-IN",
                            "te-IN",
                            "ta-IN",
                            "ml-IN",
                            "gu-IN",
                            "mr-IN",
                            "bn-IN",
                            "pa-IN",
                        ],
                        "supported_encodings": ["MP3", "LINEAR16", "OGG_OPUS"],
                        "voice_customization": True,
                    },
                    "timestamp": "2025-07-26T17:50:03+05:30",
                },
            )
        else:
            raise Exception(test_result.get("error", "TTS test failed"))

    except Exception as e:
        logger.error(
            "TTS service health check failed",
            error=str(e),
            error_type=type(e).__name__,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "Google Cloud Text-to-Speech API",
                "error": str(e),
                "timestamp": "2025-07-26T17:50:03+05:30",
            },
        )
