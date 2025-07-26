"""
Pydantic models for Agent Invocation API
"""

from typing import Optional
from pydantic import BaseModel, Field

from app.models.speech import SpeechToTextRequest


class TextAgentRequest(BaseModel):
    """Request model for text agent invocation"""
    
    user_id: str = Field(..., description="Unique user identifier")
    session_id: str = Field(..., description="Session identifier for conversation continuity")
    text_data: str = Field(..., description="Text input from user", min_length=1, max_length=5000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": "session456",
                "text_data": "मेरी टमाटर की फसल में कुछ समस्या है"
            }
        }


class TextAgentResponse(BaseModel):
    """Response model for text agent invocation"""
    
    success: bool = Field(..., description="Whether the request was successful")
    original_text: Optional[str] = Field(None, description="Original text input from user")
    translated_text: Optional[str] = Field(None, description="User text translated to English")
    detected_language: Optional[str] = Field(None, description="Detected source language")
    agent_response: Optional[str] = Field(None, description="Response from the AI agent in English")
    agent_response_translated: Optional[str] = Field(None, description="Agent response translated to user's language")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    error: Optional[str] = Field(None, description="Error message if request failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "original_text": "मेरी टमाटर की फसल में कुछ समस्या है",
                "translated_text": "There is some problem with my tomato crop",
                "detected_language": "hi",
                "agent_response": "I can help you diagnose the issue with your tomato crop. Can you describe the specific symptoms you're seeing?",
                "agent_response_translated": "मैं आपकी टमाटर की फसल की समस्या का निदान करने में आपकी मदद कर सकता हूं। क्या आप उन विशिष्ट लक्षणों का वर्णन कर सकते हैं जो आप देख रहे हैं?",
                "user_id": "user123",
                "session_id": "session456",
                "error": None
            }
        }


class VoiceAgentRequest(SpeechToTextRequest):
    """Request model for voice agent invocation that extends SpeechToTextRequest"""
    
    user_id: str = Field(..., description="Unique user identifier")
    session_id: str = Field(..., description="Session identifier for conversation continuity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "audio_data": "UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVg...",
                "language_code": "hi-IN",
                "audio_encoding": "WEBM_OPUS",
                "sample_rate": 48000,
                "use_latest_model": True,
                "user_id": "user123",
                "session_id": "session456"
            }
        }


class VoiceAgentResponse(BaseModel):
    """Response model for voice agent invocation"""
    
    success: bool = Field(..., description="Whether the request was successful")
    translated_text: Optional[str] = Field(None, description="Translated text from audio")
    original_transcript: Optional[str] = Field(None, description="Original transcribed text")
    detected_language: Optional[str] = Field(None, description="Detected source language")
    transcription_confidence: Optional[float] = Field(None, description="Transcription confidence score")
    agent_response: Optional[str] = Field(None, description="Response from the AI agent in English")
    agent_response_translated: Optional[str] = Field(None, description="Agent response translated to user's language")
    response_audio_data: Optional[str] = Field(None, description="Base64 encoded audio of translated agent response")
    response_audio_encoding: Optional[str] = Field(None, description="Audio encoding format used")
    response_audio_size_bytes: Optional[int] = Field(None, description="Audio size in bytes")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    error: Optional[str] = Field(None, description="Error message if request failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "translated_text": "Hello, I am a farmer",
                "original_transcript": "नमस्ते, मैं एक किसान हूं",
                "detected_language": "hi",
                "transcription_confidence": 0.95,
                "agent_response": "Hello! I'm here to help you with agricultural queries. What would you like to know about farming, market prices, or crop diagnosis?",
                "agent_response_translated": "नमस्ते! मैं आपकी कृषि संबंधी प्रश्नों में मदद करने के लिए यहाँ हूँ। आप खेती, बाजार की कीमतों या फसल निदान के बारे में क्या जानना चाहेंगे?",
                "response_audio_data": "UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVg...",
                "response_audio_encoding": "MP3",
                "response_audio_size_bytes": 15420,
                "user_id": "user123",
                "session_id": "session456",
                "error": None
            }
        }
