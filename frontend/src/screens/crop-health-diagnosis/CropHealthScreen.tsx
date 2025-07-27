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
} from '../../services/diagnosisService';
import aiService from '../../services/aiService';

type NavigationProp = StackNavigationProp<RootStackParamList>;

export const CropHealthScreen: React.FC = () => {
  const navigation = useNavigation<NavigationProp>();
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [diagnosis, setDiagnosis] = useState<DiagnosisResponse | null>(null);
  const { t } = useTranslation();

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

  // Convert image URI to base64
  const convertImageToBase64 = async (imageUri: string): Promise<string> => {
    try {
      const response = await fetch(imageUri);
      const blob = await response.blob();

      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64 = reader.result as string;
          // Remove data URL prefix (data:image/jpeg;base64,)
          const base64Data = base64.split(',')[1];
          resolve(base64Data);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
    } catch (error) {
      console.error('Error converting image to base64:', error);
      throw new Error('Failed to process image');
    }
  };

  // Handle crop health diagnosis
  const handleDiagnosis = async () => {
    if (!selectedImage) {
      Alert.alert(t('cropHealth.noImage'), t('cropHealth.selectImageFirst'));
      return;
    }

    setIsLoading(true);
    try {
      // Convert image to base64 first
      const base64Image = await convertImageToBase64(selectedImage);

      // Call the AI service with base64 image and description
      const response = await aiService.diagnoseCrop(
        base64Image,
        'Image of the crop - to be processed for analysis'
      );

      // Navigate to results screen with the AI agent response
      navigation.navigate('DiagnosisResult', {
        diagnosis: response,
        imageUri: selectedImage,
      });
    } catch (error) {
      console.error('Diagnosis error:', error);
      Alert.alert(t('cropHealth.diagnosisFailed'), t('cropHealth.diagnosisFailedMessage'));
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
          disabled={!selectedImage || isLoading}
          className={`py-4 rounded-xl flex-row justify-center items-center ${
            selectedImage && !isLoading ? 'bg-primary' : 'bg-accent'
          }`}
        >
          <View className="flex-row items-center justify-center">
            {isLoading ? (
              <>
                <Animated.View style={{ transform: [{ rotate: spin }] }}>
                  <Ionicons name="hourglass-outline" size={24} color="black" />
                </Animated.View>
                <Text className="text-black font-bold text-lg ml-3">
                  {t('cropHealth.analyzing')}
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
