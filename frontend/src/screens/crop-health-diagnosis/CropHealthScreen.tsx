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
import { RootStackParamList } from '../../types/navigation';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import {
  diagnosisService,
  DiagnosisRequest,
  DiagnosisResponse,
} from '../../services/diagnosisService';

type NavigationProp = StackNavigationProp<RootStackParamList>;

export const CropHealthScreen: React.FC = () => {
  const navigation = useNavigation<NavigationProp>();
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [diagnosis, setDiagnosis] = useState<DiagnosisResponse | null>(null);

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
      // Navigate to results screen instead of setting diagnosis state
      navigation.navigate('DiagnosisResult', {
        diagnosis: response,
        imageUri: selectedImage,
      });
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
                className="w-full h-72 rounded-xl"
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
            <Ionicons name="camera" size={22} color="white" />
            <Text className="text-white font-bold ml-2">Capture</Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={handleGallerySelect}
            className="flex-1 bg-primary py-3 rounded-lg flex-row justify-center items-center"
          >
            <Ionicons name="images" size={22} color="white" />
            <Text className="text-white font-bold ml-2">Gallery</Text>
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
                <Text className="text-black font-bold text-lg ml-3">ANALYZING...</Text>
              </>
            ) : (
              <>
                <Ionicons name="leaf" size={24} color="white" />
                <Text className="text-white font-bold text-lg ml-3">CHECK CROP HEALTH</Text>
              </>
            )}
          </View>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};
