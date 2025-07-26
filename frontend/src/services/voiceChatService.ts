import { baseApiClient } from './baseApiService';

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
  transcription: string;
  translation: string;
  confidence: number;
  language: string;
}

export class VoiceChatService {
  /**
   * Send text message to AI and get response
   */
  async sendTextMessage(message: string, language: string = 'en'): Promise<TextChatResponse> {
    try {
      const response = await baseApiClient.post('/voice/text-chat', {
        message,
        language,
      });
      return response.data;
    } catch (error) {
      console.error('Text chat error:', error);
      // Return fallback response
      return {
        response_text: 'I apologize, but I am currently experiencing technical difficulties. Please try again later.',
        response_translation: 'ಕ್ಷಮಿಸಿ, ನಾನು ಪ್ರಸ್ತುತ ತಾಂತ್ರಿಕ ತೊಂದರೆಗಳನ್ನು ಅನುಭವಿಸುತ್ತಿದ್ದೇನೆ. ದಯವಿಟ್ಟು ನಂತರ ಪ್ರಯತ್ನಿಸಿ.',
      };
    }
  }

  /**
   * Send audio file to voice interface API
   */
  async sendVoiceMessage(audioUri: string): Promise<VoiceQueryResponse> {
    try {
      const formData = new FormData();
      formData.append('audio', {
        uri: audioUri,
        type: 'audio/pcm',
        name: 'voice_message.pcm',
      } as any);

      const response = await baseApiClient.post('/voice/voice-query', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      console.error('Voice message error:', error);
      // Return fallback response
      return {
        query_text: 'Audio not recognized',
        query_translation: 'ಆಡಿಯೋ ಗುರುತಿಸಲಾಗಿಲ್ಲ',
        response_text: 'I apologize, but I could not understand your voice message. Please try speaking clearly or use text instead.',
        response_translation: 'ಕ್ಷಮಿಸಿ, ನಿಮ್ಮ ಧ್ವನಿ ಸಂದೇಶವನ್ನು ನಾನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಸ್ಪಷ್ಟವಾಗಿ ಮಾತನಾಡಲು ಪ್ರಯತ್ನಿಸಿ ಅಥವಾ ಬದಲಿಗೆ ಪಠ್ಯವನ್ನು ಬಳಸಿ.',
      };
    }
  }

  /**
   * Convert speech to text
   */
  async speechToText(audioUri: string): Promise<SpeechToTextResponse> {
    try {
      const formData = new FormData();
      formData.append('audio', {
        uri: audioUri,
        type: 'audio/pcm',
        name: 'speech.pcm',
      } as any);

      const response = await baseApiClient.post('/voice/speech-to-text', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      console.error('Speech to text error:', error);
      throw error;
    }
  }
}

export const voiceChatService = new VoiceChatService(); 