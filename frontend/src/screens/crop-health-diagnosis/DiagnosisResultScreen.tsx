import React from 'react';
import { View, Text, Image, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../../types/navigation';
import { Ionicons } from '@expo/vector-icons';

interface RouteParams {
  diagnosis: any; // Agent API response (parsed JSON)
  imageUri: string;
}

type NavigationProp = StackNavigationProp<RootStackParamList>;

export const DiagnosisResultScreen: React.FC = () => {
  const navigation = useNavigation<NavigationProp>();
  const route = useRoute();
  const { diagnosis, imageUri } = route.params as RouteParams;

  const handleCallExpert = () => {
    console.log('Call expert');
  };

  const handleGetSecondOpinion = () => {
    console.log('Get second opinion');
  };

  const handleSaveReport = () => {
    console.log('Save report');
  };

  // Check if diagnosis is already parsed JSON or needs error handling
  if (!diagnosis || diagnosis.error) {
    return (
      <SafeAreaView className="flex-1 bg-background font-sans">
        <View className="flex-1 justify-center items-center p-4">
          <Text className="text-xl text-gray-800 mb-4">Unable to process diagnosis</Text>
          <Text className="text-gray-600 mb-4 text-center">
            {diagnosis?.message || 'There was an error processing the response'}
          </Text>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            className="bg-primary py-3 px-6 rounded-lg"
          >
            <Text className="text-white font-bold">Go Back</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-background font-sans">
      <ScrollView className="flex-1">
        {/* Header */}
        <View className="flex-row items-center p-4 bg-white">
          <TouchableOpacity onPress={() => navigation.goBack()} className="mr-3">
            <Ionicons name="arrow-back" size={24} color="#333" />
          </TouchableOpacity>
          <Text className="text-lg font-bold text-gray-800">Diagnosis Results</Text>
        </View>

        {/* Image Preview */}
        {imageUri && (
          <Image
            source={{ uri: imageUri }}
            className="w-full h-60 bg-gray-100"
            resizeMode="cover"
          />
        )}

        <View className="p-4">
          {/* Language Detection */}
          {diagnosis.language_detected && (
            <View className="bg-blue-50 p-3 rounded-lg mb-4">
              <Text className="text-sm text-blue-700 font-medium">
                Language: {diagnosis.language_detected}
              </Text>
            </View>
          )}

          {/* Image Assessment */}
          {diagnosis.image_assessment && (
            <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
              <Text className="text-lg font-bold text-gray-800 mb-2">📸 Image Quality</Text>
              <Text className="text-gray-600 mb-1">
                Quality: <Text className="font-medium">{diagnosis.image_assessment.quality}</Text>
              </Text>
              <Text className="text-gray-600 mb-1">
                Confidence: <Text className="font-medium">{diagnosis.image_assessment.diagnostic_confidence}%</Text>
              </Text>
              {diagnosis.image_assessment.limitations && (
                <Text className="text-gray-600 text-sm">
                  Note: {diagnosis.image_assessment.limitations}
                </Text>
              )}
            </View>
          )}

          {/* Crop Identification */}
          {diagnosis.crop_identification && (
            <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
              <Text className="text-lg font-bold text-gray-800 mb-2">🌱 Crop Identification</Text>
              <Text className="text-xl font-semibold text-green-700 mb-1">
                {diagnosis.crop_identification.crop_name}
              </Text>
              <Text className="text-gray-600 mb-1">
                Confidence: <Text className="font-medium">{diagnosis.crop_identification.confidence_percentage}%</Text>
              </Text>
              <Text className="text-gray-600 mb-1">
                Growth Stage: <Text className="font-medium">{diagnosis.crop_identification.growth_stage}</Text>
              </Text>
              {diagnosis.crop_identification.variety_hints && (
                <Text className="text-gray-600 text-sm">
                  {diagnosis.crop_identification.variety_hints}
                </Text>
              )}
            </View>
          )}

          {/* Disease Analysis */}
          {diagnosis.disease_analysis?.disease_detected && (
            <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
              <Text className="text-lg font-bold text-gray-800 mb-2">🦠 Disease Detected</Text>
              <Text className="text-xl font-semibold text-red-600 mb-1">
                {diagnosis.disease_analysis.primary_diagnosis?.disease_name}
              </Text>
              <Text className="text-gray-600 mb-1">
                Scientific name: <Text className="italic">{diagnosis.disease_analysis.primary_diagnosis?.scientific_name}</Text>
              </Text>
              <Text className="text-gray-600 mb-1">
                Confidence: <Text className="font-medium">{diagnosis.disease_analysis.primary_diagnosis?.confidence_percentage}%</Text>
              </Text>
              <Text className="text-gray-600 mb-1">
                Severity: <Text className="font-medium capitalize">{diagnosis.disease_analysis.primary_diagnosis?.severity_level}</Text>
              </Text>
              <Text className="text-gray-600 mb-2">
                Affected area: <Text className="font-medium">{diagnosis.disease_analysis.primary_diagnosis?.affected_area_percentage}%</Text>
              </Text>
              
              {diagnosis.disease_analysis.symptoms_observed?.length > 0 && (
                <View className="mt-2">
                  <Text className="font-semibold text-gray-700 mb-1">Symptoms observed:</Text>
                  {diagnosis.disease_analysis.symptoms_observed.map((symptom: string, index: number) => (
                    <Text key={index} className="text-gray-600 ml-2">• {symptom}</Text>
                  ))}
                </View>
              )}

              {diagnosis.disease_analysis.differential_diagnosis?.length > 0 && (
                <View className="mt-2">
                  <Text className="font-semibold text-gray-700 mb-1">Other possibilities:</Text>
                  {diagnosis.disease_analysis.differential_diagnosis.map((disease: string, index: number) => (
                    <Text key={index} className="text-gray-600 ml-2">• {disease}</Text>
                  ))}
                </View>
              )}
            </View>
          )}

          {/* Treatment Recommendations */}
          {diagnosis.treatment_recommendations && (
            <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
              <Text className="text-lg font-bold text-gray-800 mb-3">💊 Treatment Recommendations</Text>
              
              {/* Immediate Action */}
              {diagnosis.treatment_recommendations.immediate_action && (
                <View className="mb-4 bg-orange-50 p-3 rounded-lg">
                  <Text className="font-semibold text-orange-700 mb-2">
                    ⚡ Immediate Action ({diagnosis.treatment_recommendations.immediate_action.urgency} urgency)
                  </Text>
                  {diagnosis.treatment_recommendations.immediate_action.steps?.map((step: string, index: number) => (
                    <Text key={index} className="text-gray-700 ml-2 mb-1">• {step}</Text>
                  ))}
                </View>
              )}

              {/* Organic Treatment */}
              {diagnosis.treatment_recommendations.organic_treatment && (
                <View className="mb-4 bg-green-50 p-3 rounded-lg">
                  <Text className="font-semibold text-green-700 mb-2">🌿 Organic Treatment</Text>
                  <Text className="text-gray-700 mb-1">
                    <Text className="font-medium">Treatment:</Text> {diagnosis.treatment_recommendations.organic_treatment.primary_recommendation}
                  </Text>
                  <Text className="text-gray-700 mb-1">
                    <Text className="font-medium">Method:</Text> {diagnosis.treatment_recommendations.organic_treatment.application_method}
                  </Text>
                  <Text className="text-gray-700 mb-1">
                    <Text className="font-medium">Frequency:</Text> {diagnosis.treatment_recommendations.organic_treatment.frequency}
                  </Text>
                  <Text className="text-green-600 font-medium">
                    Cost: {diagnosis.treatment_recommendations.cost_analysis?.organic_cost_per_acre}
                  </Text>
                </View>
              )}

              {/* Chemical Treatment */}
              {diagnosis.treatment_recommendations.chemical_treatment && (
                <View className="mb-4 bg-blue-50 p-3 rounded-lg">
                  <Text className="font-semibold text-blue-700 mb-2">🧪 Chemical Treatment</Text>
                  <Text className="text-gray-700 mb-1">
                    <Text className="font-medium">Treatment:</Text> {diagnosis.treatment_recommendations.chemical_treatment.primary_recommendation}
                  </Text>
                  <Text className="text-gray-700 mb-1">
                    <Text className="font-medium">Dosage:</Text> {diagnosis.treatment_recommendations.chemical_treatment.dosage}
                  </Text>
                  <Text className="text-gray-700 mb-1">
                    <Text className="font-medium">Frequency:</Text> {diagnosis.treatment_recommendations.chemical_treatment.frequency}
                  </Text>
                  
                  {diagnosis.treatment_recommendations.chemical_treatment.indian_brands?.length > 0 && (
                    <View className="mt-2">
                      <Text className="font-medium text-gray-700 mb-1">Available brands:</Text>
                      {diagnosis.treatment_recommendations.chemical_treatment.indian_brands.map((brand: string, index: number) => (
                        <Text key={index} className="text-gray-600 ml-2">• {brand}</Text>
                      ))}
                    </View>
                  )}

                  <Text className="text-blue-600 font-medium mt-2">
                    Cost: {diagnosis.treatment_recommendations.cost_analysis?.chemical_cost_per_acre}
                  </Text>

                  {diagnosis.treatment_recommendations.chemical_treatment.precautions && (
                    <Text className="text-red-600 text-sm mt-2 font-medium">
                      ⚠️ {diagnosis.treatment_recommendations.chemical_treatment.precautions}
                    </Text>
                  )}
                </View>
              )}
            </View>
          )}

          {/* Prevention Measures */}
          {diagnosis.prevention_measures && (
            <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
              <Text className="text-lg font-bold text-gray-800 mb-2">🛡️ Prevention</Text>
              
              {diagnosis.prevention_measures.cultural_practices?.length > 0 && (
                <View className="mb-3">
                  <Text className="font-semibold text-gray-700 mb-1">Cultural practices:</Text>
                  {diagnosis.prevention_measures.cultural_practices.map((practice: string, index: number) => (
                    <Text key={index} className="text-gray-600 ml-2">• {practice}</Text>
                  ))}
                </View>
              )}

              {diagnosis.prevention_measures.seasonal_timing && (
                <Text className="text-gray-600">
                  <Text className="font-medium">Seasonal timing:</Text> {diagnosis.prevention_measures.seasonal_timing}
                </Text>
              )}
            </View>
          )}

          {/* Regional Context */}
          {diagnosis.regional_context && (
            <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
              <Text className="text-lg font-bold text-gray-800 mb-2">🇮🇳 Karnataka Context</Text>
              <Text className="text-gray-600 mb-1">
                <Text className="font-medium">Prevalence:</Text> {diagnosis.regional_context.karnataka_prevalence}
              </Text>
              <Text className="text-gray-600 mb-2">
                <Text className="font-medium">Season:</Text> {diagnosis.regional_context.season_correlation}
              </Text>
              
              {diagnosis.regional_context.local_support?.helpline && (
                <TouchableOpacity className="bg-green-100 p-3 rounded-lg">
                  <Text className="text-green-700 font-medium text-center">
                    📞 {diagnosis.regional_context.local_support.helpline}
                  </Text>
                </TouchableOpacity>
              )}
            </View>
          )}

          {/* Follow-up */}
          {diagnosis.follow_up && (
            <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
              <Text className="text-lg font-bold text-gray-800 mb-2">📋 Follow-up</Text>
              
              {diagnosis.follow_up.monitoring_schedule && (
                <Text className="text-gray-600 mb-2">
                  <Text className="font-medium">Monitoring:</Text> {diagnosis.follow_up.monitoring_schedule}
                </Text>
              )}
              
              {diagnosis.follow_up.success_indicators?.length > 0 && (
                <View className="mb-2">
                  <Text className="font-semibold text-green-600 mb-1">✅ Success indicators:</Text>
                  {diagnosis.follow_up.success_indicators.map((indicator: string, index: number) => (
                    <Text key={index} className="text-gray-600 ml-2">• {indicator}</Text>
                  ))}
                </View>
              )}

              {diagnosis.follow_up.escalation_triggers?.length > 0 && (
                <View>
                  <Text className="font-semibold text-red-600 mb-1">🚨 Contact expert if:</Text>
                  {diagnosis.follow_up.escalation_triggers.map((trigger: string, index: number) => (
                    <Text key={index} className="text-gray-600 ml-2">• {trigger}</Text>
                  ))}
                </View>
              )}
            </View>
          )}

          {/* Disclaimer */}
          {diagnosis.disclaimer && (
            <View className="bg-yellow-50 p-4 rounded-lg mb-4">
              <Text className="text-yellow-800 text-sm leading-5">
                ⚠️ <Text className="font-medium">Disclaimer:</Text> {diagnosis.disclaimer}
              </Text>
            </View>
          )}
        </View>
      </ScrollView>

      {/* Bottom Action Buttons */}
      <View className="p-4 bg-background">
        <View className="flex-row justify-between mb-4">
          <TouchableOpacity
            onPress={handleCallExpert}
            className="bg-white py-3 px-6 rounded-lg border border-gray-200 flex-1 mr-2"
          >
            <Text className="font-medium text-gray-700 text-center">📞 Call Expert</Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={handleGetSecondOpinion}
            className="bg-white py-3 px-6 rounded-lg border border-gray-200 flex-1 ml-2"
          >
            <Text className="font-medium text-gray-700 text-center">🔄 Second Opinion</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity onPress={handleSaveReport} className="bg-primary py-4 rounded-xl">
          <Text className="text-white font-bold text-center text-lg">
            💾 Save Report
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};
