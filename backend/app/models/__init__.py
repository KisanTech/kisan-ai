# Pydantic Models Package

from .speech import (
    AudioValidationResponse,
    SpeechToTextRequest,
    SpeechToTextResponse,
    SupportedLanguagesResponse,
    TranscriptionResult,
    WordInfo,
)
from .translation import (
    BatchTranslationRequest,
    BatchTranslationResponse,
    LanguageDetectionRequest,
    LanguageDetectionResponse,
    SupportedLanguage,
    SupportedLanguagesResponse as TranslationSupportedLanguagesResponse,
    TranslationRequest,
    TranslationResponse,
)

__all__ = [
    "SpeechToTextRequest",
    "SpeechToTextResponse",
    "SupportedLanguagesResponse",
    "AudioValidationResponse",
    "TranscriptionResult",
    "WordInfo",
    "TranslationRequest",
    "BatchTranslationRequest",
    "TranslationResponse",
    "BatchTranslationResponse",
    "LanguageDetectionRequest",
    "LanguageDetectionResponse",
    "SupportedLanguage",
    "TranslationSupportedLanguagesResponse",
]
