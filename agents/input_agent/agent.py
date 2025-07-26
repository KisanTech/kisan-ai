from google.adk.agents import Agent
from google.adk.tools import google_search, FunctionTool
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, Dict
import requests
import os


class InputSchema(BaseModel):
    """Schema for input data supporting both text and voice inputs."""
    
    input_type: Literal["TEXT", "VOICE"] = Field(
        description="Type of input - either TEXT or VOICE"
    )
    
    # Voice-specific fields
    audio_data: Optional[str] = Field(
        default=None,
        description="Base64 encoded audio data, required when input_type is VOICE"
    )
    
    audio_encoding: Optional[str] = Field(
        default=None,
        description="Audio encoding format, required when input_type is VOICE"
    )
    
    language_code: Optional[str] = Field(
        default=None,
        description="Language code for audio processing, required when input_type is VOICE"
    )
    
    # Text-specific field
    text_data: Optional[str] = Field(
        default=None,
        description="Text input data, required when input_type is TEXT"
    )
    
    @validator('audio_data', 'audio_encoding', 'language_code')
    def validate_voice_fields(cls, v, values):
        """Validate that voice fields are provided when input_type is VOICE."""
        if values.get('input_type') == 'VOICE' and v is None:
            raise ValueError('This field is required when input_type is VOICE')
        elif values.get('input_type') == 'TEXT' and v is not None:
            raise ValueError('This field should not be provided when input_type is TEXT')
        return v
    
    @validator('text_data')
    def validate_text_data(cls, v, values):
        """Validate that text_data is provided when input_type is TEXT."""
        if values.get('input_type') == 'TEXT' and v is None:
            raise ValueError('text_data is required when input_type is TEXT')
        elif values.get('input_type') == 'VOICE' and v is not None:
            raise ValueError('text_data should not be provided when input_type is VOICE')
        return v


def process_input(
    input_type: str,
    audio_data: Optional[str] = None,
    audio_encoding: Optional[str] = None,
    language_code: Optional[str] = None,
    text_data: Optional[str] = None
) -> Dict[str, str]:
    """
    Process input by making sequential API calls for speech transcription and translation.
    
    Args:
        input_type: Type of input ("TEXT" or "VOICE")
        audio_data: Base64 encoded audio data (required for VOICE)
        audio_encoding: Audio encoding format (required for VOICE)
        language_code: Language code (required for VOICE)
        text_data: Text input (required for TEXT)
    
    Returns:
        Dict containing input_type, audio_encoding, language_code, and translated_text
    """
    base_url = os.getenv('BACKEND_API_URL')
    
    # Initialize variables
    full_transcript = ""
    
    # Step 1: Speech transcription (only for VOICE input)
    if input_type == "VOICE":
        transcribe_url = f"{base_url}/api/v1/speech/speech/transcribe"
        transcribe_payload = {
            "audio_data": audio_data,
            "audio_encoding": audio_encoding,
            "language_code": language_code
        }
        
        try:
            transcribe_response = requests.post(
                transcribe_url,
                json=transcribe_payload,
                headers={'Content-Type': 'application/json'}
            )
            transcribe_response.raise_for_status()
            
            transcribe_data = transcribe_response.json()
            full_transcript = transcribe_data.get('full_transcript', '')
            # Update language_code from response if provided
            response_language = transcribe_data.get('language_code')
            if response_language:
                language_code = response_language
            else:
                raise Exception("Speech transcription failed")
                
        except requests.RequestException as e:
            raise Exception(f"Error in speech transcription: {str(e)}")
    else:
        # For TEXT input, use the provided text_data
        full_transcript = text_data or ""
    
    # Step 2: Translation (always called)
    translate_url = f"{base_url}/api/v1/translation/translate"
    translate_payload = {
        "target_language": "en",
        "text": full_transcript
    }
    
    translated_text = ""
    try:
        translate_response = requests.post(
            translate_url,
            json=translate_payload,
            headers={'Content-Type': 'application/json'}
        )
        translate_response.raise_for_status()
        
        translate_data = translate_response.json()
        translated_text = translate_data.get('translated_text', '')
        
    except requests.RequestException as e:
        raise Exception(f"Error in translation: {str(e)}")
    
    # Return the required fields
    return {
        "input_type": input_type,
        "audio_encoding": audio_encoding,
        "language_code": language_code,
        "translated_text": translated_text
    }

process_input_tool = FunctionTool(func=process_input)
    

root_agent = Agent(
    name="input_agent",
    model="gemini-2.5-flash",
    description=(
        "Input Transforming agent"
    ),
    instruction=(
        "ALWAYS Transform the user input using the tool. You MUST use the tool ALWAYS."
    ),
    input_schema=InputSchema,
    output_key="output",
    tools=[process_input_tool]
)