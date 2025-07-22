import React from 'react';
import { View, Text, Image, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../../types/navigation';
import { DiagnosisResponse } from '../../services/diagnosisService';
import { NavigateBackButton } from '../../components';

interface RouteParams {
  diagnosis: DiagnosisResponse;
  imageUri: string;
}

type NavigationProp = StackNavigationProp<RootStackParamList>;

export const DiagnosisResultScreen: React.FC = () => {
  const navigation = useNavigation<NavigationProp>();
  const route = useRoute();
  const { diagnosis, imageUri } = route.params as RouteParams;

  const handleCallExpert = () => {
    // TODO: Implement call expert functionality
    console.log('Call expert');
  };

  const handleGetSecondOpinion = () => {
    // TODO: Implement second opinion functionality
    console.log('Get second opinion');
  };

  const handleSaveReport = () => {
    // TODO: Implement save report functionality
    console.log('Save report');
  };

  return (
    <SafeAreaView className="flex-1 bg-card font-sans">
      <ScrollView className="flex-1">
        {/* Image Preview */}
        {imageUri && (
          <Image
            source={{ uri: imageUri }}
            className="w-full h-60 bg-gray-100"
            resizeMode="cover"
          />
        )}

        {/* Disease Detection Result */}
        <View className="p-4">
          <Text className="text-3xl font-bold mb-1 text-foreground tracking-tighter">
            {diagnosis.diagnosis.disease_name}
          </Text>
          <Text className="text-xl text-secondary mb-6">
            ({(diagnosis.diagnosis.confidence * 100).toFixed(0)}% Confidence)
          </Text>

          {/* Treatment Section */}
          <Text className="text-2xl font-bold mb-4 text-foreground tracking-tighter">
            Recommended Treatment
          </Text>
          <Text className="text-base leading-6 text-foreground mb-6">
            {diagnosis.treatment.immediate_action}
            {'\n\n'}• Apply '{diagnosis.treatment.recommended_fungicide}' as directed
            {'\n'}• {diagnosis.treatment.application_frequency}
          </Text>

          {/* Available Suppliers */}
          <Text className="text-2xl font-bold mb-4 text-foreground tracking-tighter">
            Available at
          </Text>
          {diagnosis.local_suppliers.map((supplier, index) => (
            <View
              key={index}
              className="flex-row justify-between items-center mb-4 border-b border-border pb-2"
            >
              <View>
                <Text className="text-lg font-medium text-foreground">{supplier.name}</Text>
                <Text className="text-primary">{supplier.distance}</Text>
              </View>
              <Text className="text-xl font-semibold text-foreground">${25}</Text>
            </View>
          ))}
        </View>
      </ScrollView>

      {/* Bottom Action Buttons */}
      <View className="p-4 bg-background">
        {/* Expert and Second Opinion */}
        <View className="flex-row justify-between mb-4">
          <TouchableOpacity
            onPress={handleCallExpert}
            className="bg-card py-3 px-6 rounded-lg border border-border"
          >
            <Text className="font-medium text-foreground">Call Expert</Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={handleGetSecondOpinion}
            className="bg-card py-3 px-6 rounded-lg border border-border"
          >
            <Text className="font-medium text-foreground">Get Second Opinion</Text>
          </TouchableOpacity>
        </View>

        {/* Save Report Button */}
        <TouchableOpacity onPress={handleSaveReport} className="bg-primary py-4 rounded-xl">
          <Text className="text-card font-bold text-center text-lg tracking-tighter">
            Save Report
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};
