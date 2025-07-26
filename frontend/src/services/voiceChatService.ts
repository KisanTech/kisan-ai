import { voiceChatApiClient } from './baseApiService';

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isAudio?: boolean;
  audioUrl?: string;
}

export interface VoiceQueryResponse {
  query_text: string;
  query_translation: string;
  response_text: string;
  response_translation: string;
  audio_response_url?: string;
}

export interface TextChatResponse {
  response_text: string;
  response_translation: string;
  audio_response_url?: string;
}

export interface SpeechToTextResponse {
  success: boolean;
  translated_text: string;
  original_transcript: string;
  detected_language: string;
  transcription_confidence: number;
  agent_response: string;
  agent_response_translated: string;
  response_audio_data: string;
  response_audio_encoding: string;
  response_audio_size_bytes: number;
  user_id: string;
  session_id: string;
  error: string | null;
  // Legacy properties for backward compatibility
  transcription?: string;
  translation?: string;
  confidence?: number;
  language?: string;
}

export class VoiceChatService {
  /**
   * Send text message to AI and get response
   */
  async sendTextMessage(message: string, language: string = 'en'): Promise<TextChatResponse> {
    try {
      const response = await voiceChatApiClient.post('/voice/text-chat', {
        message,
        language,
      });
      return response.data;
    } catch (error) {
      console.error('Text chat error:', error);
      // Return fallback response
      return {
        response_text:
          'I apologize, but I am currently experiencing technical difficulties. Please try again later.',
        response_translation:
          'ಕ್ಷಮಿಸಿ, ನಾನು ಪ್ರಸ್ತುತ ತಾಂತ್ರಿಕ ತೊಂದರೆಗಳನ್ನು ಅನುಭವಿಸುತ್ತಿದ್ದೇನೆ. ದಯವಿಟ್ಟು ನಂತರ ಪ್ರಯತ್ನಿಸಿ.',
      };
    }
  }

  /**
   * Send audio data to voice interface API using base64 encoding
   */
  async sendVoiceMessage(base64Audio: string, languageCode: string = 'kn-IN'): Promise<VoiceQueryResponse> {
    try {
      const response = await voiceChatApiClient.post('/voice/voice-query', {
        audio_data: base64Audio,
        audio_encoding: 'MP3',
        language_code: languageCode,
      });

      return response.data;
    } catch (error) {
      console.error('Voice message error:', error);
      // Return fallback response
      return {
        query_text: 'Audio not recognized',
        query_translation: 'ಆಡಿಯೋ ಗುರುತಿಸಲಾಗಿಲ್ಲ',
        response_text:
          'I apologize, but I could not understand your voice message. Please try speaking clearly or use text instead.',
        response_translation:
          'ಕ್ಷಮಿಸಿ, ನಿಮ್ಮ ಧ್ವನಿ ಸಂದೇಶವನ್ನು ನಾನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಸ್ಪಷ್ಟವಾಗಿ ಮಾತನಾಡಲು ಪ್ರಯತ್ನಿಸಿ ಅಥವಾ ಬದಲಿಗೆ ಪಠ್ಯವನ್ನು ಬಳಸಿ.',
      };
    }
  }

  /**
   * Convert speech to text using base64 audio data
   */
  async speechToText(base64Audio: string, languageCode: string = 'hi-IN'): Promise<SpeechToTextResponse> {
    try {
      console.log('Speech to text request received', base64Audio);
      const response = await voiceChatApiClient.post('/invoke/voice', {
        audio_data: base64Audio,
        audio_encoding: 'MP3',
        language_code: languageCode,
        user_id: '123',
        session_id: '123',
      });
      console.log('Speech to text response:', response.data);
      
      // Return the full response from the API
      const apiResponse = response.data;
      return {
        success: apiResponse.success || false,
        translated_text: apiResponse.translated_text || '',
        original_transcript: apiResponse.original_transcript || '',
        detected_language: apiResponse.detected_language || languageCode,
        transcription_confidence: apiResponse.transcription_confidence || 0,
        agent_response: apiResponse.agent_response || '',
        agent_response_translated: apiResponse.agent_response_translated || '',
        response_audio_data: apiResponse.response_audio_data || '',
        response_audio_encoding: apiResponse.response_audio_encoding || 'MP3',
        response_audio_size_bytes: apiResponse.response_audio_size_bytes || 0,
        user_id: apiResponse.user_id || '123',
        session_id: apiResponse.session_id || '123',
        error: apiResponse.error || null,
        // Legacy properties for backward compatibility
        transcription: apiResponse.original_transcript || apiResponse.transcription || '',
        translation: apiResponse.translated_text || apiResponse.translation || '',
        confidence: apiResponse.transcription_confidence || apiResponse.confidence || 0,
        language: apiResponse.detected_language || apiResponse.language || languageCode,
      };
    } catch (error) {
      console.error('Speech to text error:', error);
      throw error;
    }
  }
}

export const voiceChatService = new VoiceChatService();
