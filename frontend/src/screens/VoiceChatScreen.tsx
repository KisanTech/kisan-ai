import React, { useState, useRef, useEffect } from 'react';
import {
  SafeAreaView,
  Text,
  View,
  ScrollView,
  Alert,
  KeyboardAvoidingView,
  Platform,
  TextInput,
  TouchableOpacity,
  Animated,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { VoiceRecorder, VoicePlayer, NavigateBackButton } from '../components';
import { voiceChatService } from '../services/voiceChatService';
import { useLanguage } from '../i18n/LanguageContext';
import { getSpeechRecognitionCode, getTextApiCode } from '../config/languages';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isAudio?: boolean;
  audioData?: string;
}

// Animated typing dots component
const TypingDots: React.FC = () => {
  const dot1 = useRef(new Animated.Value(0)).current;
  const dot2 = useRef(new Animated.Value(0)).current;
  const dot3 = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const animateDot = (dot: Animated.Value, delay: number) => {
      return Animated.loop(
        Animated.sequence([
          Animated.delay(delay),
          Animated.timing(dot, {
            toValue: -4,
            duration: 300,
            useNativeDriver: true,
          }),
          Animated.timing(dot, {
            toValue: 0,
            duration: 300,
            useNativeDriver: true,
          }),
        ])
      );
    };

    const animations = [animateDot(dot1, 0), animateDot(dot2, 150), animateDot(dot3, 300)];

    Animated.parallel(animations).start();

    return () => {
      animations.forEach(animation => animation.stop());
    };
  }, [dot1, dot2, dot3]);

  return (
    <View className="flex-row items-end space-x-1" style={{ height: 12 }}>
      {[dot1, dot2, dot3].map((dot, index) => (
        <Animated.View
          key={index}
          style={{
            transform: [{ translateY: dot }],
          }}
          className="w-2 h-2 mx-0.5 bg-primary rounded-full"
        />
      ))}
    </View>
  );
};

