"""
Speech-to-Text service using Google Cloud Speech API with latest models
Handles base64 encoded audio data from React Native app
"""

import base64
from concurrent.futures import TimeoutError

from google.cloud import speech, texttospeech
from google.cloud.speech import RecognitionAudio, RecognitionConfig

from app.utils.logger import logger


class SpeechToTextService:
    """
    Service for converting speech to text using Google Cloud Speech API with latest models
    """

    def __init__(self):
        self.client = speech.SpeechClient()
        self.tts_client = texttospeech.TextToSpeechClient()
        self._supported_languages = {
            "hi": "hi-IN",  # Hindi
            "en": "en-US",  # English
            "kn": "kn-IN",  # Kannada
            "te": "te-IN",  # Telugu
            "ta": "ta-IN",  # Tamil
            "ml": "ml-IN",  # Malayalam
            "gu": "gu-IN",  # Gujarati
            "mr": "mr-IN",  # Marathi
            "bn": "bn-IN",  # Bengali
            "pa": "pa-IN",  # Punjabi
        }

    async def transcribe_audio(
        self,
        base64_audio: str,
        language_code: str = "hi-IN",
        audio_encoding: str = "WEBM_OPUS",
        sample_rate: int = 48000,
        use_latest_model: bool = True,
    ) -> dict:
        """
        Transcribe base64 encoded audio to text using Google Speech API

        Args:
            base64_audio: Base64 encoded audio data
            language_code: Language code (e.g., 'hi-IN', 'en-US')
            audio_encoding: Audio encoding format
            sample_rate: Audio sample rate in Hz
            use_latest_model: Whether to use the latest model for better accuracy

        Returns:
            Dictionary containing transcription results and metadata
        """
        try:
            # Validate language code
            if language_code not in self._supported_languages.values():
                # Try to map from short code
                short_code = language_code.split("-")[0] if "-" in language_code else language_code
                if short_code in self._supported_languages:
                    language_code = self._supported_languages[short_code]
                else:
                    logger.warning(
                        f"Unsupported language code: {language_code}, defaulting to hi-IN"
                    )
                    language_code = "hi-IN"

            # Decode base64 audio
            try:
                audio_data = base64.b64decode(base64_audio)
            except Exception as decode_error:
                logger.error("Failed to decode base64 audio", error=str(decode_error))
                raise ValueError("Invalid base64 audio data")

            # Check audio size to determine recognition method
            audio_size_mb = len(audio_data) / (1024 * 1024)
            estimated_duration = self._estimate_audio_duration(
                len(audio_data), sample_rate, audio_encoding
            )
            use_async = (
                audio_size_mb > 10 or estimated_duration > 60
            )  # Use async for files > 10MB or > 60 seconds

            logger.info(
                "Audio analysis",
                audio_size_bytes=len(audio_data),
                audio_size_mb=round(audio_size_mb, 2),
                estimated_duration_seconds=estimated_duration,
                will_use_async=use_async,
            )

            # Configure recognition settings
            config = RecognitionConfig(
                encoding=getattr(speech.RecognitionConfig.AudioEncoding, audio_encoding),
                sample_rate_hertz=sample_rate,
                language_code=language_code,
                enable_automatic_punctuation=True,
                enable_word_confidence=True,
                enable_word_time_offsets=True,
                model=self._get_best_model(language_code, use_latest_model),
                audio_channel_count=1,  # Mono audio
            )

            # Only use enhanced model when not using latest model (they are incompatible)
            if not use_latest_model:
                config.use_enhanced = True

            # Create audio object
            audio = RecognitionAudio(content=audio_data)

            logger.info(
                "Starting speech recognition",
                language=language_code,
                model=config.model,
                audio_size=len(audio_data),
            )

            # Perform speech recognition
            try:
                if use_async:
                    operation = self.client.long_running_recognize(config=config, audio=audio)
                    try:
                        response = operation.result(timeout=600)  # 10 minutes
                    except TimeoutError:
                        logger.error("Async speech recognition timed out")
                        raise ValueError("Async speech recognition timed out")
                else:
                    response = self.client.recognize(config=config, audio=audio)
            except Exception as recognition_error:
                # If latest model fails, try fallback to latest_long without enhanced
                if use_latest_model and "enhanced model" in str(recognition_error).lower():
                    logger.warning(
                        "Latest model not available for language, falling back to latest_long",
                        language=language_code,
                        original_error=str(recognition_error),
                    )

                    # Fallback configuration
                    fallback_config = RecognitionConfig(
                        encoding=getattr(speech.RecognitionConfig.AudioEncoding, audio_encoding),
                        sample_rate_hertz=sample_rate,
                        language_code=language_code,
                        enable_automatic_punctuation=False,
                        enable_word_confidence=False,
                        enable_word_time_offsets=False,
                        model=self._get_best_model(
                            language_code, False
                        ),  # Use basic model for fallback
                        audio_channel_count=1,
                    )

                    if use_async:
                        operation = self.client.long_running_recognize(
                            config=fallback_config, audio=audio
                        )
                        try:
                            response = operation.result(timeout=600)  # 10 minutes
                        except TimeoutError:
                            logger.error("Async speech recognition timed out")
                            raise ValueError("Async speech recognition timed out")
                    else:
                        response = self.client.recognize(config=fallback_config, audio=audio)
                    use_latest_model = False  # Update for logging
                else:
                    raise recognition_error

            # Process results
            results = []
            for result in response.results:
                alternative = result.alternatives[0]

                # Extract word-level details
                words = []
                for word_info in alternative.words:
                    words.append(
                        {
                            "word": word_info.word,
                            "confidence": word_info.confidence,
                            "start_time": word_info.start_time.total_seconds(),
                            "end_time": word_info.end_time.total_seconds(),
                        }
                    )

                results.append(
                    {
                        "transcript": alternative.transcript,
                        "confidence": alternative.confidence,
                        "words": words,
                    }
                )

            # Compile final response
            transcription_result = {
                "success": True,
                "language_code": language_code,
                "model_used": config.model,
                "recognition_method": "async" if use_async else "sync",
                "audio_size_mb": round(audio_size_mb, 2),
                "estimated_duration_seconds": estimated_duration,
                "results": results,
                "full_transcript": " ".join([r["transcript"] for r in results]),
                "average_confidence": (
                    sum([r["confidence"] for r in results]) / len(results) if results else 0.0
                ),
                "total_duration": (
                    max([w["end_time"] for r in results for w in r["words"]])
                    if results and any(r["words"] for r in results)
                    else 0.0
                ),
            }

            logger.info(
                "Speech recognition completed",
                transcript_length=len(transcription_result["full_transcript"]),
                confidence=transcription_result["average_confidence"],
                results_count=len(results),
                method=transcription_result["recognition_method"],
                audio_size_mb=transcription_result["audio_size_mb"],
            )

            return transcription_result

        except Exception as e:
            logger.error(
                "Speech recognition failed",
                error=str(e),
                error_type=type(e).__name__,
                language=language_code,
            )
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "language_code": language_code,
            }

    def _get_best_model(self, language_code: str, use_latest_model: bool = True) -> str:
        """
        Get the best available model for the given language

        Args:
            language_code: Language code (e.g., 'hi-IN', 'en-US')
            use_latest_model: Whether to prefer latest models

        Returns:
            Model name to use
        """
        # Models that support Indian languages well
        indian_language_models = {
            "hi-IN": "latest_long",  # Hindi
            "kn-IN": "latest_long",  # Kannada
            "te-IN": "latest_long",  # Telugu
            "ta-IN": "latest_long",  # Tamil
            "ml-IN": "latest_long",  # Malayalam
            "gu-IN": "latest_long",  # Gujarati
            "mr-IN": "latest_long",  # Marathi
            "bn-IN": "latest_long",  # Bengali
            "pa-IN": "latest_long",  # Punjabi
        }

        # Determine the best model based on language and preference
        if language_code in indian_language_models:
            model = indian_language_models[language_code]
        elif language_code.startswith("en-") and use_latest_model:
            model = "video"  # Video model works well for English
        elif use_latest_model:
            model = "latest_long"  # Safe fallback for other languages
        else:
            model = "default"  # Basic model

        logger.info(
            "Model selected for language",
            language_code=language_code,
            model=model,
            use_latest_model=use_latest_model,
        )

        return model

    def _estimate_audio_duration(
        self, audio_size_bytes: int, sample_rate: int = 48000, encoding: str = "WEBM_OPUS"
    ) -> float:
        """
        Estimate audio duration based on file size and encoding
        This is a rough estimation for logging purposes
        """
        # Rough estimates for different encodings (bytes per second)
        encoding_bitrates = {
            "WEBM_OPUS": 6000,  # ~48kbps
            "MP3": 16000,  # ~128kbps
            "WAV": 96000,  # ~768kbps for 48kHz 16-bit
            "FLAC": 48000,  # ~384kbps
        }

        bytes_per_second = encoding_bitrates.get(encoding, 6000)
        estimated_duration = audio_size_bytes / bytes_per_second
        return round(estimated_duration, 1)

    async def get_supported_languages(self) -> dict:
        """
        Get list of supported languages for speech recognition

        Returns:
            Dictionary of supported language codes and names
        """
        return {
            "supported_languages": self._supported_languages,
            "default_language": "hi-IN",
            "recommended_for_agriculture": ["hi-IN", "en-US", "kn-IN"],
        }

    async def validate_audio_format(self, base64_audio: str) -> dict:
        """
        Validate the audio format and provide recommendations

        Args:
            base64_audio: Base64 encoded audio data

        Returns:
            Validation results and recommendations
        """
        try:
            audio_data = base64.b64decode(base64_audio)
            audio_size = len(audio_data)

            # Basic validation
            validation_result = {
                "is_valid": True,
                "audio_size_bytes": audio_size,
                "audio_size_mb": round(audio_size / (1024 * 1024), 2),
                "recommendations": [],
            }

            # Size recommendations
            if audio_size > 10 * 1024 * 1024:  # 10MB
                validation_result["recommendations"].append(
                    "Audio file is large (>10MB). Consider compressing or using streaming recognition."
                )
            elif audio_size < 1024:  # 1KB
                validation_result["recommendations"].append(
                    "Audio file is very small (<1KB). May not contain sufficient audio data."
                )

            # Duration estimation (rough)
            estimated_duration = audio_size / (48000 * 2)  # Assuming 48kHz, 16-bit
            validation_result["estimated_duration_seconds"] = round(estimated_duration, 2)

            if estimated_duration > 60:
                validation_result["recommendations"].append(
                    "Audio duration is long (>60s). Consider using streaming recognition for better performance."
                )

            return validation_result

        except Exception as e:
            logger.error("Audio validation failed", error=str(e))
            return {
                "is_valid": False,
                "error": str(e),
                "recommendations": ["Ensure audio is properly base64 encoded"],
            }

    async def text_to_speech(
        self,
        text: str,
        language_code: str = "hi-IN",
        voice_name: str | None = None,
        gender: str = "NEUTRAL",
        audio_encoding: str = "MP3",
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        volume_gain_db: float = 0.0,
        use_latest_model: bool = True,
    ) -> dict:
        """
        Convert text to speech using Google Cloud Text-to-Speech API

        Args:
            text: Text to convert to speech
            language_code: Language code (e.g., 'hi-IN', 'en-US')
            voice_name: Specific voice name to use
            gender: Voice gender (MALE, FEMALE, NEUTRAL)
            audio_encoding: Output audio encoding (MP3, LINEAR16, OGG_OPUS)
            speaking_rate: Speaking rate (0.25 to 4.0)
            pitch: Voice pitch (-20.0 to 20.0)
            volume_gain_db: Volume gain in dB (-96.0 to 16.0)
            use_latest_model: Use latest model for better quality

        Returns:
            Dictionary containing audio data and metadata
        """
        try:
            logger.info(
                "Text-to-speech conversion started",
                text_length=len(text),
                language=language_code,
                voice_name=voice_name,
                gender=gender,
                encoding=audio_encoding,
                use_latest_model=use_latest_model,
            )

            # Validate language code
            if language_code not in self._supported_languages.values():
                logger.warning(f"Language {language_code} not in supported list, proceeding anyway")

            # Set up synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Configure voice selection
            voice_selection_params = {
                "language_code": language_code,
            }

            # Map gender string to enum
            gender_mapping = {
                "MALE": texttospeech.SsmlVoiceGender.MALE,
                "FEMALE": texttospeech.SsmlVoiceGender.FEMALE,
                "NEUTRAL": texttospeech.SsmlVoiceGender.NEUTRAL,
            }
            voice_selection_params["ssml_gender"] = gender_mapping.get(
                gender.upper(), texttospeech.SsmlVoiceGender.NEUTRAL
            )

            # Use specific voice if provided
            if voice_name:
                voice_selection_params["name"] = voice_name

            voice = texttospeech.VoiceSelectionParams(**voice_selection_params)

            # Configure audio output
            audio_encoding_mapping = {
                "MP3": texttospeech.AudioEncoding.MP3,
                "LINEAR16": texttospeech.AudioEncoding.LINEAR16,
                "OGG_OPUS": texttospeech.AudioEncoding.OGG_OPUS,
            }

            audio_config_params = {
                "audio_encoding": audio_encoding_mapping.get(
                    audio_encoding.upper(), texttospeech.AudioEncoding.MP3
                ),
                "speaking_rate": speaking_rate,
                "pitch": pitch,
                "volume_gain_db": volume_gain_db,
            }

            audio_config = texttospeech.AudioConfig(**audio_config_params)

            # Perform the text-to-speech request
            response = self.tts_client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            # Encode audio content to base64
            audio_base64 = base64.b64encode(response.audio_content).decode("utf-8")
            audio_size = len(response.audio_content)

            # Estimate duration (rough calculation)
            # MP3 bitrate is typically around 128 kbps
            estimated_duration = None
            if audio_encoding.upper() == "MP3":
                estimated_duration = audio_size * 8 / (128 * 1000)  # seconds
            elif audio_encoding.upper() == "LINEAR16":
                # Assuming 24kHz sample rate for TTS
                estimated_duration = audio_size / (24000 * 2)  # seconds

            result = {
                "success": True,
                "audio_data": audio_base64,
                "audio_encoding": audio_encoding,
                "audio_size_bytes": audio_size,
                "audio_size_mb": round(audio_size / (1024 * 1024), 4),
                "estimated_duration_seconds": round(estimated_duration, 2)
                if estimated_duration
                else None,
                "voice_used": voice_name or f"{language_code}-{gender}",
                "language_code": language_code,
            }

            logger.info(
                "Text-to-speech conversion completed",
                audio_size_bytes=audio_size,
                estimated_duration=estimated_duration,
            )

            return result

        except Exception as e:
            logger.error("Text-to-speech conversion failed", error=str(e), text_length=len(text))
            return {
                "success": False,
                "audio_data": None,
                "audio_encoding": audio_encoding,
                "audio_size_bytes": 0,
                "audio_size_mb": 0.0,
                "estimated_duration_seconds": None,
                "voice_used": None,
                "language_code": language_code,
                "error": str(e),
            }

    async def get_available_voices(self, language_code: str | None = None) -> dict:
        """
        Get list of available voices for text-to-speech

        Args:
            language_code: Optional language code to filter voices

        Returns:
            Dictionary containing available voices information
        """
        try:
            logger.info("Fetching available voices", language_filter=language_code)

            # List available voices
            voices = self.tts_client.list_voices()

            voice_list = []
            languages_supported = set()

            for voice in voices.voices:
                # Filter by language if specified
                if language_code and not any(
                    lang.startswith(language_code[:2]) for lang in voice.language_codes
                ):
                    continue

                for lang_code in voice.language_codes:
                    languages_supported.add(lang_code)

                    voice_info = {
                        "name": voice.name,
                        "language_code": lang_code,
                        "gender": voice.ssml_gender.name,
                        "natural_sample_rate": voice.natural_sample_rate_hertz,
                    }
                    voice_list.append(voice_info)

            result = {
                "voices": voice_list,
                "total_voices": len(voice_list),
                "languages_supported": sorted(list(languages_supported)),
            }

            logger.info(
                "Available voices fetched",
                total_voices=len(voice_list),
                languages_count=len(languages_supported),
            )

            return result

        except Exception as e:
            logger.error("Failed to fetch available voices", error=str(e))
            return {
                "voices": [],
                "total_voices": 0,
                "languages_supported": [],
                "error": str(e),
            }


# Global service instance
speech_service = SpeechToTextService()
