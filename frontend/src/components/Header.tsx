import React from 'react';
import { View, Text } from 'react-native';
import { LanguageSelector } from './LanguageSelector';

interface HeaderProps {
  title: string;
  currentLanguage: string;
  onLanguageChange: (languageId: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ title, currentLanguage, onLanguageChange }) => {
  return (
    <View className="flex-row justify-between items-center px-6 py-4 bg-card">
      <Text className="text-2xl font-bold text-foreground tracking-tighter">{title}</Text>

      <LanguageSelector currentLanguage={currentLanguage} onLanguageChange={onLanguageChange} />
    </View>
  );
};
