import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { useTranslation } from 'react-i18next';
import './global.css'; // Import global CSS for NativeWind
import './src/i18n'; // Initialize i18n
import { LanguageProvider } from './src/i18n/LanguageContext';
import {
  HomeScreen,
  CropHealthScreen,
  DiagnosisResultScreen,
  MarketPricesScreen,
  GovernmentSchemesScreen,
  VoiceChatScreen,
} from './src/screens';
import { NavigateBackButton } from './src/components';
import { RootStackParamList } from './src/types/navigation';

const Stack = createStackNavigator<RootStackParamList>();

const AppNavigator: React.FC = () => {
  const { t } = useTranslation();

  return (
    <NavigationContainer>
      <StatusBar style="dark" />
      <Stack.Navigator
        id={undefined}
        initialRouteName="Home"
        screenOptions={{
          headerStyle: {
            backgroundColor: '#ffffff',
          },
          headerTintColor: '#121b0d',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        <Stack.Screen name="Home" component={HomeScreen} options={{ headerShown: false }} />
        <Stack.Screen
          name="CropHealth"
          component={CropHealthScreen}
          options={({ navigation }) => ({
            title: t('cropHealth.title'),
            headerLeft: () => <NavigateBackButton navigation={navigation} />,
          })}
        />
        <Stack.Screen
          name="MarketPrices"
          component={MarketPricesScreen}
          options={({ navigation }) => ({
            title: t('marketPrices.title'),
            headerLeft: () => <NavigateBackButton navigation={navigation} />,
          })}
        />
        <Stack.Screen
          name="GovernmentSchemes"
          component={GovernmentSchemesScreen}
          options={({ navigation }) => ({
            title: t('governmentSchemes.title'),
            headerLeft: () => <NavigateBackButton navigation={navigation} />,
          })}
        />
        <Stack.Screen
          name="DiagnosisResult"
          component={DiagnosisResultScreen}
          options={({ navigation }) => ({
            title: t('diagnosisResult.title'),
            headerLeft: () => <NavigateBackButton navigation={navigation} />,
          })}
        />
        <Stack.Screen
          name="VoiceChat"
          component={VoiceChatScreen}
          options={{ headerShown: false }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default function App() {
  return (
    <LanguageProvider>
      <AppNavigator />
    </LanguageProvider>
  );
}
