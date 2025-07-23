import React from 'react';
import { TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface NavigateBackButtonProps {
  navigation: any;
  color?: string;
  size?: number;
}

export const NavigateBackButton: React.FC<NavigateBackButtonProps> = ({
  navigation,
  color = '#121b0d',
  size = 24,
}) => {
  return (
    <TouchableOpacity onPress={() => navigation.goBack()} className="ml-4 p-2" activeOpacity={0.7}>
      <Ionicons name="arrow-back" size={size} color={color} />
    </TouchableOpacity>
  );
};
