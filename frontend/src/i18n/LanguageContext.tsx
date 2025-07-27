import React, { createContext, useContext, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { changeLanguage, getCurrentLanguage } from './index';
import { SUPPORTED_LANGUAGES } from '../config/languages';

interface LanguageContextType {
  currentLanguage: string;
  setLanguage: (language: string) => Promise<void>;
  isLoading: boolean;
  supportedLanguages: typeof SUPPORTED_LANGUAGES;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

interface LanguageProviderProps {
  children: React.ReactNode;
}

export const LanguageProvider: React.FC<LanguageProviderProps> = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState<string>('en');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const { i18n } = useTranslation();

  useEffect(() => {
    // Initialize language from i18n
    const initLanguage = () => {
      const lang = getCurrentLanguage();
      setCurrentLanguage(lang);
      setIsLoading(false);
    };

    // Listen for language changes
    const handleLanguageChange = (lng: string) => {
      setCurrentLanguage(lng);
    };

    i18n.on('languageChanged', handleLanguageChange);
    initLanguage();

    return () => {
      i18n.off('languageChanged', handleLanguageChange);
    };
  }, [i18n]);

  const setLanguage = async (language: string) => {
    try {
      setIsLoading(true);
      await changeLanguage(language);
      setCurrentLanguage(language);
    } catch (error) {
      console.error('Error changing language:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const value: LanguageContextType = {
    currentLanguage,
    setLanguage,
    isLoading,
    supportedLanguages: SUPPORTED_LANGUAGES,
  };

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
};

export const useLanguage = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
