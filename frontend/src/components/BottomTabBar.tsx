import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { TABS } from '../config/app';

interface BottomTabBarProps {
  activeTab: string;
  onTabPress: (tabId: string) => void;
}

export const BottomTabBar: React.FC<BottomTabBarProps> = ({ activeTab, onTabPress }) => {
  return (
    <View className="flex-row bg-card border-t border-muted">
      {TABS.map(tab => (
        <TouchableOpacity
          key={tab.id}
          onPress={() => onTabPress(tab.id)}
          className="flex-1 items-center py-3"
          activeOpacity={0.7}
        >
          <MaterialCommunityIcons
            name={tab.iconName as any}
            size={24}
            color={activeTab === tab.id ? '#669a4c' : '#121b0d50'}
          />
          <Text
            className={`text-xs font-medium ${
              activeTab === tab.id ? 'text-secondary' : 'text-foreground opacity-50'
            }`}
          >
            {tab.title}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );
};
