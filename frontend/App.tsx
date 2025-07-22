import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import './global.css'; // Import global CSS for NativeWind
import {
  HomeScreen,
  CropHealthScreen,
  MarketPricesScreen,
  GovernmentSchemesScreen,
  VoiceChatScreen,
} from './src/screens';
import { RootStackParamList } from './src/types/navigation';

const Stack = createStackNavigator<RootStackParamList>();

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="dark" />
      <Stack.Navigator
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
          options={{ title: 'Crop Health Diagnosis' }}
        />
        <Stack.Screen
          name="MarketPrices"
          component={MarketPricesScreen}
          options={{ title: 'Market Prices' }}
        />
        <Stack.Screen
          name="GovernmentSchemes"
          component={GovernmentSchemesScreen}
          options={{ title: 'Government Schemes' }}
        />
        <Stack.Screen
          name="VoiceChat"
          component={VoiceChatScreen}
          options={{ title: 'Voice Chat Assistant' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
