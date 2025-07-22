import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';

interface FeatureCardProps {
  title: string;
  subtitle?: string;
  iconName: string; // MaterialCommunityIcons icon name
  onPress?: () => void;
}

export const FeatureCard: React.FC<FeatureCardProps> = ({
  title,
  subtitle,
  iconName,
  onPress,
}) => {
  return (
    <TouchableOpacity
      onPress={onPress}
      className="bg-card border border-border rounded-xl p-4 h-20 justify-center"
      activeOpacity={0.7}
    >
      <View className="flex-row items-center">
        {/* Icon */}
        <View className="w-10 h-10 mr-3 items-center justify-center bg-accent rounded-lg">
          <MaterialCommunityIcons
            name={iconName as any}
            size={24}
            color="#121b0d"
          />
        </View>

        {/* Text Content */}
        <View className="flex-1">
          <Text className="text-sm font-semibold text-foreground leading-tight">
            {title}
          </Text>
          {subtitle && (
            <Text className="text-xs text-foreground opacity-70 leading-tight">
              {subtitle}
            </Text>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );
}; 