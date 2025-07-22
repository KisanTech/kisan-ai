import React, { useState } from 'react';
import {
  View,
  Text,
  SafeAreaView,
  TouchableOpacity,
  Image,
  Alert,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import {
  diagnosisService,
  DiagnosisRequest,
  DiagnosisResponse,
} from '../../services/diagnosisService';

export const CropHealthScreen: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [diagnosis, setDiagnosis] = useState<DiagnosisResponse | null>(null);

  // Request permissions for camera and media library
  const requestPermissions = async () => {
    const { status: cameraStatus } = await ImagePicker.requestCameraPermissionsAsync();
    const { status: mediaStatus } = await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (cameraStatus !== 'granted' || mediaStatus !== 'granted') {
      Alert.alert(
        'Permissions Required',
        'We need camera and photo library permissions to help diagnose your crops.',
        [{ text: 'OK' }]
      );
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
      Alert.alert('Error', 'Failed to capture image. Please try again.');
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
      Alert.alert('Error', 'Failed to select image. Please try again.');
    }
  };

  // Handle crop health diagnosis
  const handleDiagnosis = async () => {
    if (!selectedImage) {
      Alert.alert('No Image', 'Please capture or select an image first.');
      return;
    }

    setIsLoading(true);
    try {
      const requestData: DiagnosisRequest = {
        imageUri: selectedImage,
        description: 'Crop health diagnosis from mobile app',
      };

      const response = await diagnosisService.diagnoseCrop(requestData);
      setDiagnosis(response);
    } catch (error) {
      console.error('Diagnosis error:', error);
      Alert.alert(
        'Diagnosis Failed',
        'Unable to analyze the image. Please try again with a clearer photo.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Reset screen state
  const handleRetake = () => {
    setSelectedImage(null);
    setDiagnosis(null);
  };

  const photoTips = [
    '📱 Hold phone steady, close to affected leaves',
    '☀️ Use good natural light, avoid shadows',
    '🔍 Focus clearly on damaged areas',
    '📐 Keep leaf flat and visible',
  ];

  return (
    <SafeAreaView className="flex-1 bg-background font-sans">
      <ScrollView className="flex-1 px-4 py-2">
        {/* Header */}
        <View className="mb-6">
          <Text className="text-lg font-bold text-gray-800 text-center mb-2">
            Diagnose Plant Disease
          </Text>
          <Text className="text-gray-600 text-center">
            Take a clear photo of the affected leaves
          </Text>
        </View>

        {/* Image Display Area */}
        <View className="bg-white rounded-2xl p-4 mb-6 shadow-sm">
          {selectedImage ? (
            <View>
              <Image
                source={{ uri: selectedImage }}
                className="w-full h-64 rounded-xl"
                resizeMode="cover"
              />
              <TouchableOpacity
                onPress={handleRetake}
                className="mt-4 bg-gray-100 px-4 py-2 rounded-lg self-center"
              >
                <Text className="text-gray-700 font-medium">Retake</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View className="h-64 bg-gray-100 rounded-xl justify-center items-center">
              <Ionicons name="camera-outline" size={48} color="#9CA3AF" />
              <Text className="text-gray-500 mt-2">No image selected</Text>
            </View>
          )}
        </View>

        {/* Action Buttons */}
        <View className="flex-row justify-between mb-6 gap-3">
          <TouchableOpacity
            onPress={handleCameraCapture}
            className="flex-1 bg-primary py-3 rounded-lg flex-row justify-center items-center"
          >
            <Ionicons name="camera" size={18} color="white" />
            <Text className="text-white font-medium ml-2">Capture</Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={handleGallerySelect}
            className="flex-1 bg-secondary py-3 rounded-lg flex-row justify-center items-center"
          >
            <Ionicons name="images" size={18} color="white" />
            <Text className="text-white font-medium ml-2">Gallery</Text>
          </TouchableOpacity>
        </View>

        {/* Photo Tips */}
        <View className="bg-white rounded-2xl p-4 mb-6 shadow-sm">
          <Text className="text-lg font-semibold text-gray-800 mb-3">Tips for better photos</Text>
          {photoTips.map((tip, index) => (
            <Text key={index} className="text-gray-600 mb-2 leading-5">
              {tip}
            </Text>
          ))}
        </View>

        {/* Diagnosis Results */}
        {diagnosis && (
          <View className="bg-white rounded-2xl p-4 mb-6 shadow-sm">
            <Text className="text-lg font-semibold text-gray-800 mb-4">Diagnosis Results</Text>

            {/* Status */}
            <View className="mb-4">
              <Text className="text-sm font-medium text-gray-600 mb-1">Status:</Text>
              <Text className="text-lg text-green-600">{diagnosis.status}</Text>
            </View>

            {/* Disease Diagnosis */}
            <View className="mb-4">
              <Text className="text-sm font-medium text-gray-600 mb-2">Disease Detected:</Text>
              <Text className="text-xl font-bold text-red-600 mb-1">
                {diagnosis.diagnosis.disease_name}
              </Text>
              <Text className="text-gray-800">
                • Confidence: {(diagnosis.diagnosis.confidence * 100).toFixed(1)}%
              </Text>
              <Text className="text-gray-800">• Severity: {diagnosis.diagnosis.severity}</Text>
              <Text className="text-gray-800">
                • Affected Area: {diagnosis.diagnosis.affected_area}
              </Text>
            </View>

            {/* Treatment */}
            <View className="mb-4">
              <Text className="text-sm font-medium text-gray-600 mb-2">
                Treatment Recommendations:
              </Text>
              <Text className="text-gray-800 mb-1">
                • Immediate Action: {diagnosis.treatment.immediate_action}
              </Text>
              <Text className="text-gray-800 mb-1">
                • Fungicide: {diagnosis.treatment.recommended_fungicide}
              </Text>
              <Text className="text-gray-800">
                • Frequency: {diagnosis.treatment.application_frequency}
              </Text>
            </View>

            {/* Local Suppliers */}
            {diagnosis.local_suppliers && diagnosis.local_suppliers.length > 0 && (
              <View>
                <Text className="text-sm font-medium text-gray-600 mb-2">Nearby Suppliers:</Text>
                {diagnosis.local_suppliers.map((supplier, index) => (
                  <Text key={index} className="text-gray-800 mb-1">
                    • {supplier.name} ({supplier.distance})
                  </Text>
                ))}
              </View>
            )}
          </View>
        )}
      </ScrollView>

      {/* Bottom Action Button */}
      <View className="px-4 pb-4 bg-gray-50">
        <TouchableOpacity
          onPress={handleDiagnosis}
          disabled={!selectedImage || isLoading}
          className={`py-4 rounded-xl flex-row justify-center items-center ${
            selectedImage && !isLoading ? 'bg-green-600' : 'bg-gray-300'
          }`}
        >
          {isLoading ? (
            <ActivityIndicator color="white" />
          ) : (
            <>
              <Ionicons name="medical" size={20} color="white" />
              <Text className="text-white font-bold text-lg ml-2">CHECK CROP HEALTH</Text>
            </>
          )}
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};
