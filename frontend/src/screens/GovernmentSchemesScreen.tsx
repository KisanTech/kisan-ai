import React, { useState } from 'react';
import { SafeAreaView, Text, View, ScrollView, Alert } from 'react-native';
import { useTranslation } from 'react-i18next';
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
        <View className="bg-white border border-gray-200 rounded-lg p-4 mb-8">
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
              buttonText={isProcessing ? t('marketPrices.processing') : t('marketPrices.pleaseAskQuery')}
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
                onError={(error) => {
                  console.error('Response audio playback error:', error);
                  Alert.alert(t('marketPrices.playbackError'), t('marketPrices.playbackErrorMessage'));
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
              <Text className="text-sm text-gray-700">
                {userQuestion}
              </Text>
            </View>
          </View>
        )}

        {response && (
          <View className="mb-6">
            <Text className="text-lg font-semibold text-foreground mb-2">
              {t('marketPrices.response')}
            </Text>
            <View className="bg-green-50 p-4 rounded-lg">
              <Text className="text-sm text-gray-700">
                {response}
              </Text>
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
            <View className="bg-green-50 border border-green-200 rounded-lg p-4 flex-row items-start">
              <Text className="text-2xl mr-3">🌾</Text>
              <View className="flex-1">
                <Text className="text-base font-semibold text-green-800 mb-1">
                  {t('governmentSchemes.agriculturalSubsidies.title')}
                </Text>
                <Text className="text-sm text-green-700">
                  {t('governmentSchemes.agriculturalSubsidies.description')}
                </Text>
              </View>
            </View>

            {/* Farmer Welfare Schemes Card */}
            <View className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex-row items-start">
              <Text className="text-2xl mr-3">👨‍🌾</Text>
              <View className="flex-1">
                <Text className="text-base font-semibold text-blue-800 mb-1">
                  {t('governmentSchemes.farmerWelfare.title')}
                </Text>
                <Text className="text-sm text-blue-700">
                  {t('governmentSchemes.farmerWelfare.description')}
                </Text>
              </View>
            </View>

            {/* Relief & Support Card */}
            <View className="bg-purple-50 border border-purple-200 rounded-lg p-4 flex-row items-start">
              <Text className="text-2xl mr-3">🆘</Text>
              <View className="flex-1">
                <Text className="text-base font-semibold text-purple-800 mb-1">
                  {t('governmentSchemes.reliefSupport.title')}
                </Text>
                <Text className="text-sm text-purple-700">
                  {t('governmentSchemes.reliefSupport.description')}
                </Text>
              </View>
            </View>

            {/* Credit & Loans Card */}
            <View className="bg-orange-50 border border-orange-200 rounded-lg p-4 flex-row items-start">
              <Text className="text-2xl mr-3">💰</Text>
              <View className="flex-1">
                <Text className="text-base font-semibold text-orange-800 mb-1">
                  {t('governmentSchemes.creditLoans.title')}
                </Text>
                <Text className="text-sm text-orange-700">
                  {t('governmentSchemes.creditLoans.description')}
                </Text>
              </View>
            </View>

            {/* Training & Development Card */}
            <View className="bg-teal-50 border border-teal-200 rounded-lg p-4 flex-row items-start">
              <Text className="text-2xl mr-3">📚</Text>
              <View className="flex-1">
                <Text className="text-base font-semibold text-teal-800 mb-1">
                  {t('governmentSchemes.trainingDevelopment.title')}
                </Text>
                <Text className="text-sm text-teal-700">
                  {t('governmentSchemes.trainingDevelopment.description')}
                </Text>
              </View>
            </View>
          </View>
        </View>

        {/* Sample Questions */}
        <View className="mb-8">
          <Text className="text-lg font-semibold text-foreground mb-4">
            {t('governmentSchemes.sampleQuestions.title')}
          </Text>
          <View className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <View className="space-y-3">
              <Text className="text-sm text-gray-700">{t('governmentSchemes.sampleQuestions.question1')}</Text>
              <Text className="text-sm text-gray-700">{t('governmentSchemes.sampleQuestions.question2')}</Text>
              <Text className="text-sm text-gray-700">{t('governmentSchemes.sampleQuestions.question3')}</Text>
              <Text className="text-sm text-gray-700">{t('governmentSchemes.sampleQuestions.question4')}</Text>
              <Text className="text-sm text-gray-700">{t('governmentSchemes.sampleQuestions.question5')}</Text>
              <Text className="text-sm text-gray-700">{t('governmentSchemes.sampleQuestions.question6')}</Text>
            </View>
          </View>
        </View>

        {/* Bottom spacing */}
        <View className="h-8" />
      </ScrollView>
    </SafeAreaView>
  );
};
