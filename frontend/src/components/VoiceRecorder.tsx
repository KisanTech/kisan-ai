import React, { useState, useEffect, useRef } from 'react';
import { View, TouchableOpacity, Text, Platform, Alert, StyleSheet } from 'react-native';
import {
  useAudioRecorder,
  AudioModule,
  RecordingPresets,
  setAudioModeAsync,
  useAudioRecorderState,
} from 'expo-audio';
import * as FileSystem from 'expo-file-system';
import { VoiceRecorderProps, RecordingState } from '../types';

export const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  onAudioRecorded,
  onRecordingStart,
  onRecordingStop,
  onError,
  customStyles = {},
  buttonText = 'Start Recording',
  recordingText = 'Recording...',
}) => {
  const [permissionStatus, setPermissionStatus] = useState<'undetermined' | 'granted' | 'denied'>('undetermined');
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Use the proper expo-audio hooks
  const audioRecorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
  const recorderState = useAudioRecorderState(audioRecorder);
  const isRecording = recorderState?.isRecording ?? false;

  // Request audio recording permissions
  const requestPermissions = async () => {
    try {
      const status = await AudioModule.requestRecordingPermissionsAsync();
      setPermissionStatus(status.granted ? 'granted' : 'denied');
      
      if (!status.granted) {
        const errorMsg = 'Audio recording permission denied. Please enable microphone access in your device settings.';
        onError?.(errorMsg);
        Alert.alert('Permission Required', errorMsg);
        return false;
      }
      
      return true;
    } catch (error) {
      const errorMsg = 'Failed to request audio permissions';
      console.error(errorMsg, error);
      onError?.(errorMsg);
      setPermissionStatus('denied');
      return false;
    }
  };

  // Convert audio file to Base64
  const convertToBase64 = async (uri: string): Promise<string> => {
    try {
      const base64 = await FileSystem.readAsStringAsync(uri, {
        encoding: FileSystem.EncodingType.Base64,
      });
      return base64;
    } catch (error) {
      console.error('Error converting audio to base64:', error);
      throw new Error('Failed to convert audio to base64');
    }
  };

  // Start recording
  const startRecording = async () => {
    try {
      // Check permissions first
      if (permissionStatus !== 'granted') {
        const hasPermission = await requestPermissions();
        if (!hasPermission) return;
      }

      // Set audio mode for recording
      await setAudioModeAsync({
        playsInSilentMode: true,
        allowsRecording: true,
      });

      // Prepare and start recording using the hook-based approach
      await audioRecorder.prepareToRecordAsync();
      await audioRecorder.record();
      
      console.log('recording started');
      onRecordingStart?.();

      // Auto-stop recording after 60 seconds (safety measure)
      timeoutRef.current = setTimeout(() => {
        stopRecording();
      }, 60000);

    } catch (error) {
      const errorMsg = 'Failed to start recording';
      console.error(errorMsg, error);
      onError?.(errorMsg);
      
      // Show specific error message for simulator
      if (Platform.OS === 'ios' && __DEV__) {
        Alert.alert(
          'Simulator Limitation', 
          'Audio recording typically does not work in iOS Simulator. Please test on a physical iOS device for full functionality.'
        );
      }
    }
  };

  // Stop recording
  const stopRecording = async () => {
    try {
      if (!audioRecorder) {
        console.warn('No audio recorder found to stop');
        return;
      }

      // Clear auto-stop timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }

      // Stop the recording and get the URI
      await audioRecorder.stop();
      const uri = audioRecorder.uri;

      onRecordingStop?.();

      if (uri) {
        // Convert to base64 and return via callback
        const base64Audio = await convertToBase64(uri);
        onAudioRecorded(base64Audio);

        // Clean up the temporary file
        try {
          await FileSystem.deleteAsync(uri, { idempotent: true });
        } catch (deleteError) {
          console.warn('Failed to delete temporary audio file:', deleteError);
        }
      } else {
        const errorMsg = 'Recording URI not found';
        console.error(errorMsg);
        onError?.(errorMsg);
      }

    } catch (error) {
      const errorMsg = 'Failed to stop recording';
      console.error(errorMsg, error);
      onError?.(errorMsg);
    }
  };

  // Toggle recording
  const toggleRecording = async () => {
    if (isRecording) {
      await stopRecording();
    } else {
      await startRecording();
    }
  };

  // Request permissions and setup audio mode on mount
  useEffect(() => {
    const setupAudio = async () => {
      await requestPermissions();
      
      try {
        await setAudioModeAsync({
          playsInSilentMode: true,
          allowsRecording: true,
        });
      } catch (error) {
        console.warn('Failed to set audio mode:', error);
      }
    };
    
    setupAudio();
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (audioRecorder && isRecording) {
        audioRecorder.stop().catch(console.error);
      }
    };
  }, [audioRecorder, isRecording]);

  // Determine button style and text
  const buttonStyle = [
    styles.button,
    customStyles.button,
    isRecording && styles.buttonRecording,
    isRecording && customStyles.buttonRecording,
  ];

  const textStyle = [
    styles.text,
    customStyles.text,
    isRecording && styles.textRecording,
    isRecording && customStyles.textRecording,
  ];

  const displayText = isRecording ? recordingText : buttonText;

  return (
    <View style={[styles.container, customStyles.container]}>
      <TouchableOpacity
        style={buttonStyle}
        onPress={toggleRecording}
        disabled={permissionStatus === 'denied'}
        activeOpacity={0.8}
      >
        <Text style={textStyle}>{displayText}</Text>
      </TouchableOpacity>
      
      {permissionStatus === 'denied' && (
        <Text style={styles.errorText}>
          Microphone permission required for voice recording
        </Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  button: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 25,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  buttonRecording: {
    backgroundColor: '#FF3B30',
    transform: [{ scale: 1.05 }],
  },
  text: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  textRecording: {
    color: '#FFFFFF',
  },
  errorText: {
    color: '#FF3B30',
    fontSize: 12,
    marginTop: 8,
    textAlign: 'center',
  },
}); 