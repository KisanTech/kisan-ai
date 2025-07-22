import { RootStackParamList } from '../types/navigation';

// Feature card configuration
export interface FeatureConfig {
    id: string;
    title: string;
    subtitle?: string; // Made optional since you removed it
    iconName: string; // MaterialCommunityIcons icon name
    screen: keyof RootStackParamList;
}

// Quick action button configuration
export interface QuickActionConfig {
    id: string;
    title: string;
    action: string;
}

// Tab configuration
export interface TabConfig {
    id: string;
    title: string;
    iconName: string; // MaterialCommunityIcons icon name
}

// App features configuration
export const FEATURES: FeatureConfig[] = [
    {
        id: 'crop-health',
        title: 'Crop Health Diagnosis',
        iconName: 'leaf',
        screen: 'CropHealth',
    },
    {
        id: 'market-prices',
        title: 'Market Prices',
        iconName: 'chart-line',
        screen: 'MarketPrices',
    },
    {
        id: 'govt-schemes',
        title: 'Government Schemes',
        iconName: 'account-tie',
        screen: 'GovernmentSchemes',
    },
    {
        id: 'voice-chat',
        title: 'Voice Chat Assistant',
        iconName: 'microphone',
        screen: 'VoiceChat',
    },
    {
        id: 'farm-analytics',
        title: 'My Farm Analytics',
        iconName: 'chart-box',
        screen: 'Home', // Placeholder - not implemented yet
    },
    {
        id: 'alerts',
        title: 'Alerts & Reminders',
        iconName: 'bell',
        screen: 'Home', // Placeholder - not implemented yet
    },
];

// Quick actions configuration
export const QUICK_ACTIONS: QuickActionConfig[] = [
    {
        id: 'crop-prices',
        title: 'Check Crop Prices',
        action: 'crop-prices',
    },
    {
        id: 'crop-health',
        title: 'Assess Crop Health',
        action: 'crop-health',
    },
];

// Bottom tab configuration
export const TABS: TabConfig[] = [
    { id: 'home', title: 'Home', iconName: 'home-outline' },
    { id: 'community', title: 'Community', iconName: 'account-group-outline' },
    { id: 'profile', title: 'Profile', iconName: 'account-outline' },
];

// App text configuration
export const APP_TEXT = {
    appTitle: 'Kisan',
    sections: {
        features: 'Features',
        quickActions: 'Quick Actions',
    },
    screens: {
        cropHealth: 'Crop Health Diagnosis',
        marketPrices: 'Market Prices',
        governmentSchemes: 'Government Schemes',
        voiceChat: 'Voice Chat Assistant',
    },
}; 