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
    id: 'farm-analytics',
    titleKey: 'home.features.farmAnalytics.title',
    subtitleKey: 'home.features.farmAnalytics.subtitle',
    iconName: 'chart-box',
    screen: 'Home', // Placeholder
  },
  {
    id: 'alerts',
    titleKey: 'home.features.alerts.title',
    subtitleKey: 'home.features.alerts.subtitle',
    iconName: 'bell',
    screen: 'Home', // Placeholder
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

          {/* Features Grid */}
          <View className="flex-row flex-wrap justify-between">
            {FEATURES.map(feature => (
              <View key={feature.id} style={{ width: '48%' }} className="mb-3">
                <FeatureCard
                  title={t(feature.titleKey)}
                  subtitle={t(feature.subtitleKey)}
                  iconName={feature.iconName}
                  onPress={() => handleFeaturePress(feature)}
                />
              </View>
            ))}
          </View>
        </View>

        {/* Quick Actions Section */}
        <View className="px-6">
          <Text className="text-lg font-bold text-foreground mb-4 tracking-tighter">
            {t('home.sections.quickActions')}
          </Text>

          {QUICK_ACTIONS.map(action => (
            <QuickActionButton
              key={action.id}
              title={t(action.titleKey)}
              onPress={() => handleQuickAction(action.id)}
            />
          ))}
        </View>
      </ScrollView>

      {/* Bottom Tab Bar */}
      <BottomTabBar activeTab={activeTab} onTabPress={handleTabPress} />
    </SafeAreaView>
  );
};
