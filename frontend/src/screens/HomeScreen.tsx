import React, { useState, useCallback } from 'react';
import { View, Text, ScrollView, SafeAreaView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { Header, FeatureCard, QuickActionButton, BottomTabBar } from '../components';
import { RootStackParamList } from '../types/navigation';
import { FEATURES, QUICK_ACTIONS, APP_TEXT, FeatureConfig } from '../config/app';

type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Home'>;



export const HomeScreen: React.FC = () => {
    const navigation = useNavigation<HomeScreenNavigationProp>();
    const [activeTab, setActiveTab] = useState('home');
    const [currentLanguage, setCurrentLanguage] = useState('en');

    // Generic handlers using useCallback for optimization
    const handleMicPress = useCallback(() => {
        console.log('Voice assistant activated');
        // TODO: Implement voice assistant functionality
    }, []);

    const handleFeaturePress = useCallback((feature: FeatureConfig) => {
        if (feature.screen === 'Home') {
            console.log(`Feature not implemented: ${feature.id}`);
        } else {
            navigation.navigate(feature.screen);
        }
    }, [navigation]);

    const handleQuickAction = useCallback((actionId: string) => {
        const action = QUICK_ACTIONS.find(qa => qa.id === actionId);
        if (action) {
            console.log(`Quick action: ${action.action}`);
            // TODO: Implement specific quick action functionality
        }
    }, []);

    const handleTabPress = useCallback((tabId: string) => {
        setActiveTab(tabId);
        console.log(`Tab pressed: ${tabId}`);
        // TODO: Implement tab navigation
    }, []);

    return (
        <SafeAreaView className="flex-1 bg-background font-sans">
            {/* Header */}
            <Header
                title={APP_TEXT.appTitle}
                currentLanguage={currentLanguage}
                onLanguageChange={setCurrentLanguage}
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
                        {APP_TEXT.sections.features}
                    </Text>

                    {/* Features Grid */}
                    <View className="flex-row flex-wrap justify-between">
                        {FEATURES.map((feature) => (
                            <View key={feature.id} style={{ width: '48%' }} className="mb-3">
                                <FeatureCard
                                    title={feature.title}
                                    subtitle={feature.subtitle}
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
                        {APP_TEXT.sections.quickActions}
                    </Text>

                    {QUICK_ACTIONS.map((action) => (
                        <QuickActionButton
                            key={action.id}
                            title={action.title}
                            onPress={() => handleQuickAction(action.id)}
                        />
                    ))}
                </View>
            </ScrollView>

            {/* Bottom Tab Bar */}
            <BottomTabBar
                activeTab={activeTab}
                onTabPress={handleTabPress}
            />
        </SafeAreaView>
    );
}; 