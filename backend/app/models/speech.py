"""
Pydantic models for Speech-to-Text API
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class WordInfo(BaseModel):
    """Individual word information from speech recognition"""

    word: str = Field(..., description="The recognized word")
    confidence: float = Field(..., description="Confidence score for this word (0.0-1.0)")
    start_time: float = Field(..., description="Start time in seconds")
    end_time: float = Field(..., description="End time in seconds")


class TranscriptionResult(BaseModel):
    """Single transcription result"""

    transcript: str = Field(..., description="The transcribed text")
    confidence: float = Field(..., description="Overall confidence score (0.0-1.0)")
    words: List[WordInfo] = Field(default=[], description="Word-level timing and confidence")


class SpeechToTextRequest(BaseModel):
    """Request model for speech-to-text conversion"""

    audio_data: str = Field(..., description="Base64 encoded audio data")
    language_code: str = Field(
        default="hi-IN", description="Language code (e.g., 'hi-IN', 'en-US')"
    )
    audio_encoding: str = Field(default="WEBM_OPUS", description="Audio encoding format")
    sample_rate: int = Field(default=48000, description="Audio sample rate in Hz")
    use_latest_model: bool = Field(default=True, description="Use latest model for better accuracy")

    class Config:
        json_schema_extra = {
            "example": {
                "audio_data": "UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVg...",
                "language_code": "hi-IN",
                "audio_encoding": "WEBM_OPUS",
                "sample_rate": 48000,
                "use_latest_model": True,
            }
        }


class SpeechToTextResponse(BaseModel):
    """Response model for speech-to-text conversion"""

    success: bool = Field(..., description="Whether the transcription was successful")
    language_code: str = Field(..., description="Language code used for transcription")
    model_used: str = Field(..., description="Model used for transcription (chirp/latest_long)")
    results: List[TranscriptionResult] = Field(default=[], description="Transcription results")
    full_transcript: str = Field(default="", description="Complete transcribed text")
    average_confidence: float = Field(default=0.0, description="Average confidence score")
    total_duration: float = Field(default=0.0, description="Total audio duration in seconds")
    error: Optional[str] = Field(None, description="Error message if transcription failed")
    error_type: Optional[str] = Field(None, description="Type of error if transcription failed")


class SupportedLanguagesResponse(BaseModel):
    """Response model for supported languages"""

    supported_languages: dict = Field(..., description="Dictionary of supported language codes")
    default_language: str = Field(..., description="Default language code")
    recommended_for_agriculture: List[str] = Field(
        ..., description="Recommended languages for agriculture"
    )


class AudioValidationResponse(BaseModel):
    """Response model for audio validation"""

    is_valid: bool = Field(..., description="Whether the audio format is valid")
    audio_size_bytes: int = Field(..., description="Audio size in bytes")
    audio_size_mb: float = Field(..., description="Audio size in MB")
    estimated_duration_seconds: Optional[float] = Field(
        None, description="Estimated duration in seconds"
    )
    recommendations: List[str] = Field(
        default=[], description="Recommendations for audio optimization"
    )
    error: Optional[str] = Field(None, description="Error message if validation failed")


class TextToSpeechRequest(BaseModel):
    """Request model for text-to-speech conversion"""

    text: str = Field(..., description="Text to convert to speech", max_length=5000)
    language_code: str = Field(
        default="hi-IN", description="Language code (e.g., 'hi-IN', 'en-US')"
    )
    voice_name: Optional[str] = Field(None, description="Specific voice name to use")
    gender: str = Field(default="NEUTRAL", description="Voice gender: MALE, FEMALE, or NEUTRAL")
    audio_encoding: str = Field(
        default="MP3", description="Output audio encoding: MP3, LINEAR16, OGG_OPUS"
    )
    speaking_rate: float = Field(
        default=1.0, description="Speaking rate (0.25 to 4.0)", ge=0.25, le=4.0
    )
    pitch: float = Field(default=0.0, description="Voice pitch (-20.0 to 20.0)", ge=-20.0, le=20.0)
    volume_gain_db: float = Field(
        default=0.0, description="Volume gain in dB (-96.0 to 16.0)", ge=-96.0, le=16.0
    )
    use_latest_model: bool = Field(default=True, description="Use latest model for better quality")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "नमस्ते, आज मौसम कैसा है?",
                "language_code": "hi-IN",
                "gender": "FEMALE",
                "audio_encoding": "MP3",
                "speaking_rate": 1.0,
                "pitch": 0.0,
                "volume_gain_db": 0.0,
                "use_latest_model": True,
            }
        }


class TextToSpeechResponse(BaseModel):
    """Response model for text-to-speech conversion"""

    success: bool = Field(..., description="Whether the conversion was successful")
    audio_data: Optional[str] = Field(None, description="Base64 encoded audio data")
    audio_encoding: str = Field(..., description="Audio encoding format used")
    audio_size_bytes: int = Field(..., description="Audio size in bytes")
    audio_size_mb: float = Field(..., description="Audio size in MB")
    estimated_duration_seconds: Optional[float] = Field(
        None, description="Estimated audio duration"
    )
    voice_used: Optional[str] = Field(None, description="Voice name that was used")
    language_code: str = Field(..., description="Language code used")
    error: Optional[str] = Field(None, description="Error message if conversion failed")


class VoiceInfo(BaseModel):
    """Information about available voices"""

    name: str = Field(..., description="Voice name")
    language_code: str = Field(..., description="Language code")
    gender: str = Field(..., description="Voice gender")
    natural_sample_rate: int = Field(..., description="Natural sample rate in Hz")


class AvailableVoicesResponse(BaseModel):
    """Response model for available voices"""

    voices: List[VoiceInfo] = Field(..., description="List of available voices")
    total_voices: int = Field(..., description="Total number of available voices")
    languages_supported: List[str] = Field(..., description="List of supported language codes")
