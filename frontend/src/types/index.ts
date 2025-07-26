// API Response Types
export interface APIResponse<T = any> {
  data?: T;
  message: string;
  status: string;
  error?: string;
}

// Crop Diagnosis Types
export interface CropDiagnosisRequest {
  image: string; // base64 encoded image
  cropType?: string;
  location?: string;
}

export interface CropDiagnosisResponse {
  disease: string;
  confidence: number;
  treatment: string;
  prevention: string[];
  severity: 'low' | 'medium' | 'high';
}

// Voice Interface Types
export interface VoiceRequest {
  audioData: string; // base64 encoded audio
  language: 'kn-IN' | 'en-IN';
}

export interface VoiceResponse {
  transcription: string;
  intent?: string;
  response?: string;
}

// Voice Recording Component Types
export interface VoiceRecorderProps {
  onAudioRecorded: (base64Audio: string) => void;
  onRecordingStart?: () => void;
  onRecordingStop?: () => void;
  onError?: (error: string) => void;
  customStyles?: {
    container?: object;
    button?: object;
    buttonRecording?: object;
    text?: object;
    textRecording?: object;
  };
  buttonText?: string;
  recordingText?: string;
}

export interface RecordingState {
  isRecording: boolean;
  permissionStatus: 'granted' | 'denied' | 'undetermined';
  recording?: any; // expo-audio Recording object
}

// Market Price Types
export interface MarketPrice {
  commodity: string;
  price: number;
  unit: string;
  market: string;
  date: string;
  trend: 'up' | 'down' | 'stable';
}

export interface MarketPricesResponse {
  prices: MarketPrice[];
  lastUpdated: string;
}

// Navigation Types
export type RootStackParamList = {
  Home: undefined;
  CropDiagnosis: undefined;
  VoiceAssistant: undefined;
  MarketPrices: undefined;
  Profile: undefined;
};

// Component Props Types
export interface FeatureCardProps {
  title: string;
  description: string;
  icon: string;
  onPress?: () => void;
}
