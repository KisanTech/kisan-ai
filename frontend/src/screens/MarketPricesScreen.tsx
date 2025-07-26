import React, { useState } from 'react';
import { SafeAreaView, Text, View, ScrollView, Alert } from 'react-native';
import { useTranslation } from 'react-i18next';
import * as FileSystem from 'expo-file-system';
import { VoiceRecorder, VoicePlayer } from '../components';
import { voiceChatService } from '../services/voiceChatService';
import { useLanguage } from '../i18n/LanguageContext';
import { getSpeechRecognitionCode, getTextApiCode } from '../config/languages';

export const MarketPricesScreen: React.FC = () => {
  const { t } = useTranslation();
  const { currentLanguage } = useLanguage();
  const [audioBase64, setAudioBase64] = useState<string>('');
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordingStatus, setRecordingStatus] = useState<string>(t('marketPrices.readyToRecord'));
  const [userQuestion, setUserQuestion] = useState<string>('');
  const [response, setResponse] = useState<string>('');
  const [responseAudioData, setResponseAudioData] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const handleAudioRecorded = async (base64Audio: string) => {
    setAudioBase64(base64Audio);
    setIsProcessing(true);
    setRecordingStatus(t('marketPrices.processingAudio'));

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
        setRecordingStatus(t('marketPrices.responseReceived'));
        
        console.log('Original Transcript:', speechResult.original_transcript);
        console.log('Translated Text:', speechResult.translated_text);
        console.log('Agent Response:', speechResult.agent_response);
        console.log('Agent Response Translated:', speechResult.agent_response_translated);
        console.log('Confidence:', speechResult.transcription_confidence);
        
        // Show success alert with user question and response
        Alert.alert(
          t('marketPrices.voiceProcessingComplete'), 
          `${t('marketPrices.userQuestion')} ${speechResult.original_transcript}\n\n${t('marketPrices.response')} ${speechResult.agent_response_translated}`,
          [{ text: t('common.ok') }]
        );
      } else {
        throw new Error(speechResult.error || 'Unknown error occurred');
      }

    } catch (error) {
      console.error('Failed to process audio:', error);
      setRecordingStatus(t('marketPrices.errorProcessAudio'));
      Alert.alert(t('marketPrices.processingError'), t('marketPrices.processingErrorMessage'));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRecordingStart = () => {
    setIsRecording(true);
    setRecordingStatus(t('marketPrices.recordingInProgress'));
    setAudioBase64(''); // Clear previous recording
  };

  const handleRecordingStop = () => {
    setIsRecording(false);
    setRecordingStatus(t('marketPrices.processingRecording'));
  };

  const handleRecordingError = (error: string) => {
    setIsRecording(false);
    setRecordingStatus(`${t('marketPrices.errorProcessAudio')}: ${error}`);
    Alert.alert(t('marketPrices.recordingError'), error);
  };

  return (
    <SafeAreaView className="flex-1 bg-background font-sans">
      <ScrollView className="flex-1 p-4">
        <View className="items-center mb-8">
          <Text className="text-2xl font-bold text-foreground tracking-tighter mb-2">
            {t('marketPrices.title')}
          </Text>
          <Text className="text-sm text-gray-600 text-center">
            {t('marketPrices.subtitle')}
          </Text>
        </View>

        {/* Voice Recording Section */}
        <View className="bg-white border border-gray-200 rounded-lg p-4 mb-8">
          <View className="items-center mb-4">
            <Text className="text-lg font-semibold text-foreground mb-2">
              {t('marketPrices.voiceAssistant')}
            </Text>
            <Text className="text-sm text-gray-600 text-center">
              {t('marketPrices.voiceSubtitle')}
            </Text>
          </View>

          <View className="items-center">
            <VoiceRecorder
              onAudioRecorded={handleAudioRecorded}
              onRecordingStart={handleRecordingStart}
              onRecordingStop={handleRecordingStop}
              onError={handleRecordingError}
              disabled={isProcessing}
              buttonText={isProcessing ? t('marketPrices.processing') : t('marketPrices.startRecording')}
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

          <View className="mb-2">
            <Text className="text-lg font-semibold text-foreground mb-2">
              {t('marketPrices.status')}:
            </Text>
            <Text className={`text-sm ${
              isRecording ? 'text-red-600' : 
              isProcessing ? 'text-blue-600' : 
              'text-gray-600'
            }`}>
              {recordingStatus}
            </Text>
            {isProcessing && (
              <Text className="text-xs text-blue-500 mt-1">
                {t('marketPrices.pleaseWait')}
              </Text>
            )}
          </View>
        </View>

        {/* Feature Information Cards */}
        <View className="mb-8">
          <Text className="text-lg font-semibold text-foreground mb-4">
            {t('marketPrices.whatYouCanGet')}
          </Text>
          
          <View className="space-y-4">
            {/* Current Prices Card */}
            <View className="bg-green-50 border border-green-200 rounded-lg p-4 flex-row items-start">
              <Text className="text-2xl mr-3">💰</Text>
              <View className="flex-1">
                <Text className="text-base font-semibold text-green-800 mb-1">
                  {t('marketPrices.currentCropPrices.title')}
                </Text>
                <Text className="text-sm text-green-700">
                  {t('marketPrices.currentCropPrices.description')}
                </Text>
              </View>
            </View>

            {/* Price Trends Card */}
            <View className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex-row items-start">
              <Text className="text-2xl mr-3">📊</Text>
              <View className="flex-1">
                <Text className="text-base font-semibold text-blue-800 mb-1">
                  {t('marketPrices.priceTrends.title')}
                </Text>
                <Text className="text-sm text-blue-700">
                  {t('marketPrices.priceTrends.description')}
                </Text>
              </View>
            </View>

            {/* Market Insights Card */}
            <View className="bg-purple-50 border border-purple-200 rounded-lg p-4 flex-row items-start">
              <Text className="text-2xl mr-3">🎯</Text>
              <View className="flex-1">
                <Text className="text-base font-semibold text-purple-800 mb-1">
                  {t('marketPrices.marketInsights.title')}
                </Text>
                <Text className="text-sm text-purple-700">
                  {t('marketPrices.marketInsights.description')}
                </Text>
              </View>
            </View>

            {/* Regional Comparison Card */}
            <View className="bg-orange-50 border border-orange-200 rounded-lg p-4 flex-row items-start">
              <Text className="text-2xl mr-3">🗺️</Text>
              <View className="flex-1">
                <Text className="text-base font-semibold text-orange-800 mb-1">
                  {t('marketPrices.regionalComparison.title')}
                </Text>
                <Text className="text-sm text-orange-700">
                  {t('marketPrices.regionalComparison.description')}
                </Text>
              </View>
            </View>
          </View>
        </View>

        {/* Sample Questions */}
        <View className="mb-8">
          <Text className="text-lg font-semibold text-foreground mb-4">
            {t('marketPrices.sampleQuestions.title')}
          </Text>
          <View className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <View className="space-y-3">
              <Text className="text-sm text-gray-700">{t('marketPrices.sampleQuestions.question1')}</Text>
              <Text className="text-sm text-gray-700">{t('marketPrices.sampleQuestions.question2')}</Text>
              <Text className="text-sm text-gray-700">{t('marketPrices.sampleQuestions.question3')}</Text>
              <Text className="text-sm text-gray-700">{t('marketPrices.sampleQuestions.question4')}</Text>
              <Text className="text-sm text-gray-700">{t('marketPrices.sampleQuestions.question5')}</Text>
            </View>
          </View>
        </View>

        {/* Recording Results Section */}
        {responseAudioData && (
          <View className="mt-8">
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

        {audioBase64 && (
          <View className="mb-6">
            <Text className="text-lg font-semibold text-foreground mb-2">
              {t('marketPrices.recordedAudioBase64')}
            </Text>
            <View className="bg-gray-100 p-4 rounded-lg">
              <Text className="text-xs font-mono text-gray-700 leading-5">
                {audioBase64.length > 200 
                  ? `${audioBase64.substring(0, 200)}...` 
                  : audioBase64
                }
              </Text>
              {audioBase64.length > 200 && (
                <Text className="text-xs text-gray-500 mt-2">
                  {t('marketPrices.fullLength')}: {audioBase64.length} {t('marketPrices.characters')}
                </Text>
              )}
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

        {/* Bottom spacing */}
        <View className="h-8" />
      </ScrollView>
    </SafeAreaView>
  );
};
