export interface Language {
  id: string;
  name: string;
  nativeName: string;
  icon?: string; // Optional flag icon
  speechRecognitionCode: string; // Language code for speech recognition APIs
  textApiCode: string; // Language code for text/chat APIs
}

export const SUPPORTED_LANGUAGES: Language[] = [
  {
    id: 'en',
    name: 'English',
    nativeName: 'English',
    speechRecognitionCode: 'en-IN',
    textApiCode: 'en',
  },
  {
    id: 'kn',
    name: 'Kannada',
    nativeName: 'ಕನ್ನಡ',
    speechRecognitionCode: 'kn-IN',
    textApiCode: 'kn',
  },
  {
    id: 'hi',
    name: 'Hindi',
    nativeName: 'हिंदी',
    speechRecognitionCode: 'hi-IN',
    textApiCode: 'hi',
  },
  {
    id: 'od',
    name: 'Odia',
    nativeName: 'ଓଡ଼ିଆ',
    speechRecognitionCode: 'hi-IN', // Fallback to Hindi for Odia since Odia speech recognition might not be available
    textApiCode: 'od',
  },
];

// Helper functions to get language codes
export const getSpeechRecognitionCode = (languageId: string): string => {
  const language = SUPPORTED_LANGUAGES.find(lang => lang.id === languageId);
  return language?.speechRecognitionCode || 'en-US';
};

export const getTextApiCode = (languageId: string): string => {
  const language = SUPPORTED_LANGUAGES.find(lang => lang.id === languageId);
  return language?.textApiCode || 'en';
};
