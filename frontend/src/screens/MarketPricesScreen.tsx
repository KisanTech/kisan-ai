import React, { useState } from 'react';
import { SafeAreaView, Text, View, ScrollView, Alert } from 'react-native';
import * as FileSystem from 'expo-file-system';
import { VoiceRecorder } from '../components/VoiceRecorder';
import { voiceChatService } from '../services/voiceChatService';

export const MarketPricesScreen: React.FC = () => {
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
            Market Prices
          </Text>
          <Text className="text-sm text-gray-600 text-center">
            Record your voice to get market price information
          </Text>
        </View>

        <View className="items-center mb-6">
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

        <View className="mb-6">
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
      </ScrollView>
    </SafeAreaView>
  );
};
