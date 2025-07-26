# Pydantic Models Package

from .speech import (
    SpeechToTextRequest,
    SpeechToTextResponse,
    SupportedLanguagesResponse,
    AudioValidationResponse,
    TranscriptionResult,
    WordInfo,
)

__all__ = [
    "SpeechToTextRequest",
    "SpeechToTextResponse",
    "SupportedLanguagesResponse",
    "AudioValidationResponse",
    "TranscriptionResult",
    "WordInfo",
]
