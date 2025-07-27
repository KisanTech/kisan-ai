import React, { useState } from 'react';
import { SafeAreaView, Text, View, ScrollView, Alert } from 'react-native';
import { useTranslation } from 'react-i18next';
import { Ionicons } from '@expo/vector-icons';
import * as FileSystem from 'expo-file-system';
import { VoiceRecorder, VoicePlayer } from '../components';
import { voiceChatService } from '../services/voiceChatService';
import { useLanguage } from '../i18n/LanguageContext';
import { getSpeechRecognitionCode } from '../config/languages';

export const GovernmentSchemesScreen: React.FC = () => {
  const { t } = useTranslation();
  const { currentLanguage } = useLanguage();
  const [audioBase64, setAudioBase64] = useState<string>('');
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [userQuestion, setUserQuestion] = useState<string>('');
  const [response, setResponse] = useState<string>('');
  const [responseAudioData, setResponseAudioData] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const handleAudioRecorded = async (base64Audio: string) => {
    setAudioBase64(base64Audio);
    setIsProcessing(true);

    try {
      // Get language codes based on current language
      const speechLanguageCode = getSpeechRecognitionCode(currentLanguage);

      // Send audio to speech-to-text API
      const speechResult = await voiceChatService.speechToText(base64Audio, speechLanguageCode);

      // Handle the new response format
      if (speechResult.success) {
        setUserQuestion(speechResult.original_transcript);
        setResponse(speechResult.agent_response_translated);
        setResponseAudioData(speechResult.response_audio_data);

        console.log('Original Transcript:', speechResult.original_transcript);
        console.log('Translated Text:', speechResult.translated_text);
        console.log('Agent Response:', speechResult.agent_response);
        console.log('Agent Response Translated:', speechResult.agent_response_translated);
        console.log('Confidence:', speechResult.transcription_confidence);
      } else {
        throw new Error(speechResult.error || 'Unknown error occurred');
      }
    } catch (error) {
      console.error('Failed to process audio:', error);
      Alert.alert(t('marketPrices.processingError'), t('marketPrices.processingErrorMessage'));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRecordingStart = () => {
    setIsRecording(true);
    setAudioBase64(''); // Clear previous recording
  };

  const handleRecordingStop = () => {
    setIsRecording(false);
  };

  const handleRecordingError = (error: string) => {
    setIsRecording(false);
    Alert.alert(t('marketPrices.recordingError'), error);
  };

  return (
    <SafeAreaView className="flex-1 bg-background font-sans">
      <ScrollView className="flex-1 p-4">
        <View className="items-center mb-8">
          <Text className="text-2xl font-bold text-foreground tracking-tighter mb-2">
            {t('governmentSchemes.title')}
          </Text>
          <Text className="text-sm text-gray-600 text-center">
            {t('governmentSchemes.subtitle')}
          </Text>
        </View>

        {/* Voice Recording Section */}
        <View className="bg-cardBackground border border-gray-200 rounded-lg p-4 mb-8">
          <View className="items-center mb-4">
            <Text className="text-lg font-semibold text-foreground mb-2">
              {t('governmentSchemes.voiceAssistant')}
            </Text>
          </View>

          <View className="items-center">
            <VoiceRecorder
              onAudioRecorded={handleAudioRecorded}
              onRecordingStart={handleRecordingStart}
              onRecordingStop={handleRecordingStop}
              onError={handleRecordingError}
              disabled={isProcessing}
              buttonText={
                isProcessing ? t('marketPrices.processing') : t('marketPrices.pleaseAskQuery')
              }
              recordingText={t('marketPrices.recording')}
              customStyles={{
                container: { marginVertical: 20 },
                button: {
                  paddingHorizontal: 32,
                  paddingVertical: 16,
                  borderRadius: 30,
                  opacity: isProcessing ? 0.6 : 1,
                },
              }}
            />
          </View>
        </View>

        {/* Recording Results Section - Moved to top */}
        {responseAudioData && (
          <View className="mb-8">
            <Text className="text-lg font-semibold text-foreground mb-4">
              {t('marketPrices.recordingResults')}
            </Text>

            <View className="mb-4">
              <Text className="text-sm font-medium text-gray-700 mb-2 text-center">
                {t('marketPrices.playResponseAudio')}
              </Text>
              <VoicePlayer
                base64Audio={responseAudioData}
                onPlay={() => console.log('Playing response audio')}
                onPause={() => console.log('Paused response audio playback')}
                onError={error => {
                  console.error('Response audio playback error:', error);
                  Alert.alert(
                    t('marketPrices.playbackError'),
                    t('marketPrices.playbackErrorMessage')
                  );
                }}
                playButtonText={t('marketPrices.playResponse')}
                pauseButtonText={t('marketPrices.pause')}
                replayButtonText={t('marketPrices.replay')}
                customStyles={{
                  container: { marginVertical: 10 },
                  button: {
                    paddingHorizontal: 24,
                    paddingVertical: 12,
                    borderRadius: 25,
                  },
                }}
              />
            </View>
          </View>
        )}

        {userQuestion && (
          <View className="mb-6">
            <Text className="text-lg font-semibold text-foreground mb-2">
              {t('marketPrices.userQuestion')}
            </Text>
            <View className="bg-blue-50 p-4 rounded-lg">
              <Text className="text-sm text-gray-700">{userQuestion}</Text>
            </View>
          </View>
        )}

        {response && (
          <View className="mb-6">
            <Text className="text-lg font-semibold text-foreground mb-2">
              {t('marketPrices.response')}
            </Text>
            <View className="bg-green-50 p-4 rounded-lg">
              <Text className="text-sm text-gray-700">{response}</Text>
            </View>
          </View>
        )}

        {/* Feature Information Cards */}
        <View className="mb-8">
          <Text className="text-lg font-semibold text-foreground mb-4">
            {t('governmentSchemes.whatYouCanGet')}
          </Text>

          <View className="space-y-4">
            {/* Agricultural Subsidies Card */}
            <View
              className="bg-white border border-green-200 rounded-xl p-5 flex-row items-center shadow-sm"
              style={{
                shadowColor: '#000',
                shadowOffset: { width: 0, height: 2 },
                shadowOpacity: 0.1,
                shadowRadius: 4,
                elevation: 3,
              }}
            >
              <View className="w-12 h-12 bg-primary rounded-full items-center justify-center mr-4">
                <Ionicons name="leaf" size={24} color="#ffffff" />
              </View>
              <View className="flex-1">
                <Text className="text-base font-bold text-foreground mb-1">
                  {t('governmentSchemes.agriculturalSubsidies.title')}
                </Text>
                <Text className="text-sm text-green-700 leading-5">
                  {t('governmentSchemes.agriculturalSubsidies.description')}
                </Text>
              </View>
            </View>

            {/* Farmer Welfare Schemes Card */}
            <View
              className="bg-white border border-green-200 rounded-xl p-5 flex-row items-center shadow-sm"
              style={{
                shadowColor: '#000',
                shadowOffset: { width: 0, height: 2 },
                shadowOpacity: 0.1,
                shadowRadius: 4,
                elevation: 3,
              }}
            >
              <View className="w-12 h-12 bg-secondary rounded-full items-center justify-center mr-4">
                <Ionicons name="people" size={24} color="#ffffff" />
              </View>
              <View className="flex-1">
                <Text className="text-base font-bold text-foreground mb-1">
                  {t('governmentSchemes.farmerWelfare.title')}
                </Text>
                <Text className="text-sm text-green-700 leading-5">
                  {t('governmentSchemes.farmerWelfare.description')}
                </Text>
              </View>
            </View>

            {/* Relief & Support Card */}
            <View
              className="bg-white border border-green-200 rounded-xl p-5 flex-row items-center shadow-sm"
              style={{
                shadowColor: '#000',
                shadowOffset: { width: 0, height: 2 },
                shadowOpacity: 0.1,
                shadowRadius: 4,
                elevation: 3,
              }}
            >
              <View className="w-12 h-12 bg-primary rounded-full items-center justify-center mr-4">
                <Ionicons name="shield-checkmark" size={24} color="#ffffff" />
              </View>
              <View className="flex-1">
                <Text className="text-base font-bold text-foreground mb-1">
                  {t('governmentSchemes.reliefSupport.title')}
                </Text>
                <Text className="text-sm text-green-700 leading-5">
                  {t('governmentSchemes.reliefSupport.description')}
                </Text>
              </View>
            </View>

            {/* Credit & Loans Card */}
            <View
              className="bg-white border border-green-200 rounded-xl p-5 flex-row items-center shadow-sm"
              style={{
                shadowColor: '#000',
                shadowOffset: { width: 0, height: 2 },
                shadowOpacity: 0.1,
                shadowRadius: 4,
                elevation: 3,
              }}
            >
              <View className="w-12 h-12 bg-secondary rounded-full items-center justify-center mr-4">
                <Ionicons name="wallet" size={24} color="#ffffff" />
              </View>
              <View className="flex-1">
                <Text className="text-base font-bold text-foreground mb-1">
                  {t('governmentSchemes.creditLoans.title')}
                </Text>
                <Text className="text-sm text-green-700 leading-5">
                  {t('governmentSchemes.creditLoans.description')}
                </Text>
              </View>
            </View>

            {/* Training & Development Card */}
            <View
              className="bg-white border border-green-200 rounded-xl p-5 flex-row items-center shadow-sm"
              style={{
                shadowColor: '#000',
                shadowOffset: { width: 0, height: 2 },
                shadowOpacity: 0.1,
                shadowRadius: 4,
                elevation: 3,
              }}
            >
              <View className="w-12 h-12 bg-primary rounded-full items-center justify-center mr-4">
                <Ionicons name="school" size={24} color="#ffffff" />
              </View>
              <View className="flex-1">
                <Text className="text-base font-bold text-foreground mb-1">
                  {t('governmentSchemes.trainingDevelopment.title')}
                </Text>
                <Text className="text-sm text-green-700 leading-5">
                  {t('governmentSchemes.trainingDevelopment.description')}
                </Text>
              </View>
            </View>
          </View>
        </View>

        {/* Sample Questions */}
        <View className="mb-8">
          <View
            className="bg-white border border-green-200 rounded-xl p-5 shadow-sm"
            style={{
              shadowColor: '#000',
              shadowOffset: { width: 0, height: 2 },
              shadowOpacity: 0.1,
              shadowRadius: 4,
              elevation: 3,
            }}
          >
            <View className="flex-row items-center mb-4">
              <View className="w-10 h-10 bg-primary rounded-full items-center justify-center mr-3">
                <Ionicons name="chatbubble-ellipses" size={20} color="#ffffff" />
              </View>
              <Text className="text-base font-bold text-foreground">
                {t('governmentSchemes.sampleQuestions.title')}
              </Text>
            </View>
            <View className="space-y-4">
              <View className="flex-row items-start">
                <View className="w-6 h-6 bg-green-100 rounded-full items-center justify-center mr-3 mt-0.5">
                  <Text className="text-xs font-bold text-primary">•</Text>
                </View>
                <Text className="text-sm text-green-800 flex-1 leading-5">
                  {t('governmentSchemes.sampleQuestions.question1')}
                </Text>
              </View>
              <View className="flex-row items-start">
                <View className="w-6 h-6 bg-green-100 rounded-full items-center justify-center mr-3 mt-0.5">
                  <Text className="text-xs font-bold text-primary">•</Text>
                </View>
                <Text className="text-sm text-green-800 flex-1 leading-5">
                  {t('governmentSchemes.sampleQuestions.question2')}
                </Text>
              </View>
              <View className="flex-row items-start">
                <View className="w-6 h-6 bg-green-100 rounded-full items-center justify-center mr-3 mt-0.5">
                  <Text className="text-xs font-bold text-primary">•</Text>
                </View>
                <Text className="text-sm text-green-800 flex-1 leading-5">
                  {t('governmentSchemes.sampleQuestions.question3')}
                </Text>
              </View>
              <View className="flex-row items-start">
                <View className="w-6 h-6 bg-green-100 rounded-full items-center justify-center mr-3 mt-0.5">
                  <Text className="text-xs font-bold text-primary">•</Text>
                </View>
                <Text className="text-sm text-green-800 flex-1 leading-5">
                  {t('governmentSchemes.sampleQuestions.question4')}
                </Text>
              </View>
              <View className="flex-row items-start">
                <View className="w-6 h-6 bg-green-100 rounded-full items-center justify-center mr-3 mt-0.5">
                  <Text className="text-xs font-bold text-primary">•</Text>
                </View>
                <Text className="text-sm text-green-800 flex-1 leading-5">
                  {t('governmentSchemes.sampleQuestions.question5')}
                </Text>
              </View>
              <View className="flex-row items-start">
                <View className="w-6 h-6 bg-green-100 rounded-full items-center justify-center mr-3 mt-0.5">
                  <Text className="text-xs font-bold text-primary">•</Text>
                </View>
                <Text className="text-sm text-green-800 flex-1 leading-5">
                  {t('governmentSchemes.sampleQuestions.question6')}
                </Text>
              </View>
            </View>
          </View>
        </View>

        {/* Bottom spacing */}
        <View className="h-8" />
      </ScrollView>
    </SafeAreaView>
  );
};
