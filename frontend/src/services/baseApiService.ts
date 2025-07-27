import axios, { AxiosInstance } from 'axios';
import { Platform } from 'react-native';
import Constants from 'expo-constants';

// Service types
export type ServiceType = 'diagnosis' | 'voiceChat' | 'default';

// API Configuration
const getApiUrl = (serviceType: ServiceType = 'default'): string => {
  // Get API URL from app.json extra config or use default
  const apiUrl = Constants.expoConfig?.extra?.apiUrl;

  if (apiUrl) {
    return apiUrl;
  }

  // Fallback URLs for development based on service type
  if (__DEV__) {
    const baseUrl =
      Platform.OS === 'android'
        ? '10.0.2.2'
        : 'https://kisan-ai-api-556613941388.us-central1.run.app';

    switch (serviceType) {
      case 'diagnosis':
        return `${baseUrl}/api/v1`;
      case 'voiceChat':
        return `${baseUrl}/api/v1`;
      default:
        return `${baseUrl}/api/v1`;
    }
  }

  // Production URLs (update these when deployed)
  switch (serviceType) {
    case 'diagnosis':
      return 'http://127.0.0.1:8000/api/v1';
    case 'voiceChat':
      return 'http://127.0.0.1:8000/api/v1';
    default:
      return 'http://127.0.0.1:8000/api/v1';
  }
};

// Export individual service URLs
export const DIAGNOSIS_API_BASE_URL = getApiUrl('diagnosis');
export const VOICE_CHAT_API_BASE_URL = getApiUrl('voiceChat');
export const API_BASE_URL = getApiUrl('default'); // Keep for backward compatibility

// Create base axios instance with shared configuration
const createBaseApiClient = (serviceType: ServiceType = 'default'): AxiosInstance => {
  const client = axios.create({
    baseURL: getApiUrl(serviceType),
    timeout: 90000, // Increased to 90 seconds for voice processing
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor for adding auth tokens if needed
  client.interceptors.request.use(
    config => {
      // Add auth token here if needed
      // const token = getAuthToken();
      // if (token) {
      //   config.headers.Authorization = `Bearer ${token}`;
      // }
      console.log(`${serviceType} service request config:`, config.baseURL);
      return config;
    },
    error => {
      return Promise.reject(error);
    }
  );

  // Response interceptor for handling common errors
  client.interceptors.response.use(
    response => {
      return response;
    },
    error => {
      // Handle common errors here
      console.error(`${serviceType} service API Error:`, error.response?.data || error.message);
      return Promise.reject(error);
    }
  );

  return client;
};

// Create service-specific API clients
export const diagnosisApiClient = createBaseApiClient('diagnosis');
export const voiceChatApiClient = createBaseApiClient('voiceChat');

// Export the base API client instance (default)
export const baseApiClient = createBaseApiClient();

// Export factory function for creating new instances if needed
export { createBaseApiClient };
