"""
Agent Invocation API endpoints for Kisan AI Backend.

This module provides REST API endpoints for agent invocations that combine
multiple AI services like speech-to-text and translation.
"""

from fastapi import APIRouter, HTTPException, status
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agents.coordinator_agent.agent import root_agent
from app.models.agent_invocation import (
    TextAgentRequest,
    TextAgentResponse,
    VoiceAgentRequest,
    VoiceAgentResponse,
)
from app.services.speech_service import speech_service
from app.services.translation_service import translation_service
from app.utils.logger import logger

router = APIRouter(prefix="/invoke", tags=["agent-invocation"])

# Constants
APP_NAME = "kisan_ai_agent"


async def setup_session_and_runner(user_id: str, session_id: str):
    """Setup session and runner for agent interaction"""
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id
    )
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    return session, runner


async def call_agent_async(query: str, user_id: str, session_id: str) -> str:
    """Call the agent with a query and return the response"""
    try:
        content = types.Content(role='user', parts=[types.Part(text=query)])
        session, runner = await setup_session_and_runner(user_id, session_id)
        events = runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        )

        async for event in events:
            if event.is_final_response():
                final_response = event.content.parts[0].text
                logger.info(
                    "Agent response received",
                    user_id=user_id,
                    session_id=session_id,
                    response_length=len(final_response)
                )
                return final_response

        # If no final response found
        return "I apologize, but I couldn't process your request at the moment. Please try again."

    except Exception as e:
        logger.error(
            "Agent call failed",
            error=str(e),
            error_type=type(e).__name__,
            user_id=user_id,
            session_id=session_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent processing failed: {str(e)}"
        )


@router.post(
    "/voice",
    response_model=VoiceAgentResponse,
    summary="Transcribe speech, translate to English, and get AI agent response",
    description="Transcribe base64 encoded audio data to text, translate to English, and process through AI agent",
)
async def invoke_voice(request: VoiceAgentRequest) -> VoiceAgentResponse:
    """
    Transcribe speech to text, translate to English, and get AI agent response

    Args:
        request: Voice agent request containing audio data, user_id, and session_id

    Returns:
        VoiceAgentResponse containing transcription, translation, and agent response

    Raises:
        HTTPException: If transcription, translation, or agent processing fails
    """
    try:
        logger.info(
            "Voice invoke request received",
            user_id=request.user_id,
            session_id=request.session_id,
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
        transcription_result = await speech_service.transcribe_audio(
            base64_audio=request.audio_data,
            language_code=request.language_code,
            audio_encoding=request.audio_encoding,
            sample_rate=request.sample_rate,
            use_latest_model=request.use_latest_model,
        )

        # Check if transcription was successful
        if not transcription_result.get("success", False):
            error_msg = transcription_result.get("error", "Unknown transcription error")
            logger.error("Speech transcription failed", error=error_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transcription failed: {error_msg}",
            )

        # Get the transcribed text
        transcribed_text = transcription_result.get("full_transcript", "")

        if not transcribed_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text was transcribed from the audio"
            )

        logger.info(
            "Speech transcription completed",
            transcript_length=len(transcribed_text),
            confidence=transcription_result.get("average_confidence", 0.0),
        )

        # Translate the transcribed text to English
        translation_result = await translation_service.translate_text(
            text=transcribed_text,
            target_language="en",
            source_language=None  # Auto-detect source language
        )

        # Get the translated text
        translated_text = translation_result.get("translated_text", "")

        if not translated_text:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Translation failed: No translated text received"
            )

        logger.info(
            "Translation completed successfully",
            original_text_length=len(transcribed_text),
            translated_text_length=len(translated_text),
            detected_language=translation_result.get("detected_language", "unknown"),
        )

        # Process through AI agent
        agent_response = await call_agent_async(
            query=translated_text,
            user_id=request.user_id,
            session_id=request.session_id
        )

        logger.info(
            "Agent processing completed successfully",
            user_id=request.user_id,
            session_id=request.session_id,
            agent_response_length=len(agent_response)
        )

        # Translate agent response back to user's original language
        detected_language = translation_result.get("detected_language", "unknown")
        agent_response_translated = None

        if detected_language != "en" and detected_language != "unknown":
            try:
                translation_back_result = await translation_service.translate_text(
                    text=agent_response,
                    target_language=detected_language,
                    source_language="en"
                )
                agent_response_translated = translation_back_result.get("translated_text", agent_response)

                logger.info(
                    "Agent response translation completed",
                    user_id=request.user_id,
                    session_id=request.session_id,
                    target_language=detected_language,
                    translated_length=len(agent_response_translated)
                )
            except Exception as e:
                logger.warning(
                    "Failed to translate agent response back to user language",
                    error=str(e),
                    user_id=request.user_id,
                    session_id=request.session_id
                )
                agent_response_translated = agent_response
        else:
            agent_response_translated = agent_response

        # Convert translated agent response to speech
        response_audio_data = None
        response_audio_encoding = None
        response_audio_size_bytes = None

        try:
            # Map detected language to TTS language code
            tts_language_code = request.language_code  # Use original language code from request

            tts_result = await speech_service.text_to_speech(
                text=agent_response_translated,
                language_code=tts_language_code,
                audio_encoding="MP3",
                gender="FEMALE",
                speaking_rate=1.0,
                pitch=0.0,
                volume_gain_db=0.0,
                use_latest_model=True
            )

            if tts_result.get("success"):
                response_audio_data = tts_result.get("audio_data")
                response_audio_encoding = tts_result.get("audio_encoding", "MP3")
                response_audio_size_bytes = tts_result.get("audio_size_bytes", 0)

                logger.info(
                    "Text-to-speech conversion completed",
                    user_id=request.user_id,
                    session_id=request.session_id,
                    audio_size_bytes=response_audio_size_bytes,
                    language_code=tts_language_code
                )
            else:
                logger.warning(
                    "Text-to-speech conversion failed",
                    error=tts_result.get("error", "Unknown TTS error"),
                    user_id=request.user_id,
                    session_id=request.session_id
                )
        except Exception as e:
            logger.warning(
                "Failed to convert agent response to speech",
                error=str(e),
                user_id=request.user_id,
                session_id=request.session_id
            )

        # Return the complete response
        return VoiceAgentResponse(
            success=True,
            translated_text=translated_text,
            original_transcript=transcribed_text,
            detected_language=detected_language,
            transcription_confidence=transcription_result.get("average_confidence", 0.0),
            agent_response=agent_response,
            agent_response_translated=agent_response_translated,
            response_audio_data=response_audio_data,
            response_audio_encoding=response_audio_encoding,
            response_audio_size_bytes=response_audio_size_bytes,
            user_id=request.user_id,
            session_id=request.session_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error in voice invoke",
            error=str(e),
            error_type=type(e).__name__,
            user_id=getattr(request, 'user_id', 'unknown'),
            session_id=getattr(request, 'session_id', 'unknown'),
        )
        # Return error response instead of raising exception
        return VoiceAgentResponse(
            success=False,
            user_id=getattr(request, 'user_id', 'unknown'),
            session_id=getattr(request, 'session_id', 'unknown'),
            error=f"Internal server error during voice processing: {str(e)}"
        )


