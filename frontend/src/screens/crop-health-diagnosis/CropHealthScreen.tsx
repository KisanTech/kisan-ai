import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  SafeAreaView,
  TouchableOpacity,
  Image,
  Alert,
  ScrollView,
  Animated,
  Easing,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { useTranslation } from 'react-i18next';
import { RootStackParamList } from '../../types/navigation';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import {
  diagnosisService,
  DiagnosisRequest,
  DiagnosisResponse,
  ParsedAgentResponse,
} from '../../services/diagnosisService';
import { useLanguage } from '../../i18n/LanguageContext';

type NavigationProp = StackNavigationProp<RootStackParamList>;

export const CropHealthScreen: React.FC = () => {
  const navigation = useNavigation<NavigationProp>();
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [diagnosis, setDiagnosis] = useState<DiagnosisResponse | null>(null);
  const { t } = useTranslation();
  const { currentLanguage } = useLanguage();

  // Animation value for rotating icon
  const spinValue = useRef(new Animated.Value(0)).current;

  // Set up rotation animation
  useEffect(() => {
    if (isLoading) {
      Animated.loop(
        Animated.timing(spinValue, {
          toValue: 1,
          duration: 1500,
          easing: Easing.linear,
          useNativeDriver: true,
        })
      ).start();
    } else {
      spinValue.setValue(0);
    }
  }, [isLoading]);

  // Create interpolated rotation value
  const spin = spinValue.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  // Request permissions for camera and media library
  const requestPermissions = async () => {
    const { status: cameraStatus } = await ImagePicker.requestCameraPermissionsAsync();
    const { status: mediaStatus } = await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (cameraStatus !== 'granted' || mediaStatus !== 'granted') {
      Alert.alert(t('cropHealth.permissionsRequired'), t('cropHealth.permissionsMessage'), [
        { text: t('common.ok') },
      ]);
      return false;
    }
    return true;
  };

  // Handle camera capture
  const handleCameraCapture = async () => {
    const hasPermissions = await requestPermissions();
    if (!hasPermissions) return;

    try {
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ['images'],
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setSelectedImage(result.assets[0].uri);
        setDiagnosis(null); // Clear previous diagnosis
      }
    } catch (error) {
      Alert.alert(t('common.error'), t('cropHealth.errorCapture'));
    }
  };

  // Handle gallery selection
  const handleGallerySelect = async () => {
    const hasPermissions = await requestPermissions();
    if (!hasPermissions) return;

    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setSelectedImage(result.assets[0].uri);
        setDiagnosis(null); // Clear previous diagnosis
      }
    } catch (error) {
      Alert.alert(t('common.error'), t('cropHealth.errorSelect'));
    }
  };

  // Parse the raw agent response JSON safely
  const parseAgentResponse = (rawResponse: string): ParsedAgentResponse | null => {
    try {
      // Extract JSON from the raw response (remove ```json and ``` wrapper if present)
      let jsonString = rawResponse.trim();
      if (jsonString.startsWith('```json')) {
        jsonString = jsonString.replace(/^```json\s*/, '').replace(/\s*```$/, '');
      }

      const parsed = JSON.parse(jsonString);
      console.log('Parsed diagnosis:', parsed);
      return parsed;
    } catch (error) {
      console.error('Error parsing agent response:', error);
      console.log('Raw response:', rawResponse);
      return null;
    }
  };

  // Translate diagnosis content to current language
  const translateDiagnosis = async (
    parsedDiagnosis: ParsedAgentResponse
  ): Promise<ParsedAgentResponse> => {
    const translated: ParsedAgentResponse = { ...parsedDiagnosis };

    // Helper function to translate text
    const translateText = async (text: string | undefined): Promise<string | undefined> => {
      if (!text) return text;
      return await diagnosisService.translateText(text, currentLanguage);
    };

    // Helper function to translate array of strings
    const translateArray = async (arr: string[] | undefined): Promise<string[] | undefined> => {
      if (!arr) return arr;
      const translatedArray = await Promise.all(arr.map(item => translateText(item)));
      return translatedArray.filter(item => item !== undefined) as string[];
    };

    // Translate crop identification
    if (translated.crop_identification) {
      translated.crop_identification.crop_name = await translateText(
        translated.crop_identification.crop_name
      );
      translated.crop_identification.variety_hints = await translateText(
        translated.crop_identification.variety_hints
      );
      translated.crop_identification.growth_stage = await translateText(
        translated.crop_identification.growth_stage
      );
    }

    // Translate disease analysis
    if (translated.disease_analysis?.primary_diagnosis) {
      translated.disease_analysis.primary_diagnosis.disease_name = await translateText(
        translated.disease_analysis.primary_diagnosis.disease_name
      );
      translated.disease_analysis.primary_diagnosis.scientific_name = await translateText(
        translated.disease_analysis.primary_diagnosis.scientific_name
      );
      translated.disease_analysis.primary_diagnosis.severity_level = await translateText(
        translated.disease_analysis.primary_diagnosis.severity_level
      );
    }

    if (translated.disease_analysis) {
      translated.disease_analysis.symptoms_observed = await translateArray(
        translated.disease_analysis.symptoms_observed
      );
      translated.disease_analysis.differential_diagnosis = await translateArray(
        translated.disease_analysis.differential_diagnosis
      );
    }

    // Translate treatment recommendations
    if (translated.treatment_recommendations?.immediate_action) {
      translated.treatment_recommendations.immediate_action.urgency = await translateText(
        translated.treatment_recommendations.immediate_action.urgency
      );
      translated.treatment_recommendations.immediate_action.steps = await translateArray(
        translated.treatment_recommendations.immediate_action.steps
      );
    }

    if (translated.treatment_recommendations?.organic_treatment) {
      translated.treatment_recommendations.organic_treatment.primary_recommendation =
        await translateText(
          translated.treatment_recommendations.organic_treatment.primary_recommendation
        );
      translated.treatment_recommendations.organic_treatment.application_method =
        await translateText(
          translated.treatment_recommendations.organic_treatment.application_method
        );
      translated.treatment_recommendations.organic_treatment.frequency = await translateText(
        translated.treatment_recommendations.organic_treatment.frequency
      );
      translated.treatment_recommendations.organic_treatment.local_availability =
        await translateText(
          translated.treatment_recommendations.organic_treatment.local_availability
        );
    }

    if (translated.treatment_recommendations?.chemical_treatment) {
      translated.treatment_recommendations.chemical_treatment.primary_recommendation =
        await translateText(
          translated.treatment_recommendations.chemical_treatment.primary_recommendation
        );
      translated.treatment_recommendations.chemical_treatment.dosage = await translateText(
        translated.treatment_recommendations.chemical_treatment.dosage
      );
      translated.treatment_recommendations.chemical_treatment.application_method =
        await translateText(
          translated.treatment_recommendations.chemical_treatment.application_method
        );
      translated.treatment_recommendations.chemical_treatment.frequency = await translateText(
        translated.treatment_recommendations.chemical_treatment.frequency
      );
      translated.treatment_recommendations.chemical_treatment.precautions = await translateText(
        translated.treatment_recommendations.chemical_treatment.precautions
      );
      translated.treatment_recommendations.chemical_treatment.indian_brands = await translateArray(
        translated.treatment_recommendations.chemical_treatment.indian_brands
      );
    }

    if (translated.treatment_recommendations?.cost_analysis) {
      translated.treatment_recommendations.cost_analysis.organic_cost_per_acre =
        await translateText(
          translated.treatment_recommendations.cost_analysis.organic_cost_per_acre
        );
      translated.treatment_recommendations.cost_analysis.chemical_cost_per_acre =
        await translateText(
          translated.treatment_recommendations.cost_analysis.chemical_cost_per_acre
        );
      translated.treatment_recommendations.cost_analysis.recommendation = await translateText(
        translated.treatment_recommendations.cost_analysis.recommendation
      );
    }

    // Translate prevention measures
    if (translated.prevention_measures) {
      translated.prevention_measures.cultural_practices = await translateArray(
        translated.prevention_measures.cultural_practices
      );
      translated.prevention_measures.resistant_varieties = await translateArray(
        translated.prevention_measures.resistant_varieties
      );
      translated.prevention_measures.seasonal_timing = await translateText(
        translated.prevention_measures.seasonal_timing
      );
    }

    // Translate follow-up
    if (translated.follow_up) {
      translated.follow_up.monitoring_schedule = await translateText(
        translated.follow_up.monitoring_schedule
      );
      translated.follow_up.success_indicators = await translateArray(
        translated.follow_up.success_indicators
      );
      translated.follow_up.escalation_triggers = await translateArray(
        translated.follow_up.escalation_triggers
      );
    }

    // Translate disclaimer
    translated.disclaimer = await translateText(translated.disclaimer);

    return translated;
  };

  // Handle crop health diagnosis
  const handleDiagnosis = async () => {
    if (!selectedImage) {
      Alert.alert(t('cropHealth.noImage'), t('cropHealth.selectImageFirst'));
      return;
    }

    setIsLoading(true);
    try {
      // Call the diagnosis service with multipart form-data
      const response = await diagnosisService.diagnoseCrop({
        imageUri: selectedImage,
        description: 'Image of the crop - to be processed for analysis',
      });

      // Parse the agent response
      const parsedDiagnosis = parseAgentResponse(response.raw_agent_response);
      if (!parsedDiagnosis) {
        throw new Error('Failed to parse agent response');
      }

      // Check if translation is needed (skip for English)
      let translatedDiagnosis = parsedDiagnosis;

      if (currentLanguage && currentLanguage !== 'en') {
        // Start translation process only for non-English languages
        setIsTranslating(true);
        translatedDiagnosis = await translateDiagnosis(parsedDiagnosis);
      }

      // Create updated response with translated data
      const updatedResponse = {
        ...response,
        translatedDiagnosis,
      };

      // Navigate to results screen with the translated diagnosis response
      navigation.navigate('DiagnosisResult', {
        diagnosis: updatedResponse,
        imageUri: selectedImage,
      });
    } catch (error) {
      console.error('Diagnosis error:', error);
      Alert.alert(t('cropHealth.diagnosisFailed'), t('cropHealth.diagnosisFailedMessage'));
    } finally {
      setIsLoading(false);
      setIsTranslating(false);
    }
  };

  // Reset screen state
  const handleRetake = () => {
    setSelectedImage(null);
    setDiagnosis(null);
  };

  const photoTips = [
    t('cropHealth.photoTips.tip1'),
    t('cropHealth.photoTips.tip2'),
    t('cropHealth.photoTips.tip3'),
    t('cropHealth.photoTips.tip4'),
  ];

  return (
    <SafeAreaView className="flex-1 bg-background font-sans">
      <ScrollView className="flex-1 px-4 py-2">
        {/* Header */}
        <View className="mb-6">
          <Text className="text-lg font-bold text-gray-800 text-center mb-2">
            {t('cropHealth.diagnosePlantDisease')}
          </Text>
          <Text className="text-gray-600 text-center">{t('cropHealth.subtitle')}</Text>
        </View>

        {/* Image Display Area */}
        <View className="bg-white rounded-2xl p-4 mb-6 shadow-sm">
          {selectedImage ? (
            <View>
              <Image
                source={{ uri: selectedImage }}
                className="w-full h-72 rounded-xl"
                resizeMode="cover"
              />
              <TouchableOpacity
                onPress={handleRetake}
                className="mt-4 bg-gray-100 px-4 py-2 rounded-lg self-center"
              >
                <Text className="text-gray-700 font-medium">{t('cropHealth.retake')}</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View className="h-64 bg-gray-100 rounded-xl justify-center items-center">
              <Ionicons name="camera-outline" size={48} color="#9CA3AF" />
              <Text className="text-gray-500 mt-2">{t('cropHealth.noImageSelected')}</Text>
            </View>
          )}
        </View>

        {/* Action Buttons */}
        <View className="flex-row justify-between mb-6 gap-3">
          <TouchableOpacity
            onPress={handleCameraCapture}
            className="flex-1 bg-primary py-3 rounded-lg flex-row justify-center items-center"
          >
            <Ionicons name="camera" size={22} color="white" />
            <Text className="text-white font-bold ml-2">{t('cropHealth.capture')}</Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={handleGallerySelect}
            className="flex-1 bg-primary py-3 rounded-lg flex-row justify-center items-center"
          >
            <Ionicons name="images" size={22} color="white" />
            <Text className="text-white font-bold ml-2">{t('cropHealth.gallery')}</Text>
          </TouchableOpacity>
        </View>

        {/* Photo Tips */}
        <View className="bg-white rounded-2xl p-4 mb-6 shadow-sm">
          <Text className="text-lg font-semibold text-gray-800 mb-3">
            {t('cropHealth.photoTips.title')}
          </Text>
          {photoTips.map((tip, index) => (
            <Text key={index} className="text-gray-600 mb-2 leading-5">
              {tip}
            </Text>
          ))}
        </View>
      </ScrollView>

      {/* Bottom Action Button */}
      <View className="px-4 pb-4 bg-gray-50">
        <TouchableOpacity
          onPress={handleDiagnosis}
          disabled={!selectedImage || isLoading || isTranslating}
          className={`py-4 rounded-xl flex-row justify-center items-center ${
            selectedImage && !isLoading && !isTranslating ? 'bg-primary' : 'bg-accent'
          }`}
        >
          <View className="flex-row items-center justify-center">
            {isLoading || isTranslating ? (
              <>
                <Animated.View style={{ transform: [{ rotate: spin }] }}>
                  <Ionicons name="hourglass-outline" size={24} color="black" />
                </Animated.View>
                <Text className="text-black font-bold text-lg ml-3">
                  {isTranslating ? t('cropHealth.translating') : t('cropHealth.analyzing')}
                </Text>
              </>
            ) : (
              <>
                <Ionicons name="leaf" size={24} color="white" />
                <Text className="text-white font-bold text-lg ml-3">
                  {t('cropHealth.checkCropHealth')}
                </Text>
              </>
            )}
          </View>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};
