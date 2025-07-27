import React from 'react';
import { Text, TouchableOpacity } from 'react-native';

interface QuickActionButtonProps {
  title: string;
  onPress?: () => void;
  variant?: 'primary' | 'secondary';
}

export const QuickActionButton: React.FC<QuickActionButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
}) => {
  const buttonStyles = variant === 'primary' ? 'bg-primary' : 'bg-card border border-border';

  const textStyles = variant === 'primary' ? 'text-white font-bold' : 'text-foreground';

  return (
    <TouchableOpacity
      onPress={onPress}
      className={`w-full py-4 px-4 rounded-xl ${buttonStyles}`}
      activeOpacity={0.8}
    >
      <Text className={`text-center text-sm ${textStyles}`}>{title}</Text>
    </TouchableOpacity>
  );
};