@router.post(
    "/text",
    response_model=TextAgentResponse,
    summary="Process text input through AI agent with translation",
    description="Translate user text to English, process through AI agent, and translate response back to user's language",
)
async def invoke_text(request: TextAgentRequest) -> TextAgentResponse:
    """
    Process text input through AI agent with translation

    Args:
        request: Text agent request containing text data, user_id, session_id, and language_code

    Returns:
        TextAgentResponse containing original text, translations, and agent response

    Raises:
        HTTPException: If translation or agent processing fails
    """
    try:
        logger.info(
            "Text invoke request received",
            user_id=request.user_id,
            session_id=request.session_id,
            text_length=len(request.text_data)
        )

        # Validate text input
        if not request.text_data.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text data cannot be empty"
            )

        # Translate user text to English
        translation_result = await translation_service.translate_text(
            text=request.text_data,
            target_language="en",
            source_language=None  # Auto-detect source language
        )

        # Get the translated text
        translated_text = translation_result.get("translated_text", "")
        detected_language = translation_result.get("detected_language", "unknown")

        if not translated_text:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Translation to English failed: No translated text received"
            )

        logger.info(
            "Text translation to English completed",
            user_id=request.user_id,
            session_id=request.session_id,
            original_length=len(request.text_data),
            translated_length=len(translated_text),
            detected_language=detected_language
        )

        # Process through AI agent
        agent_response = await call_agent_async(
            query=translated_text,
            user_id=request.user_id,
            session_id=request.session_id
        )

        logger.info(
            "Agent processing completed successfully",
            user_id=request.user_id,
            session_id=request.session_id,
            agent_response_length=len(agent_response)
        )

        # Translate agent response back to user's language
        target_language = detected_language
        agent_response_translated = None

        if target_language != "en" and target_language != "unknown":
            try:
                translation_back_result = await translation_service.translate_text(
                    text=agent_response,
                    target_language=target_language,
                    source_language="en"
                )
                agent_response_translated = translation_back_result.get("translated_text", agent_response)

                logger.info(
                    "Agent response translation completed",
                    user_id=request.user_id,
                    session_id=request.session_id,
                    target_language=target_language,
                    translated_length=len(agent_response_translated)
                )
            except Exception as e:
                logger.warning(
                    "Failed to translate agent response back to user language",
                    error=str(e),
                    user_id=request.user_id,
                    session_id=request.session_id
                )
                agent_response_translated = agent_response
        else:
            agent_response_translated = agent_response

        # Return the complete response
        return TextAgentResponse(
            success=True,
            original_text=request.text_data,
            translated_text=translated_text,
            detected_language=detected_language,
            agent_response=agent_response,
            agent_response_translated=agent_response_translated,
            user_id=request.user_id,
            session_id=request.session_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error in text invoke",
            error=str(e),
            error_type=type(e).__name__,
            user_id=getattr(request, 'user_id', 'unknown'),
            session_id=getattr(request, 'session_id', 'unknown'),
        )
        # Return error response instead of raising exception
        return TextAgentResponse(
            success=False,
            user_id=getattr(request, 'user_id', 'unknown'),
            session_id=getattr(request, 'session_id', 'unknown'),
            error=f"Internal server error during text processing: {str(e)}"
        )
