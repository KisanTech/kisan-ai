import React, { useState } from 'react';
import { SafeAreaView, Text, View, ScrollView, Alert } from 'react-native';
import { useTranslation } from 'react-i18next';
import * as FileSystem from 'expo-file-system';
import { VoiceRecorder, VoicePlayer } from '../components';
import { voiceChatService } from '../services/voiceChatService';

export const GovernmentSchemesScreen: React.FC = () => {
  const { t } = useTranslation();
  const [audioBase64, setAudioBase64] = useState<string>('');
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordingStatus, setRecordingStatus] = useState<string>(t('marketPrices.readyToRecord'));
  const [transcription, setTranscription] = useState<string>('');
  const [response, setResponse] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const handleAudioRecorded = async (base64Audio: string) => {
    setAudioBase64(base64Audio);
    setIsProcessing(true);
    setRecordingStatus(t('marketPrices.processingAudio'));

    try {
      // Send audio to speech-to-text API
      const speechResult = await voiceChatService.speechToText(base64Audio, 'hi-IN');
      
      setTranscription(speechResult.transcription);
      setRecordingStatus(t('marketPrices.audioTranscribed'));
      
      console.log('Transcription:', speechResult.transcription);
      console.log('Translation:', speechResult.translation);
      console.log('Confidence:', speechResult.confidence);
      
      // Optionally, send the transcribed text to get AI response
      if (speechResult.transcription) {
        setRecordingStatus(t('marketPrices.gettingAIResponse'));
        const aiResponse = await voiceChatService.sendTextMessage(
          speechResult.transcription, 
          'kn-IN'
        );
        
        setResponse(aiResponse.response_text);
        setRecordingStatus(t('marketPrices.responseReceived'));
        
        // Show success alert with transcription and response
        Alert.alert(
          t('marketPrices.voiceProcessingComplete'), 
          `${t('marketPrices.transcription')} ${speechResult.transcription}\n\n${t('marketPrices.response')} ${aiResponse.response_text}`,
          [{ text: t('common.ok') }]
        );
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
            <Text className="text-sm text-gray-600 text-center">
              {t('governmentSchemes.voiceSubtitle')}
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

        {/* Recording Results Section */}
        {audioBase64 && (
          <View className="mt-8">
            <Text className="text-lg font-semibold text-foreground mb-4">
              {t('marketPrices.recordingResults')}
            </Text>
            
            <View className="mb-4">
              <Text className="text-sm font-medium text-gray-700 mb-2 text-center">
                {t('marketPrices.playbackRecordedAudio')}
              </Text>
              <VoicePlayer
                base64Audio={audioBase64}
                onPlay={() => console.log('Playing recorded audio')}
                onPause={() => console.log('Paused audio playback')}
                onError={(error) => {
                  console.error('Audio playback error:', error);
                  Alert.alert(t('marketPrices.playbackError'), t('marketPrices.playbackErrorMessage'));
                }}
                playButtonText={t('marketPrices.playRecording')}
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

        {transcription && (
          <View className="mb-6">
            <Text className="text-lg font-semibold text-foreground mb-2">
              {t('marketPrices.transcription')}
            </Text>
            <View className="bg-blue-50 p-4 rounded-lg">
              <Text className="text-sm text-gray-700">
                {transcription}
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
