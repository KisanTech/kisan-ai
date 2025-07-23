import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import './global.css'; // Import global CSS for NativeWind
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

export default function App() {
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
            title: 'Crop Health Diagnosis',
            headerLeft: () => <NavigateBackButton navigation={navigation} />,
          })}
        />
        <Stack.Screen
          name="MarketPrices"
          component={MarketPricesScreen}
          options={({ navigation }) => ({
            title: 'Market Prices',
            headerLeft: () => <NavigateBackButton navigation={navigation} />,
          })}
        />
        <Stack.Screen
          name="GovernmentSchemes"
          component={GovernmentSchemesScreen}
          options={({ navigation }) => ({
            title: 'Government Schemes',
            headerLeft: () => <NavigateBackButton navigation={navigation} />,
          })}
        />
        <Stack.Screen
          name="VoiceChat"
          component={VoiceChatScreen}
          options={({ navigation }) => ({
            title: 'Voice Chat Assistant',
            headerLeft: () => <NavigateBackButton navigation={navigation} />,
          })}
        />
        <Stack.Screen
          name="DiagnosisResult"
          component={DiagnosisResultScreen}
          options={({ navigation }) => ({
            title: 'Diagnosis Results',
            headerLeft: () => <NavigateBackButton navigation={navigation} />,
          })}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
