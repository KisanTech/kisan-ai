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

// API Endpoints
export const API_ENDPOINTS = {
    // Crop Diagnosis
    CROP_DIAGNOSE: '/crop/diagnose',

    // Voice Interface
    SPEECH_TO_TEXT: '/voice/speech-to-text',
    TEXT_TO_SPEECH: '/voice/text-to-speech',

    // Market Prices
    MARKET_CURRENT: '/market/current',
    MARKET_HISTORY: '/market/history',

    // Health Check
    HEALTH: '/health',
} as const;

// HTTP Client Configuration
export const httpClient = {
    async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${API_BASE_URL}${endpoint}`;

        const defaultHeaders = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers: defaultHeaders,
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    },

    get: <T>(endpoint: string) =>
        httpClient.request<T>(endpoint, { method: 'GET' }),

    post: <T>(endpoint: string, data: any) =>
        httpClient.request<T>(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        }),

    put: <T>(endpoint: string, data: any) =>
        httpClient.request<T>(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        }),

    delete: <T>(endpoint: string) =>
        httpClient.request<T>(endpoint, { method: 'DELETE' }),
}; 