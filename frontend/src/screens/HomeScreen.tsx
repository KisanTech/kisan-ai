import React, { useState, useCallback } from 'react';
import { View, Text, ScrollView, SafeAreaView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { useTranslation } from 'react-i18next';
import { Header, FeatureCard, QuickActionButton, BottomTabBar } from '../components';
import { RootStackParamList } from '../types/navigation';
import { useLanguage } from '../i18n/LanguageContext';

type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Home'>;

// Define feature configuration locally with translation keys
interface FeatureConfig {
  id: string;
  titleKey: string;
  subtitleKey: string;
  iconName: string;
  screen: keyof RootStackParamList;
}

const FEATURES: FeatureConfig[] = [
  {
    id: 'crop-health',
    titleKey: 'home.features.cropHealth.title',
    subtitleKey: 'home.features.cropHealth.subtitle',
    iconName: 'leaf',
    screen: 'CropHealth',
  },
  {
    id: 'market-prices',
    titleKey: 'home.features.marketPrices.title',
    subtitleKey: 'home.features.marketPrices.subtitle',
    iconName: 'chart-line',
    screen: 'MarketPrices',
  },
  {
    id: 'govt-schemes',
    titleKey: 'home.features.govSchemes.title',
    subtitleKey: 'home.features.govSchemes.subtitle',
    iconName: 'account-tie',
    screen: 'GovernmentSchemes',
  },
  {
    id: 'voice-chat',
    titleKey: 'home.features.voiceChat.title',
    subtitleKey: 'home.features.voiceChat.subtitle',
    iconName: 'microphone',
    screen: 'VoiceChat',
  },
  {
    id: 'instructions',
    titleKey: 'home.features.instructions.title',
    subtitleKey: 'home.features.instructions.subtitle',
    iconName: 'help-circle',
    screen: 'Instructions',
  },
];

const QUICK_ACTIONS = [
  {
    id: 'crop-prices',
    titleKey: 'home.quickActions.checkCropPrices',
    action: 'crop-prices',
  },
  {
    id: 'crop-health',
    titleKey: 'home.quickActions.assessCropHealth',
    action: 'crop-health',
  },
];

export const HomeScreen: React.FC = () => {
  const navigation = useNavigation<HomeScreenNavigationProp>();
  const [activeTab, setActiveTab] = useState('home');
  const { t } = useTranslation();
  const { currentLanguage, setLanguage } = useLanguage();

  const handleFeaturePress = useCallback(
    (feature: FeatureConfig) => {
      if (feature.screen === 'Home') {
        console.log(`Feature not implemented: ${feature.id}`);
      } else {
        navigation.navigate(feature.screen);
      }
    },
    [navigation]
  );

  const handleQuickAction = useCallback(
    (actionId: string) => {
      console.log(`Quick action: ${actionId}`);

      switch (actionId) {
        case 'crop-health':
          navigation.navigate('CropHealth');
          break;
        case 'crop-prices':
          navigation.navigate('MarketPrices');
          break;
        default:
          console.log(`Quick action not implemented: ${actionId}`);
      }
    },
    [navigation]
  );

  const handleTabPress = useCallback((tabId: string) => {
    setActiveTab(tabId);
    console.log(`Tab pressed: ${tabId}`);
    // TODO: Implement tab navigation
  }, []);

  return (
    <SafeAreaView className="flex-1 bg-background font-sans">
      {/* Header */}
      <Header
        title={t('header.title')}
        currentLanguage={currentLanguage}
        onLanguageChange={setLanguage}
      />

      {/* Main Content */}
      <ScrollView
        className="flex-1"
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: 20 }}
      >
        {/* Features Section */}
        <View className="px-6 py-6">
          <Text className="text-lg font-bold text-foreground mb-4 tracking-tighter">
            {t('home.sections.features')}
          </Text>

          {/* Features List - Single Column */}
          <View style={{ gap: 20 }}>
            {FEATURES.map(feature => (
              <FeatureCard
                key={feature.id}
                title={t(feature.titleKey)}
                subtitle={t(feature.subtitleKey)}
                iconName={feature.iconName}
                onPress={() => handleFeaturePress(feature)}
              />
            ))}
          </View>
        </View>

        {/* Quick Actions Section */}
        <View className="px-6 mt-6">
          <Text className="text-lg font-bold text-foreground mb-6 tracking-tighter">
            {t('home.sections.quickActions')}
          </Text>

          {/* Quick Actions - 2 Buttons Per Row */}
          <View className="flex-row" style={{ gap: 24 }}>
            {QUICK_ACTIONS.map(action => (
              <View key={action.id} className="flex-1">
                <QuickActionButton
                  title={t(action.titleKey)}
                  onPress={() => handleQuickAction(action.id)}
                />
              </View>
            ))}
          </View>
        </View>
      </ScrollView>

      {/* Bottom Tab Bar */}
      <BottomTabBar activeTab={activeTab} onTabPress={handleTabPress} />
    </SafeAreaView>
  );
};
