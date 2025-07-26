import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { Audio } from 'expo-av';
import { Ionicons } from '@expo/vector-icons';
import { voiceChatService, ChatMessage } from '../services/voiceChatService';

// PCM Recording configuration
const PCM_RECORDING_OPTIONS = {
  android: {
    extension: '.wav',
    outputFormat: Audio.AndroidOutputFormat.DEFAULT,
    audioEncoder: Audio.AndroidAudioEncoder.DEFAULT,
    sampleRate: 16000,
    numberOfChannels: 1,
    bitRate: 256000,
  },
  ios: {
    extension: '.wav',
    outputFormat: Audio.IOSOutputFormat.LINEARPCM,
    audioQuality: Audio.IOSAudioQuality.HIGH,
    sampleRate: 16000,
    numberOfChannels: 1,
    bitRate: 256000,
    linearPCMBitDepth: 16,
    linearPCMIsBigEndian: false,
    linearPCMIsFloat: false,
  },
  web: {
    mimeType: 'audio/wav',
    bitsPerSecond: 256000,
  },
};

export const VoiceChatScreen: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [sound, setSound] = useState<Audio.Sound | null>(null);
  const scrollViewRef = useRef<ScrollView>(null);

  useEffect(() => {
    // Add welcome message when screen loads
    const welcomeMessage: ChatMessage = {
      id: 'welcome',
      type: 'assistant',
      content:
        'Hello! I am Kisan AI, your agricultural assistant. You can ask me about crops, market prices, farming techniques, or any agriculture-related questions. You can type your message or use the microphone to speak.',
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);

    return () => {
      // Cleanup audio when component unmounts
      if (sound) {
        sound.unloadAsync();
      }
      if (recording) {
        recording.stopAndUnloadAsync();
      }
    };
  }, []);

  useEffect(() => {
    // Auto-scroll to bottom when new messages are added
    scrollViewRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  const addMessage = (message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const newMessage: ChatMessage = {
      ...message,
      id: Date.now().toString(),
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const sendTextMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage = inputText.trim();
    setInputText('');

    // Add user message
    addMessage({
      type: 'user',
      content: userMessage,
    });

    setIsLoading(true);

    try {
      const response = await voiceChatService.sendTextMessage(userMessage);

      // Add AI response
      addMessage({
        type: 'assistant',
        content: response.response_text,
        audioUrl: response.audio_response_url,
      });
    } catch (error) {
      console.error('Error sending text message:', error);
      addMessage({
        type: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      const permission = await Audio.requestPermissionsAsync();
      if (permission.status !== 'granted') {
        Alert.alert(
          'Permission required',
          'Please allow microphone access to record voice messages.'
        );
        return;
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(PCM_RECORDING_OPTIONS);

      setRecording(recording);
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
      Alert.alert('Error', 'Failed to start recording. Please try again.');
    }
  };

  const stopRecording = async () => {
    if (!recording) return;

    setIsRecording(false);
    setIsLoading(true);

    try {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecording(null);

      if (uri) {
        // Add user voice message placeholder
        addMessage({
          type: 'user',
          content: 'Voice message...',
          isAudio: true,
        });

        // Send voice message to API
        const response = await voiceChatService.sendVoiceMessage(uri);

        // Update user message with transcription
        setMessages(prev => {
          const updated = [...prev];
          const lastUserMessage = updated[updated.length - 1];
          if (lastUserMessage.type === 'user' && lastUserMessage.isAudio) {
            lastUserMessage.content = response.query_text;
          }
          return updated;
        });

        // Add AI response
        addMessage({
          type: 'assistant',
          content: response.response_text,
          audioUrl: response.audio_response_url,
        });
      }
    } catch (error) {
      console.error('Error processing voice message:', error);
      addMessage({
        type: 'assistant',
        content:
          'Sorry, I could not process your voice message. Please try again or use text instead.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const playAudioResponse = async (audioUrl: string) => {
    try {
      if (sound) {
        await sound.unloadAsync();
      }

      const { sound: newSound } = await Audio.Sound.createAsync(
        { uri: audioUrl },
        { shouldPlay: true }
      );
      setSound(newSound);

      newSound.setOnPlaybackStatusUpdate(status => {
        if (status.isLoaded && status.didJustFinish) {
          newSound.unloadAsync();
          setSound(null);
        }
      });
    } catch (error) {
      console.error('Error playing audio:', error);
      Alert.alert('Error', 'Could not play audio response.');
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const renderMessage = (message: ChatMessage) => {
    const isUser = message.type === 'user';

    return (
      <View key={message.id} className={`mb-4 ${isUser ? 'items-end' : 'items-start'}`}>
        <View
          className={`max-w-[80%] px-4 py-3 rounded-2xl ${
            isUser ? 'bg-green-600 rounded-br-sm' : 'bg-gray-200 rounded-bl-sm'
          }`}
        >
          <Text className={`text-base ${isUser ? 'text-white' : 'text-gray-800'}`}>
            {message.content}
          </Text>

          {message.audioUrl && !isUser && (
            <TouchableOpacity
              onPress={() => playAudioResponse(message.audioUrl!)}
              className="mt-2 flex-row items-center"
            >
              <Ionicons name="play-circle" size={24} color={isUser ? 'white' : '#059669'} />
              <Text className={`ml-2 text-sm ${isUser ? 'text-green-100' : 'text-green-600'}`}>
                Play audio response
              </Text>
            </TouchableOpacity>
          )}
        </View>

        <Text className="text-xs text-gray-500 mt-1 mx-2">{formatTime(message.timestamp)}</Text>
      </View>
    );
  };

  return (
    <SafeAreaView className="flex-1 bg-white">
      <KeyboardAvoidingView
        className="flex-1"
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        {/* Chat messages */}
        <ScrollView
          ref={scrollViewRef}
          className="flex-1 px-4 py-4"
          showsVerticalScrollIndicator={false}
        >
          {messages.map(renderMessage)}

          {isLoading && (
            <View className="items-start mb-4">
              <View className="bg-gray-200 px-4 py-3 rounded-2xl rounded-bl-sm">
                <Text className="text-gray-600">Kisan AI is typing...</Text>
              </View>
            </View>
          )}
        </ScrollView>

        {/* Input area */}
        <View className="border-t border-gray-200 px-4 py-3 bg-white">
          <View className="flex-row items-end space-x-3">
            {/* Text input */}
            <View className="flex-1">
              <TextInput
                value={inputText}
                onChangeText={setInputText}
                placeholder="Ask Kisan AI anything about farming..."
                multiline
                maxLength={500}
                className="border border-gray-300 rounded-2xl px-4 py-3 max-h-24 text-base"
                style={{ textAlignVertical: 'top' }}
              />
            </View>

            {/* Voice recording button */}
            <TouchableOpacity
              onPress={isRecording ? stopRecording : startRecording}
              disabled={isLoading}
              className={`w-12 h-12 rounded-full items-center justify-center ${
                isRecording ? 'bg-red-500' : isLoading ? 'bg-gray-300' : 'bg-green-600'
              }`}
            >
              <Ionicons name={isRecording ? 'stop' : 'mic'} size={24} color="white" />
            </TouchableOpacity>

            {/* Send button */}
            <TouchableOpacity
              onPress={sendTextMessage}
              disabled={!inputText.trim() || isLoading}
              className={`w-12 h-12 rounded-full items-center justify-center ${
                inputText.trim() && !isLoading ? 'bg-green-600' : 'bg-gray-300'
              }`}
            >
              <Ionicons name="send" size={20} color="white" />
            </TouchableOpacity>
          </View>

          {/* Recording indicator */}
          {isRecording && (
            <View className="flex-row items-center justify-center mt-2">
              <View className="w-2 h-2 rounded-full bg-red-500 mr-2 animate-pulse" />
              <Text className="text-red-500 text-sm">Recording... Tap to stop</Text>
            </View>
          )}
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};
