import React, { useState } from 'react';
import { SafeAreaView, Text, View, ScrollView, Alert } from 'react-native';
import * as FileSystem from 'expo-file-system';
import { VoiceRecorder, VoicePlayer } from '../components';
import { voiceChatService } from '../services/voiceChatService';

export const GovernmentSchemesScreen: React.FC = () => {
  const [audioBase64, setAudioBase64] = useState<string>('');
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordingStatus, setRecordingStatus] = useState<string>('Ready to record');
  const [transcription, setTranscription] = useState<string>('');
  const [response, setResponse] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const handleAudioRecorded = async (base64Audio: string) => {
    setAudioBase64(base64Audio);
    setIsProcessing(true);
    setRecordingStatus('Processing audio...');

    try {
      // Send audio to speech-to-text API
      const speechResult = await voiceChatService.speechToText(base64Audio, 'hi-IN');
      
      setTranscription(speechResult.transcription);
      setRecordingStatus('Audio transcribed successfully!');
      
      console.log('Transcription:', speechResult.transcription);
      console.log('Translation:', speechResult.translation);
      console.log('Confidence:', speechResult.confidence);
      
      // Optionally, send the transcribed text to get AI response
      if (speechResult.transcription) {
        setRecordingStatus('Getting AI response...');
        const aiResponse = await voiceChatService.sendTextMessage(
          speechResult.transcription, 
          'kn-IN'
        );
        
        setResponse(aiResponse.response_text);
        setRecordingStatus('Response received!');
        
        // Show success alert with transcription and response
        Alert.alert(
          'Voice Processing Complete', 
          `Transcription: ${speechResult.transcription}\n\nResponse: ${aiResponse.response_text}`,
          [{ text: 'OK' }]
        );
      }

    } catch (error) {
      console.error('Failed to process audio:', error);
      setRecordingStatus('Error: Failed to process audio');
      Alert.alert('Processing Error', 'Failed to process the audio. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRecordingStart = () => {
    setIsRecording(true);
    setRecordingStatus('Recording in progress...');
    setAudioBase64(''); // Clear previous recording
  };

  const handleRecordingStop = () => {
    setIsRecording(false);
    setRecordingStatus('Processing recording...');
  };

  const handleRecordingError = (error: string) => {
    setIsRecording(false);
    setRecordingStatus(`Error: ${error}`);
    Alert.alert('Recording Error', error);
  };

  return (
    <SafeAreaView className="flex-1 bg-background font-sans">
      <ScrollView className="flex-1 p-4">
        <View className="items-center mb-8">
          <Text className="text-2xl font-bold text-foreground tracking-tighter mb-2">
            🏛️ Government Schemes
          </Text>
          <Text className="text-sm text-gray-600 text-center">
            Get information about agricultural schemes, farmer welfare, and relief programs
          </Text>
        </View>

        {/* Voice Recording Section */}
        <View className="bg-white border border-gray-200 rounded-lg p-4 mb-8">
          <View className="items-center mb-4">
            <Text className="text-lg font-semibold text-foreground mb-2">
              🎤 Voice Assistant
            </Text>
            <Text className="text-sm text-gray-600 text-center">
              Speak in Hindi or Kannada to get instant scheme information
            </Text>
          </View>

          <View className="items-center">
            <VoiceRecorder
              onAudioRecorded={handleAudioRecorded}
              onRecordingStart={handleRecordingStart}
              onRecordingStop={handleRecordingStop}
              onError={handleRecordingError}
              disabled={isProcessing}
              buttonText={isProcessing ? "🔄 Processing..." : "🎤 Start Recording"}
              recordingText="🔴 Recording..."
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
              Status:
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
                Please wait while we process your audio...
              </Text>
            )}
          </View>
        </View>

        {/* Feature Information Cards */}
        <View className="mb-8">
          <Text className="text-lg font-semibold text-foreground mb-4">
            What You Can Get:
          </Text>
          
          <View className="space-y-4">
            {/* Agricultural Subsidies Card */}
            <View className="bg-green-50 border border-green-200 rounded-lg p-4 flex-row items-start">
              <Text className="text-2xl mr-3">🌾</Text>
              <View className="flex-1">
                <Text className="text-base font-semibold text-green-800 mb-1">
                  Agricultural Subsidies
                </Text>
                <Text className="text-sm text-green-700">
                  Learn about fertilizer subsidies, seed subsidies, equipment purchase schemes, and irrigation support programs available in your region.
                </Text>
              </View>
            </View>

            {/* Farmer Welfare Schemes Card */}
            <View className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex-row items-start">
              <Text className="text-2xl mr-3">👨‍🌾</Text>
              <View className="flex-1">
                <Text className="text-base font-semibold text-blue-800 mb-1">
                  Farmer Welfare Programs
                </Text>
                <Text className="text-sm text-blue-700">
                  Get details about PM-KISAN, Pradhan Mantri Fasal Bima Yojana, pension schemes, and health insurance for farmers.
                </Text>
              </View>
            </View>

            {/* Relief & Support Card */}
            <View className="bg-purple-50 border border-purple-200 rounded-lg p-4 flex-row items-start">
              <Text className="text-2xl mr-3">🆘</Text>
              <View className="flex-1">
                <Text className="text-base font-semibold text-purple-800 mb-1">
                  Relief & Emergency Support
                </Text>
                <Text className="text-sm text-purple-700">
                  Information about crop loss compensation, natural disaster relief, debt relief programs, and emergency financial assistance.
                </Text>
              </View>
            </View>

            {/* Credit & Loans Card */}
            <View className="bg-orange-50 border border-orange-200 rounded-lg p-4 flex-row items-start">
              <Text className="text-2xl mr-3">💰</Text>
              <View className="flex-1">
                <Text className="text-base font-semibold text-orange-800 mb-1">
                  Credit & Loan Schemes
                </Text>
                <Text className="text-sm text-orange-700">
                  Find out about KCC (Kisan Credit Card), agricultural loans, interest subsidies, and microfinance options for farmers.
                </Text>
              </View>
            </View>

            {/* Training & Development Card */}
            <View className="bg-teal-50 border border-teal-200 rounded-lg p-4 flex-row items-start">
              <Text className="text-2xl mr-3">📚</Text>
              <View className="flex-1">
                <Text className="text-base font-semibold text-teal-800 mb-1">
                  Training & Skill Development
                </Text>
                <Text className="text-sm text-teal-700">
                  Learn about agricultural training programs, modern farming techniques, and skill development initiatives for farmers.
                </Text>
              </View>
            </View>
          </View>
        </View>

        {/* Sample Questions */}
        <View className="mb-8">
          <Text className="text-lg font-semibold text-foreground mb-4">
            💬 Ask Questions Like:
          </Text>
          <View className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <View className="space-y-3">
              <Text className="text-sm text-gray-700">• "How can I apply for PM-KISAN scheme?"</Text>
              <Text className="text-sm text-gray-700">• "What fertilizer subsidies are available?"</Text>
              <Text className="text-sm text-gray-700">• "Tell me about crop insurance schemes"</Text>
              <Text className="text-sm text-gray-700">• "How to get Kisan Credit Card?"</Text>
              <Text className="text-sm text-gray-700">• "What relief is available for crop damage?"</Text>
              <Text className="text-sm text-gray-700">• "Are there any schemes for organic farming?"</Text>
            </View>
          </View>
        </View>

        {/* Recording Results Section */}
        {audioBase64 && (
          <View className="mt-8">
            <Text className="text-lg font-semibold text-foreground mb-4">
              📱 Recording Results
            </Text>
            
            <View className="mb-4">
              <Text className="text-sm font-medium text-gray-700 mb-2 text-center">
                Playback Recorded Audio
              </Text>
              <VoicePlayer
                base64Audio={audioBase64}
                onPlay={() => console.log('Playing recorded audio')}
                onPause={() => console.log('Paused audio playback')}
                onError={(error) => {
                  console.error('Audio playback error:', error);
                  Alert.alert('Playback Error', 'Failed to play the recorded audio.');
                }}
                playButtonText="▶ Play Recording"
                pauseButtonText="⏸ Pause"
                replayButtonText="🔄 Replay"
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
              Recorded Audio (Base64):
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
                  Full length: {audioBase64.length} characters
                </Text>
              )}
            </View>
          </View>
        )}

        {transcription && (
          <View className="mb-6">
            <Text className="text-lg font-semibold text-foreground mb-2">
              Transcription:
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
              Response:
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