export const VoiceChatScreen: React.FC = () => {
  const { t } = useTranslation();
  const { currentLanguage } = useLanguage();
  const navigation = useNavigation();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [textInput, setTextInput] = useState<string>('');
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [isSending, setIsSending] = useState<boolean>(false);
  const scrollViewRef = useRef<ScrollView>(null);
  const messageIdCounter = useRef<number>(0);

  // Add welcome message on component mount
  useEffect(() => {
    messageIdCounter.current += 1;
    const welcomeMessage: ChatMessage = {
      id: `assistant-${Date.now()}-${messageIdCounter.current}`,
      type: 'assistant',
      content: t('voiceChat.welcomeMessage'),
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
  }, [t]);

  // Auto scroll to bottom when new message is added
  useEffect(() => {
    if (scrollViewRef.current) {
      scrollViewRef.current.scrollToEnd({ animated: true });
    }
  }, [messages]);

  const addMessage = (type: 'user' | 'assistant', content: string, audioData?: string) => {
    messageIdCounter.current += 1;
    const newMessage: ChatMessage = {
      id: `${type}-${Date.now()}-${messageIdCounter.current}`,
      type,
      content,
      timestamp: new Date(),
      isAudio: !!audioData,
      audioData,
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleTextSend = async () => {
    if (!textInput.trim() || isSending) return;

    const userMessage = textInput.trim();
    setTextInput('');
    setIsSending(true);

    // Add user message
    addMessage('user', userMessage);

    try {
      const speechLanguageCode = getSpeechRecognitionCode(currentLanguage);

      // Debug log to verify speech language code for text
      console.log('💬 Text Chat - Current Language:', currentLanguage);
      console.log('💬 Text Chat - Speech Language Code:', speechLanguageCode);

      // Use the new text invoke API
      const response = await voiceChatService.sendTextInvoke(userMessage, speechLanguageCode);

      if (response.success) {
        // Add assistant response (text responses don't include audio)
        addMessage('assistant', response.agent_response_translated || response.agent_response);
      } else {
        throw new Error(response.error || 'Unknown error occurred');
      }
    } catch (error) {
      console.error('Failed to send text message:', error);
      addMessage('assistant', t('voiceChat.errorMessage'));
    } finally {
      setIsSending(false);
    }
  };

  const handleAudioRecorded = async (base64Audio: string) => {
    setIsProcessing(true);

    try {
      // Get language codes based on current language
      const speechLanguageCode = getSpeechRecognitionCode(currentLanguage);

      // Debug log to verify speech language code
      console.log('🎤 Voice Chat - Current Language:', currentLanguage);
      console.log('🎤 Voice Chat - Speech Language Code:', speechLanguageCode);

      // Send audio to speech-to-text API
      const speechResult = await voiceChatService.speechToText(base64Audio, speechLanguageCode);

      if (speechResult.success) {
        // Add user message (transcribed)
        addMessage('user', speechResult.original_transcript, base64Audio);

        // Add assistant response
        addMessage(
          'assistant',
          speechResult.agent_response_translated,
          speechResult.response_audio_data
        );

        console.log('Voice chat - Original Transcript:', speechResult.original_transcript);
        console.log('Voice chat - Agent Response:', speechResult.agent_response_translated);
      } else {
        throw new Error(speechResult.error || 'Unknown error occurred');
      }
    } catch (error) {
      console.error('Failed to process audio:', error);
      Alert.alert(t('voiceChat.processingError'), t('voiceChat.processingErrorMessage'));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRecordingStart = () => {
    setIsRecording(true);
  };

  const handleRecordingStop = () => {
    setIsRecording(false);
  };

  const handleRecordingError = (error: string) => {
    setIsRecording(false);
    Alert.alert(t('voiceChat.recordingError'), error);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <SafeAreaView className="flex-1 bg-background">
      {/* Header */}
      <View className="bg-white border-b border-gray-200 px-4 py-3">
        <View className="flex-row items-center">
          <NavigateBackButton navigation={navigation} />
          <View className="flex-1 ml-3">
            <Text className="text-xl font-bold text-foreground">{t('voiceChat.title')}</Text>
            <Text className="text-sm text-gray-600">{t('voiceChat.subtitle')}</Text>
          </View>
        </View>
      </View>

      <KeyboardAvoidingView
        className="flex-1"
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
      >
        {/* Chat Messages */}
        <ScrollView
          ref={scrollViewRef}
          className="flex-1 px-4 py-4"
          showsVerticalScrollIndicator={false}
        >
          {messages.map(message => (
            <View
              key={message.id}
              className={`mb-4 ${message.type === 'user' ? 'items-end' : 'items-start'}`}
            >
              <View
                className={`max-w-[80%] rounded-lg px-4 py-3 ${
                  message.type === 'user' ? 'bg-primary rounded-br-sm' : 'rounded-bl-sm'
                }`}
                style={message.type === 'assistant' ? { backgroundColor: '#d7e6cf' } : undefined}
              >
                {/* Audio player for messages with audio - TOP for assistant */}
                {message.type === 'assistant' && message.isAudio && message.audioData && (
                  <View className="mb-3">
                    <VoicePlayer
                      base64Audio={message.audioData}
                      onPlay={() => console.log('Playing message audio')}
                      onPause={() => console.log('Paused message audio')}
                      onError={error => {
                        console.error('Message audio playback error:', error);
                        Alert.alert(t('voiceChat.playbackError'), error);
                      }}
                      playButtonText={t('voiceChat.playAudio')}
                      pauseButtonText={t('voiceChat.pause')}
                      replayButtonText={t('voiceChat.replay')}
                      customStyles={{
                        container: {
                          alignItems: 'center',
                          justifyContent: 'center',
                          marginBottom: 8,
                        },
                        button: {
                          paddingHorizontal: 16,
                          paddingVertical: 8,
                          borderRadius: 20,
                          backgroundColor: '#ffffff',
                          marginRight: 8,
                        },
                        text: {
                          fontWeight: 'bold',
                          color: '#19BA49',
                          fontSize: 14,
                        },
                      }}
                    />
                  </View>
                )}

                <Text
                  className={`text-sm ${message.type === 'user' ? 'text-white' : 'text-green-800'}`}
                >
                  {message.content}
                </Text>

                {/* Audio player for USER messages - AFTER text */}
                {message.type === 'user' && message.isAudio && message.audioData && (
                  <View className="mt-3">
                    <VoicePlayer
                      base64Audio={message.audioData}
                      onPlay={() => console.log('Playing message audio')}
                      onPause={() => console.log('Paused message audio')}
                      onError={error => {
                        console.error('Message audio playback error:', error);
                        Alert.alert(t('voiceChat.playbackError'), error);
                      }}
                      playButtonText={t('voiceChat.playAudio')}
                      pauseButtonText={t('voiceChat.pause')}
                      replayButtonText={t('voiceChat.replay')}
                      customStyles={{
                        container: {
                          alignItems: 'center',
                          justifyContent: 'center',
                          marginBottom: 8,
                        },
                        button: {
                          paddingHorizontal: 16,
                          paddingVertical: 8,
                          borderRadius: 20,
                          backgroundColor: '#ffffff',
                          marginRight: 8,
                        },
                        text: {
                          fontWeight: 'bold',
                          color: '#19BA49',
                          fontSize: 14,
                        },
                      }}
                    />
                  </View>
                )}

                {/* Timestamp */}
                <Text
                  className={`text-xs ${message.isAudio && message.audioData ? 'mt-0' : 'mt-2'} ${
                    message.type === 'user' ? 'text-green-100' : 'text-green-600'
                  }`}
                >
                  {formatTime(message.timestamp)}
                </Text>
              </View>
            </View>
          ))}

          {/* Processing indicator */}
          {(isProcessing || isSending) && (
            <View className="items-start mb-4">
              <View
                className="rounded-lg rounded-bl-sm px-4 py-3"
                style={{ backgroundColor: '#d7e6cf' }}
              >
                <View className="flex-row items-center">
                  <Text className="text-sm text-green-700 mr-3">
                    {isSending ? t('voiceChat.sending') : t('voiceChat.processing')}
                  </Text>
                  <TypingDots />
                </View>
              </View>
            </View>
          )}
        </ScrollView>

        {/* Input Section */}
        <View className="bg-white border-t border-gray-200 px-4 py-4">
          {/* Text Input Row */}
          <View className="flex-row items-center mb-4">
            <View className="flex-1 mr-3">
              <TextInput
                className="border border-gray-300 rounded-full px-4 py-3 text-base bg-white"
                placeholder={t('voiceChat.typeMessage')}
                placeholderTextColor="#9CA3AF"
                value={textInput}
                onChangeText={setTextInput}
                multiline={false}
                onSubmitEditing={handleTextSend}
                editable={!isSending}
                returnKeyType="send"
                style={{
                  minHeight: 48,
                  textAlignVertical: 'center',
                  fontSize: 16,
                  lineHeight: 20,
                }}
              />
            </View>
            <TouchableOpacity
              onPress={handleTextSend}
              disabled={!textInput.trim() || isSending}
              className={`px-6 py-3 rounded-full min-h-[48px] justify-center flex-row items-center ${
                textInput.trim() && !isSending ? 'bg-primary' : 'bg-gray-300'
              }`}
              style={{ minWidth: 80 }}
            >
              <Text
                className={`text-sm font-bold text-center mr-2 ${
                  textInput.trim() && !isSending ? 'text-white' : 'text-gray-500'
                }`}
              >
                {t('voiceChat.send')}
              </Text>
              <Ionicons
                name="paper-plane"
                size={16}
                color={textInput.trim() && !isSending ? '#ffffff' : '#6B7280'}
              />
            </TouchableOpacity>
          </View>

          {/* Divider */}
          <View className="flex-row items-center mb-4">
            <View className="flex-1 h-px bg-gray-200" />
            <Text className="text-sm text-gray-500 mx-4 font-medium">
              {t('voiceChat.orUseVoice')}
            </Text>
            <View className="flex-1 h-px bg-gray-200" />
          </View>

          {/* Voice Input Section */}
          <View className="items-center">
            <VoiceRecorder
              onAudioRecorded={handleAudioRecorded}
              onRecordingStart={handleRecordingStart}
              onRecordingStop={handleRecordingStop}
              onError={handleRecordingError}
              disabled={isProcessing || isSending}
              buttonText={
                isProcessing
                  ? t('voiceChat.processing')
                  : isRecording
                    ? t('voiceChat.recording')
                    : t('voiceChat.holdToRecord')
              }
              recordingText={t('voiceChat.recording')}
              customStyles={{
                container: { marginVertical: 10 },
                button: {
                  paddingHorizontal: 24,
                  paddingVertical: 12,
                  borderRadius: 25,
                  opacity: isProcessing || isSending ? 0.6 : 1,
                },
              }}
            />
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};
