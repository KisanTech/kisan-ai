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

  const textStyles = variant === 'primary' ? 'text-white font-semibold' : 'text-foreground';

  return (
    <TouchableOpacity
      onPress={onPress}
      className={`w-full py-4 px-6 rounded-xl mb-3 ${buttonStyles}`}
      activeOpacity={0.8}
    >
      <Text className={`text-center ${textStyles}`}>{title}</Text>
    </TouchableOpacity>
  );
};
