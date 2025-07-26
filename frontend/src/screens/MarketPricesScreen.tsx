import React, { useState } from 'react';
import { SafeAreaView, Text, View, ScrollView, Alert } from 'react-native';
import * as FileSystem from 'expo-file-system';
import { VoiceRecorder } from '../components/VoiceRecorder';

export const MarketPricesScreen: React.FC = () => {
  const [audioBase64, setAudioBase64] = useState<string>('');
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordingStatus, setRecordingStatus] = useState<string>('Ready to record');
  const [savedFilePath, setSavedFilePath] = useState<string>('');

  const handleAudioRecorded = async (base64Audio: string) => {
    setAudioBase64(base64Audio);
    
    setRecordingStatus('Processing and saving recording...');

    try {
      // Create a unique filename with timestamp
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const fileName = `voice_recording_${timestamp}.wav`;
      const filePath = `${FileSystem.documentDirectory}${fileName}`;

      // Save the base64 audio data to a local file
      await FileSystem.writeAsStringAsync(filePath, base64Audio, {
        encoding: FileSystem.EncodingType.Base64,
      });

      setSavedFilePath(filePath);
      setRecordingStatus('Recording saved successfully!');
      
      console.log('Audio file saved to:', filePath);
      
      // Show success alert with file location
      Alert.alert(
        'Recording Saved', 
        `Audio file saved to:\n${fileName}`,
        [{ text: 'OK' }]
      );

    } catch (error) {
      console.error('Failed to save audio file:', error);
      setRecordingStatus('Error: Failed to save recording');
      Alert.alert('Save Error', 'Failed to save the audio file to device storage.');
    }
  };

  const handleRecordingStart = () => {
    setIsRecording(true);
    setRecordingStatus('Recording in progress...');
    setAudioBase64(''); // Clear previous recording
    setSavedFilePath(''); // Clear previous file path
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
            buttonText="🎤 Start Recording"
            recordingText="🔴 Recording..."
            customStyles={{
              container: { marginVertical: 20 },
              button: { 
                paddingHorizontal: 32,
                paddingVertical: 16,
                borderRadius: 30,
              },
            }}
          />
        </View>

        <View className="mb-6">
          <Text className="text-lg font-semibold text-foreground mb-2">
            Status:
          </Text>
          <Text className={`text-sm ${isRecording ? 'text-red-600' : 'text-gray-600'}`}>
            {recordingStatus}
          </Text>
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

        {audioBase64 && (
          <View className="mb-6">
            <Text className="text-lg font-semibold text-foreground mb-2">
              Audio Info:
            </Text>
            <View className="bg-blue-50 p-4 rounded-lg">
              <Text className="text-sm text-gray-700">
                ✅ Audio recorded successfully
              </Text>
              <Text className="text-sm text-gray-700">
                📊 Size: {Math.round(audioBase64.length * 0.75)} bytes (estimated)
              </Text>
              <Text className="text-sm text-gray-700">
                🔢 Base64 length: {audioBase64.length} characters
              </Text>
            </View>
          </View>
        )}

        {savedFilePath && (
          <View className="mb-6">
            <Text className="text-lg font-semibold text-foreground mb-2">
              Saved File:
            </Text>
            <View className="bg-green-50 p-4 rounded-lg">
              <Text className="text-sm text-gray-700">
                💾 File saved to device storage
              </Text>
              <Text className="text-xs font-mono text-gray-600 mt-2">
                {savedFilePath}
              </Text>
              <Text className="text-xs text-gray-500 mt-2">
                📁 Location: Documents directory
              </Text>
              <Text className="text-xs text-gray-500">
                🎵 Format: WAV audio file
              </Text>
            </View>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};
