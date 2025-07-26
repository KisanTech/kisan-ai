import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Import translation files
import en from './locales/en.json';
import kn from './locales/kn.json';
import hi from './locales/hi.json';
import od from './locales/od.json';

const LANGUAGE_STORAGE_KEY = '@kisan_app_language';

// Language detection and storage
const languageDetector = {
  type: 'languageDetector' as const,
  async: true,
  detect: async (callback: (lng: string) => void) => {
    try {
      // Try to get stored language
      const storedLanguage = await AsyncStorage.getItem(LANGUAGE_STORAGE_KEY);
      if (storedLanguage) {
        callback(storedLanguage);
        return;
      }
    } catch (error) {
      console.log('Error reading language from storage:', error);
    }
    
    // Default to English
    callback('en');
  },
  init: () => {},
  cacheUserLanguage: async (lng: string) => {
    try {
      await AsyncStorage.setItem(LANGUAGE_STORAGE_KEY, lng);
    } catch (error) {
      console.log('Error storing language:', error);
    }
  },
};

const initOptions = {
  resources: {
    en: { translation: en },
    kn: { translation: kn },
    hi: { translation: hi },
    od: { translation: od },
  },
  fallbackLng: 'en',
  debug: __DEV__,
  interpolation: {
    escapeValue: false, // React already escapes values
  },
  react: {
    useSuspense: false, // Important for React Native
  },
  compatibilityJSON: 'v4' as const, // For React Native compatibility
};

i18n
  .use(languageDetector)
  .use(initReactI18next)
  .init(initOptions);

export default i18n;

// Helper function to change language
export const changeLanguage = async (languageCode: string) => {
  try {
    await i18n.changeLanguage(languageCode);
    await AsyncStorage.setItem(LANGUAGE_STORAGE_KEY, languageCode);
  } catch (error) {
    console.log('Error changing language:', error);
  }
};

// Helper function to get current language
export const getCurrentLanguage = () => i18n.language;

// Helper function to get all available languages
export const getAvailableLanguages = () => Object.keys(i18n.services.resourceStore.data); 