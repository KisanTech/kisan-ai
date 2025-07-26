"""
Pydantic models for Google Cloud Translation API.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    """Request model for text translation."""

    text: str = Field(..., description="Text to translate", min_length=1, max_length=30000)
    target_language: str = Field(..., description="Target language code (e.g., 'en', 'hi', 'kn')")
    source_language: Optional[str] = Field(
        None, description="Source language code. If not provided, auto-detect."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "नमस्ते, मैं एक किसान हूं",
                "target_language": "en",
                "source_language": "hi",
            }
        }


class BatchTranslationRequest(BaseModel):
    """Request model for batch text translation."""

    texts: List[str] = Field(
        ..., description="List of texts to translate", min_items=1, max_items=100
    )
    target_language: str = Field(..., description="Target language code")
    source_language: Optional[str] = Field(
        None, description="Source language code. If not provided, auto-detect."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "texts": ["नमस्ते, मैं एक किसान हूं", "मेरी फसल में कुछ समस्या है"],
                "target_language": "en",
                "source_language": "hi",
            }
        }


class TranslationResponse(BaseModel):
    """Response model for text translation."""

    translated_text: str = Field(..., description="Translated text")
    detected_language: str = Field(..., description="Detected source language code")
    source_language: str = Field(..., description="Source language code used")
    target_language: str = Field(..., description="Target language code")
    original_text: str = Field(..., description="Original input text")

    class Config:
        json_schema_extra = {
            "example": {
                "translated_text": "Hello, I am a farmer",
                "detected_language": "hi",
                "source_language": "hi",
                "target_language": "en",
                "original_text": "नमस्ते, मैं एक किसान हूं",
            }
        }


class BatchTranslationResponse(BaseModel):
    """Response model for batch text translation."""

    translations: List[TranslationResponse] = Field(..., description="List of translation results")
    total_count: int = Field(..., description="Total number of translations")

    class Config:
        json_schema_extra = {
            "example": {
                "translations": [
                    {
                        "translated_text": "Hello, I am a farmer",
                        "detected_language": "hi",
                        "source_language": "hi",
                        "target_language": "en",
                        "original_text": "नमस्ते, मैं एक किसान हूं",
                    }
                ],
                "total_count": 1,
            }
        }


class LanguageDetectionRequest(BaseModel):
    """Request model for language detection."""

    text: str = Field(
        ..., description="Text to analyze for language detection", min_length=1, max_length=30000
    )

    class Config:
        json_schema_extra = {"example": {"text": "नमस्ते, मैं एक किसान हूं"}}


class LanguageDetectionResponse(BaseModel):
    """Response model for language detection."""

    language_code: str = Field(..., description="Detected language code")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)")
    text: str = Field(..., description="Original input text")

    class Config:
        json_schema_extra = {
            "example": {"language_code": "hi", "confidence": 0.95, "text": "नमस्ते, मैं एक किसान हूं"}
        }


class SupportedLanguage(BaseModel):
    """Model for supported language information."""

    language_code: str = Field(..., description="Language code")
    display_name: str = Field(..., description="Display name of the language")
    support_source: bool = Field(..., description="Whether language is supported as source")
    support_target: bool = Field(..., description="Whether language is supported as target")

    class Config:
        json_schema_extra = {
            "example": {
                "language_code": "hi",
                "display_name": "Hindi",
                "support_source": True,
                "support_target": True,
            }
        }


class SupportedLanguagesResponse(BaseModel):
    """Response model for supported languages."""

    languages: List[SupportedLanguage] = Field(..., description="List of supported languages")
    total_count: int = Field(..., description="Total number of supported languages")
    display_language_code: str = Field(..., description="Language code used for display names")

    class Config:
        json_schema_extra = {
            "example": {
                "languages": [
                    {
                        "language_code": "hi",
                        "display_name": "Hindi",
                        "support_source": True,
                        "support_target": True,
                    }
                ],
                "total_count": 1,
                "display_language_code": "en",
            }
        }
