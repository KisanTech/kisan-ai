// Import services for default export
import { baseApiClient } from './baseApiService';
import { diagnosisService } from './diagnosisService';
import { voiceChatService } from './voiceChatService';

// Re-export base API service
export { baseApiClient, API_BASE_URL, createBaseApiClient } from './baseApiService';

// Re-export diagnosis service
export { diagnosisService, DiagnosisService } from './diagnosisService';
export type { DiagnosisRequest, DiagnosisResponse } from './diagnosisService';

// Re-export voice chat service
export { voiceChatService, VoiceChatService } from './voiceChatService';
export type {
  ChatMessage,
  VoiceQueryResponse,
  TextChatResponse,
  SpeechToTextResponse,
} from './voiceChatService';

// Legacy API Endpoints (kept for backward compatibility)
export const API_ENDPOINTS = {
  // Crop Diagnosis
  CROP_DIAGNOSE: '/crop/diagnose',

  // Voice Interface
  SPEECH_TO_TEXT: '/voice/speech-to-text',
  TEXT_TO_SPEECH: '/voice/text-to-speech',
  VOICE_QUERY: '/voice/voice-query',
  TEXT_CHAT: '/voice/text-chat',

  // Market Prices
  MARKET_CURRENT: '/market/current',
  MARKET_HISTORY: '/market/history',

  // Health Check
  HEALTH: '/health',
} as const;

// Default export for backward compatibility
export default {
  baseApiClient,
  diagnosisService,
  voiceChatService,
};
