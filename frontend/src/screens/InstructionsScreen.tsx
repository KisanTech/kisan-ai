import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { useTranslation } from 'react-i18next';
import { Ionicons } from '@expo/vector-icons';
import { RootStackParamList } from '../types/navigation';
import { NavigateBackButton } from '../components';

type NavigationProp = StackNavigationProp<RootStackParamList>;

interface AccordionItemProps {
  title: string;
  icon: keyof typeof Ionicons.glyphMap;
  iconColor: string;
  bgColor: string;
  instructions: string[];
  isOpen: boolean;
  onToggle: () => void;
}

const AccordionItem: React.FC<AccordionItemProps> = ({
  title,
  icon,
  iconColor,
  bgColor,
  instructions,
  isOpen,
  onToggle,
}) => {
  return (
    <View
      className="mb-4 bg-white rounded-xl shadow-sm"
      style={{
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
      }}
    >
      <TouchableOpacity onPress={onToggle} className="p-4">
        <View className="flex-row items-center justify-between">
          <View className="flex-row items-center flex-1">
            <View className={`w-12 h-12 ${bgColor} rounded-full items-center justify-center mr-4`}>
              <Ionicons name={icon} size={24} className={iconColor} />
            </View>
            <Text className="text-lg font-bold text-foreground flex-1">{title}</Text>
          </View>
          <Ionicons name={isOpen ? 'chevron-up' : 'chevron-down'} size={24} color="#6B7280" />
        </View>
      </TouchableOpacity>

      {isOpen && (
        <View className="px-4 pb-4">
          <View className="border-t border-gray-100 pt-4">
            {instructions.map((instruction, index) => (
              <View key={index} className="flex-row items-start mb-3">
                <View className="w-6 h-6 bg-primary rounded-full items-center justify-center mr-3 mt-0.5">
                  <Text className="text-white text-xs font-bold">{index + 1}</Text>
                </View>
                <Text className="text-sm text-gray-700 flex-1 leading-5">{instruction}</Text>
              </View>
            ))}
          </View>
        </View>
      )}
    </View>
  );
};

export const InstructionsScreen: React.FC = () => {
  const navigation = useNavigation<NavigationProp>();
  const { t } = useTranslation();
  const [openAccordion, setOpenAccordion] = useState<string | null>(null);

  const handleAccordionToggle = (id: string) => {
    setOpenAccordion(openAccordion === id ? null : id);
  };

  const instructionsData = [
    {
      id: 'crop-health',
      title: t('instructions.cropHealth.title'),
      icon: 'leaf' as keyof typeof Ionicons.glyphMap,
      iconColor: 'text-green-600',
      bgColor: 'bg-green-100',
      instructions: [
        t('instructions.cropHealth.step1'),
        t('instructions.cropHealth.step2'),
        t('instructions.cropHealth.step3'),
        t('instructions.cropHealth.step4'),
        t('instructions.cropHealth.step5'),
        t('instructions.cropHealth.step6'),
      ],
    },
    {
      id: 'market-prices',
      title: t('instructions.marketPrices.title'),
      icon: 'trending-up' as keyof typeof Ionicons.glyphMap,
      iconColor: 'text-blue-600',
      bgColor: 'bg-blue-100',
      instructions: [
        t('instructions.marketPrices.step1'),
        t('instructions.marketPrices.step2'),
        t('instructions.marketPrices.step3'),
        t('instructions.marketPrices.step4'),
        t('instructions.marketPrices.step5'),
      ],
    },
    {
      id: 'gov-schemes',
      title: t('instructions.govSchemes.title'),
      icon: 'people' as keyof typeof Ionicons.glyphMap,
      iconColor: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
      instructions: [
        t('instructions.govSchemes.step1'),
        t('instructions.govSchemes.step2'),
        t('instructions.govSchemes.step3'),
        t('instructions.govSchemes.step4'),
        t('instructions.govSchemes.step5'),
      ],
    },
    {
      id: 'voice-chat',
      title: t('instructions.voiceChat.title'),
      icon: 'mic' as keyof typeof Ionicons.glyphMap,
      iconColor: 'text-purple-600',
      bgColor: 'bg-purple-100',
      instructions: [
        t('instructions.voiceChat.step1'),
        t('instructions.voiceChat.step2'),
        t('instructions.voiceChat.step3'),
        t('instructions.voiceChat.step4'),
        t('instructions.voiceChat.step5'),
      ],
    },
  ];

  return (
    <SafeAreaView className="flex-1 bg-background font-sans">
      {/* Header */}
      <View className="flex-row items-center p-4 bg-white border-b border-gray-100">
        <NavigateBackButton navigation={navigation} />
        <Text className="text-xl font-bold text-foreground ml-3">{t('instructions.title')}</Text>
      </View>

      <ScrollView className="flex-1 p-4">
        {/* Description */}
        <View className="mb-6">
          <Text className="text-gray-600 text-center leading-6">{t('instructions.subtitle')}</Text>
        </View>

        {/* Accordions */}
        {instructionsData.map(item => (
          <AccordionItem
            key={item.id}
            title={item.title}
            icon={item.icon}
            iconColor={item.iconColor}
            bgColor={item.bgColor}
            instructions={item.instructions}
            isOpen={openAccordion === item.id}
            onToggle={() => handleAccordionToggle(item.id)}
          />
        ))}

        {/* Bottom spacing */}
        <View className="h-8" />
      </ScrollView>
    </SafeAreaView>
  );
};
