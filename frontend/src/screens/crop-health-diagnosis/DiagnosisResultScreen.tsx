import React, { useMemo } from 'react';
import { View, Text, Image, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { useTranslation } from 'react-i18next';
import { RootStackParamList } from '../../types/navigation';
import { Ionicons } from '@expo/vector-icons';
import { DiagnosisResponse, ParsedAgentResponse } from '../../services/diagnosisService';

interface RouteParams {
  diagnosis: DiagnosisResponse & { translatedDiagnosis?: ParsedAgentResponse };
  imageUri: string;
}

type NavigationProp = StackNavigationProp<RootStackParamList>;

export const DiagnosisResultScreen: React.FC = () => {
  const navigation = useNavigation<NavigationProp>();
  const route = useRoute();
  const { diagnosis, imageUri } = route.params as RouteParams;
  const { t } = useTranslation();

  // Use the translated diagnosis passed from CropHealthScreen
  const displayDiagnosis = diagnosis.translatedDiagnosis;

  const handleCallExpert = () => {
    console.log('Call expert');
  };

  const handleGetSecondOpinion = () => {
    console.log('Get second opinion');
  };

  const handleSaveReport = () => {
    console.log('Save report');
  };

  // Check if diagnosis is valid and parseable
  if (!diagnosis || !diagnosis.success || diagnosis.error || !displayDiagnosis) {
    return (
      <SafeAreaView className="flex-1 bg-background font-sans">
        <View className="flex-1 justify-center items-center p-4">
          <Text className="text-xl text-gray-800 mb-4">{t('diagnosisResult.unableToProcess')}</Text>
          <Text className="text-gray-600 mb-4 text-center">
            {diagnosis?.error || 'Unable to parse diagnosis data'}
          </Text>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            className="bg-primary py-3 px-6 rounded-lg"
          >
            <Text className="text-white font-bold">{t('diagnosisResult.goBack')}</Text>
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
          <Text className="text-lg font-bold text-gray-800">{t('diagnosisResult.title')}</Text>
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
          {/* Crop Identification */}
          {displayDiagnosis?.crop_identification && (
            <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
              <Text className="text-lg font-bold text-gray-800 mb-2">
                {t('diagnosisResult.cropIdentification')}
              </Text>
              <Text className="text-xl font-semibold text-green-700 mb-1">
                {displayDiagnosis.crop_identification.crop_name}
              </Text>
              {displayDiagnosis.crop_identification.confidence_percentage && (
                <Text className="text-gray-600 mb-1">
                  {t('diagnosisResult.confidence')}:{' '}
                  <Text className="font-medium">
                    {displayDiagnosis.crop_identification.confidence_percentage}%
                  </Text>
                </Text>
              )}
              {displayDiagnosis.crop_identification.growth_stage && (
                <Text className="text-gray-600 mb-1">
                  {t('diagnosisResult.growthStage')}:{' '}
                  <Text className="font-medium">
                    {displayDiagnosis.crop_identification.growth_stage}
                  </Text>
                </Text>
              )}
              {displayDiagnosis.crop_identification.variety_hints && (
                <Text className="text-gray-600 text-sm">
                  {displayDiagnosis.crop_identification.variety_hints}
                </Text>
              )}
            </View>
          )}

          {/* Disease Analysis */}
          {displayDiagnosis?.disease_analysis?.disease_detected && (
            <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
              <Text className="text-lg font-bold text-gray-800 mb-2">
                {t('diagnosisResult.diseaseDetected')}
              </Text>
              {displayDiagnosis.disease_analysis.primary_diagnosis?.disease_name && (
                <Text className="text-xl font-semibold text-red-600 mb-1">
                  {displayDiagnosis.disease_analysis.primary_diagnosis.disease_name}
                </Text>
              )}
              {displayDiagnosis.disease_analysis.primary_diagnosis?.scientific_name && (
                <Text className="text-gray-600 mb-1">
                  {t('diagnosisResult.scientificName')}:{' '}
                  <Text className="italic">
                    {displayDiagnosis.disease_analysis.primary_diagnosis.scientific_name}
                  </Text>
                </Text>
              )}
              {displayDiagnosis.disease_analysis.primary_diagnosis?.confidence_percentage && (
                <Text className="text-gray-600 mb-1">
                  {t('diagnosisResult.confidence')}:{' '}
                  <Text className="font-medium">
                    {displayDiagnosis.disease_analysis.primary_diagnosis.confidence_percentage}%
                  </Text>
                </Text>
              )}
              {displayDiagnosis.disease_analysis.primary_diagnosis?.severity_level && (
                <Text className="text-gray-600 mb-1">
                  {t('diagnosisResult.severity')}:{' '}
                  <Text className="font-medium capitalize">
                    {displayDiagnosis.disease_analysis.primary_diagnosis.severity_level}
                  </Text>
                </Text>
              )}
              {displayDiagnosis.disease_analysis.primary_diagnosis?.affected_area_percentage && (
                <Text className="text-gray-600 mb-2">
                  {t('diagnosisResult.affectedArea')}:{' '}
                  <Text className="font-medium">
                    {displayDiagnosis.disease_analysis.primary_diagnosis.affected_area_percentage}%
                  </Text>
                </Text>
              )}

              {displayDiagnosis.disease_analysis.symptoms_observed?.length > 0 && (
                <View className="mt-2">
                  <Text className="font-semibold text-gray-700 mb-1">
                    {t('diagnosisResult.symptomsObserved')}:
                  </Text>
                  {displayDiagnosis.disease_analysis.symptoms_observed.map(
                    (symptom: string, index: number) => (
                      <Text key={index} className="text-gray-600 ml-2">
                        • {symptom}
                      </Text>
                    )
                  )}
                </View>
              )}

              {displayDiagnosis.disease_analysis.differential_diagnosis?.length > 0 && (
                <View className="mt-2">
                  <Text className="font-semibold text-gray-700 mb-1">
                    {t('diagnosisResult.otherPossibilities')}:
                  </Text>
                  {displayDiagnosis.disease_analysis.differential_diagnosis.map(
                    (disease: string, index: number) => (
                      <Text key={index} className="text-gray-600 ml-2">
                        • {disease}
                      </Text>
                    )
                  )}
                </View>
              )}
            </View>
          )}

          {/* Treatment Recommendations */}
          {displayDiagnosis?.treatment_recommendations && (
            <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
              <Text className="text-lg font-bold text-gray-800 mb-3">
                {t('diagnosisResult.treatmentRecommendations')}
              </Text>

              {/* Immediate Action */}
              {displayDiagnosis.treatment_recommendations.immediate_action && (
                <View className="mb-4 bg-orange-50 p-3 rounded-lg">
                  <Text className="font-semibold text-orange-700 mb-2">
                    {t('diagnosisResult.immediateAction')}
                    {displayDiagnosis.treatment_recommendations.immediate_action.urgency && (
                      <Text>
                        {' '}
                        ({displayDiagnosis.treatment_recommendations.immediate_action.urgency}{' '}
                        {t('diagnosisResult.urgency')})
                      </Text>
                    )}
                  </Text>
                  {displayDiagnosis.treatment_recommendations.immediate_action.steps?.map(
                    (step: string, index: number) => (
                      <Text key={index} className="text-gray-700 ml-2 mb-1">
                        • {step}
                      </Text>
                    )
                  )}
                </View>
              )}

              {/* Organic Treatment */}
              {displayDiagnosis.treatment_recommendations.organic_treatment && (
                <View className="mb-4 bg-green-50 p-3 rounded-lg">
                  <Text className="font-semibold text-green-700 mb-2">
                    {t('diagnosisResult.organicTreatment')}
                  </Text>
                  {displayDiagnosis.treatment_recommendations.organic_treatment
                    .primary_recommendation && (
                    <Text className="text-gray-700 mb-1">
                      <Text className="font-medium">{t('diagnosisResult.treatment')}:</Text>{' '}
                      {
                        displayDiagnosis.treatment_recommendations.organic_treatment
                          .primary_recommendation
                      }
                    </Text>
                  )}
                  {displayDiagnosis.treatment_recommendations.organic_treatment
                    .application_method && (
                    <Text className="text-gray-700 mb-1">
                      <Text className="font-medium">{t('diagnosisResult.method')}:</Text>{' '}
                      {
                        displayDiagnosis.treatment_recommendations.organic_treatment
                          .application_method
                      }
                    </Text>
                  )}
                  {displayDiagnosis.treatment_recommendations.organic_treatment.frequency && (
                    <Text className="text-gray-700 mb-1">
                      <Text className="font-medium">{t('diagnosisResult.frequency')}:</Text>{' '}
                      {displayDiagnosis.treatment_recommendations.organic_treatment.frequency}
                    </Text>
                  )}
                  {displayDiagnosis.treatment_recommendations.cost_analysis
                    ?.organic_cost_per_acre && (
                    <Text className="text-green-600 font-medium">
                      {t('diagnosisResult.cost')}:{' '}
                      {
                        displayDiagnosis.treatment_recommendations.cost_analysis
                          .organic_cost_per_acre
                      }
                    </Text>
                  )}
                </View>
              )}

              {/* Chemical Treatment */}
              {displayDiagnosis.treatment_recommendations.chemical_treatment && (
                <View className="mb-4 bg-blue-50 p-3 rounded-lg">
                  <Text className="font-semibold text-blue-700 mb-2">
                    {t('diagnosisResult.chemicalTreatment')}
                  </Text>
                  {displayDiagnosis.treatment_recommendations.chemical_treatment
                    .primary_recommendation && (
                    <Text className="text-gray-700 mb-1">
                      <Text className="font-medium">{t('diagnosisResult.treatment')}:</Text>{' '}
                      {
                        displayDiagnosis.treatment_recommendations.chemical_treatment
                          .primary_recommendation
                      }
                    </Text>
                  )}
                  {displayDiagnosis.treatment_recommendations.chemical_treatment.dosage && (
                    <Text className="text-gray-700 mb-1">
                      <Text className="font-medium">{t('diagnosisResult.dosage')}:</Text>{' '}
                      {displayDiagnosis.treatment_recommendations.chemical_treatment.dosage}
                    </Text>
                  )}
                  {displayDiagnosis.treatment_recommendations.chemical_treatment.frequency && (
                    <Text className="text-gray-700 mb-1">
                      <Text className="font-medium">{t('diagnosisResult.frequency')}:</Text>{' '}
                      {displayDiagnosis.treatment_recommendations.chemical_treatment.frequency}
                    </Text>
                  )}

                  {displayDiagnosis.treatment_recommendations.chemical_treatment.indian_brands
                    ?.length > 0 && (
                    <View className="mt-2">
                      <Text className="font-medium text-gray-700 mb-1">
                        {t('diagnosisResult.availableBrands')}:
                      </Text>
                      {displayDiagnosis.treatment_recommendations.chemical_treatment.indian_brands.map(
                        (brand: string, index: number) => (
                          <Text key={index} className="text-gray-600 ml-2">
                            • {brand}
                          </Text>
                        )
                      )}
                    </View>
                  )}

                  {displayDiagnosis.treatment_recommendations.cost_analysis
                    ?.chemical_cost_per_acre && (
                    <Text className="text-blue-600 font-medium mt-2">
                      {t('diagnosisResult.cost')}:{' '}
                      {
                        displayDiagnosis.treatment_recommendations.cost_analysis
                          .chemical_cost_per_acre
                      }
                    </Text>
                  )}

                  {displayDiagnosis.treatment_recommendations.chemical_treatment.precautions && (
                    <Text className="text-red-600 text-sm mt-2 font-medium">
                      {t('diagnosisResult.precautions')}{' '}
                      {displayDiagnosis.treatment_recommendations.chemical_treatment.precautions}
                    </Text>
                  )}
                </View>
              )}
            </View>
          )}

          {/* Prevention Measures */}
          {displayDiagnosis?.prevention_measures && (
            <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
              <Text className="text-lg font-bold text-gray-800 mb-2">
                {t('diagnosisResult.prevention')}
              </Text>

              {displayDiagnosis.prevention_measures.cultural_practices?.length > 0 && (
                <View className="mb-3">
                  <Text className="font-semibold text-gray-700 mb-1">
                    {t('diagnosisResult.culturalPractices')}:
                  </Text>
                  {displayDiagnosis.prevention_measures.cultural_practices.map(
                    (practice: string, index: number) => (
                      <Text key={index} className="text-gray-600 ml-2">
                        • {practice}
                      </Text>
                    )
                  )}
                </View>
              )}

              {displayDiagnosis.prevention_measures.seasonal_timing && (
                <Text className="text-gray-600">
                  <Text className="font-medium">{t('diagnosisResult.seasonalTiming')}:</Text>{' '}
                  {displayDiagnosis.prevention_measures.seasonal_timing}
                </Text>
              )}
            </View>
          )}

          {/* Follow-up */}
          {displayDiagnosis?.follow_up && (
            <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
              <Text className="text-lg font-bold text-gray-800 mb-2">
                {t('diagnosisResult.followUp')}
              </Text>

              {displayDiagnosis.follow_up.monitoring_schedule && (
                <Text className="text-gray-600 mb-2">
                  <Text className="font-medium">{t('diagnosisResult.monitoring')}:</Text>{' '}
                  {displayDiagnosis.follow_up.monitoring_schedule}
                </Text>
              )}

              {displayDiagnosis.follow_up.success_indicators?.length > 0 && (
                <View className="mb-2">
                  <Text className="font-semibold text-green-600 mb-1">
                    {t('diagnosisResult.successIndicators')}:
                  </Text>
                  {displayDiagnosis.follow_up.success_indicators.map(
                    (indicator: string, index: number) => (
                      <Text key={index} className="text-gray-600 ml-2">
                        • {indicator}
                      </Text>
                    )
                  )}
                </View>
              )}

              {displayDiagnosis.follow_up.escalation_triggers?.length > 0 && (
                <View>
                  <Text className="font-semibold text-red-600 mb-1">
                    {t('diagnosisResult.contactExpertIf')}:
                  </Text>
                  {displayDiagnosis.follow_up.escalation_triggers.map(
                    (trigger: string, index: number) => (
                      <Text key={index} className="text-gray-600 ml-2">
                        • {trigger}
                      </Text>
                    )
                  )}
                </View>
              )}
            </View>
          )}

          {/* Disclaimer */}
          {(displayDiagnosis?.disclaimer || diagnosis.disclaimer) && (
            <View className="bg-yellow-50 p-4 rounded-lg mb-4">
              <Text className="text-yellow-800 text-sm leading-5">
                <Text className="font-medium">{t('diagnosisResult.disclaimer')}:</Text>{' '}
                {displayDiagnosis?.disclaimer || diagnosis.disclaimer}
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
            <Text className="font-medium text-gray-700 text-center">
              {t('diagnosisResult.callExpert')}
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={handleGetSecondOpinion}
            className="bg-white py-3 px-6 rounded-lg border border-gray-200 flex-1 ml-2"
          >
            <Text className="font-medium text-gray-700 text-center">
              {t('diagnosisResult.secondOpinion')}
            </Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity onPress={handleSaveReport} className="bg-primary py-4 rounded-xl">
          <Text className="text-white font-bold text-center text-lg">
            {t('diagnosisResult.saveReport')}
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};
