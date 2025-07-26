import React, { useState, useEffect, useRef } from 'react';
import { View, TouchableOpacity, Text, StyleSheet, Alert } from 'react-native';
import { useAudioPlayer, setAudioModeAsync } from 'expo-audio';
import * as FileSystem from 'expo-file-system';
import { VoicePlayerProps, PlayerState } from '../types';

export const VoicePlayer: React.FC<VoicePlayerProps> = ({
  base64Audio,
  onPlay,
  onPause,
  onStop,
  onError,
  onLoadStart,
  onLoadComplete,
  disabled = false,
  autoPlay = false,
  customStyles = {},
  playButtonText = 'Play Audio',
  pauseButtonText = 'Pause',
  loadingText = 'Loading...',
  replayButtonText = 'Replay',
}) => {
  const [state, setState] = useState<PlayerState>({
    isLoading: false,
    isPlaying: false,
    hasError: false,
    audioUri: undefined,
  });

  const audioUriRef = useRef<string | null>(null);
  const player = useAudioPlayer(state.audioUri);

  // Convert base64 to audio file
  const convertBase64ToAudio = async (base64AudioString: string): Promise<string> => {
    try {
      setState(prev => ({ ...prev, isLoading: true, hasError: false, errorMessage: undefined }));
      onLoadStart?.();

      // Create a temporary file path with timestamp to ensure uniqueness
      const timestamp = Date.now();
      const tmpFilename = `${FileSystem.cacheDirectory}audio_${timestamp}.mp3`;
      
      // Write the base64 string to a file
      await FileSystem.writeAsStringAsync(tmpFilename, base64AudioString, {
        encoding: FileSystem.EncodingType.Base64,
      });

      audioUriRef.current = tmpFilename;
      setState(prev => ({ ...prev, isLoading: false, audioUri: tmpFilename }));
      onLoadComplete?.();
      
      return tmpFilename;
    } catch (error) {
      const errorMsg = 'Failed to convert audio for playback';
      console.error(errorMsg, error);
      setState(prev => ({ 
        ...prev, 
        isLoading: false, 
        hasError: true, 
        errorMessage: errorMsg 
      }));
      onError?.(errorMsg);
      throw error;
    }
  };

  // Set up audio mode for playback
  const setupAudioMode = async () => {
    try {
      await setAudioModeAsync({
        playsInSilentMode: true,
        allowsRecording: false,
      });
    } catch (error) {
      console.warn('Failed to set audio mode:', error);
    }
  };

  // Play audio
  const playAudio = async () => {
    try {
      if (!state.audioUri) {
        const errorMsg = 'No audio available to play';
        onError?.(errorMsg);
        return;
      }

      await setupAudioMode();
      await player.play();
      setState(prev => ({ ...prev, isPlaying: true }));
      onPlay?.();
    } catch (error) {
      const errorMsg = 'Failed to play audio';
      console.error(errorMsg, error);
      setState(prev => ({ 
        ...prev, 
        hasError: true, 
        errorMessage: errorMsg 
      }));
      onError?.(errorMsg);
    }
  };

  // Pause audio
  const pauseAudio = async () => {
    try {
      await player.pause();
      setState(prev => ({ ...prev, isPlaying: false }));
      onPause?.();
    } catch (error) {
      const errorMsg = 'Failed to pause audio';
      console.error(errorMsg, error);
      onError?.(errorMsg);
    }
  };

  // Stop audio
  const stopAudio = async () => {
    try {
      await player.pause();
      await player.seekTo(0);
      setState(prev => ({ ...prev, isPlaying: false }));
      onStop?.();
    } catch (error) {
      const errorMsg = 'Failed to stop audio';
      console.error(errorMsg, error);
      onError?.(errorMsg);
    }
  };

  // Replay audio from beginning
  const replayAudio = async () => {
    try {
      await player.seekTo(0);
      await player.play();
      setState(prev => ({ ...prev, isPlaying: true }));
      onPlay?.();
    } catch (error) {
      const errorMsg = 'Failed to replay audio';
      console.error(errorMsg, error);
      onError?.(errorMsg);
    }
  };

  // Toggle play/pause
  const togglePlayback = async () => {
    if (state.isPlaying) {
      await pauseAudio();
    } else {
      await playAudio();
    }
  };

  // Clean up temporary files
  const cleanupAudioFile = async () => {
    if (audioUriRef.current) {
      try {
        await FileSystem.deleteAsync(audioUriRef.current, { idempotent: true });
      } catch (deleteError) {
        console.warn('Failed to delete temporary audio file:', deleteError);
      }
      audioUriRef.current = null;
    }
  };

  // Process base64 audio when it changes
  useEffect(() => {
    if (base64Audio) {
      convertBase64ToAudio(base64Audio)
        .then(() => {
          if (autoPlay) {
            playAudio();
          }
        })
        .catch(() => {
          // Error already handled in convertBase64ToAudio
        });
    }

    // Cleanup previous file if any
    return () => {
      cleanupAudioFile();
    };
  }, [base64Audio]);

  // Listen for audio player status changes
  useEffect(() => {
    if (player) {
      const handleStatusUpdate = () => {
        const isCurrentlyPlaying = player.playing;
        setState(prev => {
          if (prev.isPlaying !== isCurrentlyPlaying) {
            return { ...prev, isPlaying: isCurrentlyPlaying };
          }
          return prev;
        });
      };

      // Set up a periodic check for player status
      const statusInterval = setInterval(handleStatusUpdate, 100);

      return () => {
        clearInterval(statusInterval);
      };
    }
  }, [player]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (player && state.isPlaying) {
        try {
          player.pause();
        } catch (error) {
          console.error('Error pausing audio on cleanup:', error);
        }
      }
      cleanupAudioFile();
    };
  }, []);

  // Determine if component should be disabled
  const isDisabled = disabled || state.isLoading || state.hasError || !state.audioUri;

  // Determine button style and text
  const buttonStyle = [
    styles.button,
    customStyles.button,
    state.isPlaying && styles.buttonPlaying,
    state.isPlaying && customStyles.buttonPlaying,
    isDisabled && styles.buttonDisabled,
    isDisabled && customStyles.buttonDisabled,
  ];

  const textStyle = [
    styles.text,
    customStyles.text,
    state.isPlaying && styles.textPlaying,
    state.isPlaying && customStyles.textPlaying,
    isDisabled && styles.textDisabled,
    isDisabled && customStyles.textDisabled,
  ];

  const getDisplayText = () => {
    if (state.isLoading) return loadingText;
    if (state.hasError) return 'Error';
    if (state.isPlaying) return pauseButtonText;
    return playButtonText;
  };

  return (
    <View style={[styles.container, customStyles.container]}>
      <View style={styles.controlsContainer}>
        <TouchableOpacity
          style={buttonStyle}
          onPress={togglePlayback}
          disabled={isDisabled}
          activeOpacity={0.8}
        >
          <Text style={textStyle}>{getDisplayText()}</Text>
        </TouchableOpacity>
        
        {state.audioUri && !state.isLoading && !state.hasError && (
          <TouchableOpacity
            style={[styles.secondaryButton, customStyles.button]}
            onPress={replayAudio}
            disabled={disabled}
            activeOpacity={0.8}
          >
            <Text style={[styles.secondaryText, customStyles.text]}>{replayButtonText}</Text>
          </TouchableOpacity>
        )}
      </View>
      
      {state.hasError && state.errorMessage && (
        <Text style={[styles.errorText, customStyles.errorText]}>
          {state.errorMessage}
        </Text>
      )}
      
      {!base64Audio && !state.isLoading && (
        <Text style={styles.noAudioText}>
          No audio available
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
  controlsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
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
  buttonPlaying: {
    backgroundColor: '#FF9500',
  },
  buttonDisabled: {
    backgroundColor: '#C7C7CC',
    opacity: 0.6,
  },
  secondaryButton: {
    backgroundColor: '#34C759',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.20,
    shadowRadius: 1.41,
  },
  text: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  textPlaying: {
    color: '#FFFFFF',
  },
  textDisabled: {
    color: '#FFFFFF',
  },
  secondaryText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '500',
    textAlign: 'center',
  },
  errorText: {
    color: '#FF3B30',
    fontSize: 12,
    marginTop: 8,
    textAlign: 'center',
  },
  noAudioText: {
    color: '#8E8E93',
    fontSize: 12,
    marginTop: 8,
    textAlign: 'center',
  },
}); 