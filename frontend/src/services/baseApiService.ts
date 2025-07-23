import axios, { AxiosInstance } from 'axios';
import { Platform } from 'react-native';
import Constants from 'expo-constants';

// API Configuration
const getApiUrl = (): string => {
  // Get API URL from app.json extra config or use default
  const apiUrl = Constants.expoConfig?.extra?.apiUrl;

  if (apiUrl) {
    return apiUrl;
  }

  // Fallback URLs for development
  if (__DEV__) {
    if (Platform.OS === 'android') {
      return 'http://10.0.2.2:8000/api/v1'; // Android emulator localhost
    } else {
      return 'http://localhost:8000/api/v1'; // iOS simulator localhost
    }
  }

  // Production URL (update this when deployed)
  return 'https://your-production-api.com/api/v1';
};

export const API_BASE_URL = getApiUrl();

// Create base axios instance with shared configuration
const createBaseApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
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
      console.error('API Error:', error.response?.data || error.message);
      return Promise.reject(error);
    }
  );

  return client;
};

// Export the base API client instance
export const baseApiClient = createBaseApiClient();

// Export factory function for creating new instances if needed
export { createBaseApiClient };
