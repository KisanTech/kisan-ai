# Pydantic Models Package

from .speech import (
    SpeechToTextRequest,
    SpeechToTextResponse,
    SupportedLanguagesResponse,
    AudioValidationResponse,
    TranscriptionResult,
    WordInfo,
)

from .translation import (
    TranslationRequest,
    BatchTranslationRequest,
    TranslationResponse,
    BatchTranslationResponse,
    LanguageDetectionRequest,
    LanguageDetectionResponse,
    SupportedLanguage,
    SupportedLanguagesResponse as TranslationSupportedLanguagesResponse,
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
