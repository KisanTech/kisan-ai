# Project Kisan Frontend 🌾📱

React Native mobile app for Project Kisan - AI-Powered Agricultural Assistant built with Expo and NativeWind (Tailwind CSS).

## Tech Stack

- **📱 Expo**: React Native development platform
- **⚛️ React Native 0.79**: Latest React Native
- **🎨 NativeWind**: Tailwind CSS for React Native
- **📘 TypeScript**: Type-safe development
- **🔗 API Integration**: FastAPI backend connection

## Features

- **🔬 Crop Disease Diagnosis**: AI-powered image analysis
- **🎤 Voice Interface**: Kannada language support
- **💰 Market Prices**: Real-time commodity pricing
- **🎨 Modern UI**: Tailwind CSS styling with agricultural theme

## Quick Start

### Prerequisites

- Node.js 22+
- Expo CLI: `npm install -g expo-cli`
- Expo Go app on your mobile device

### Development

```bash
# Install dependencies
npm install

# Start development server
npm start

# Run on specific platforms
npm run android    # Android emulator/device
npm run ios        # iOS simulator/device
npm run web        # Web browser
```

### Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── screens/        # App screens/pages
│   ├── services/       # API and external services
│   ├── types/          # TypeScript type definitions
│   └── utils/          # Helper functions
├── assets/             # Images, fonts, etc.
├── App.tsx            # Main app component
├── global.css         # Tailwind CSS imports
└── app.json          # Expo configuration
```

## Configuration

### API Connection

The app connects to the FastAPI backend running on:
- **Development**: `http://localhost:8000/api/v1`
- **Android Emulator**: `http://10.0.2.2:8000/api/v1`

Update `app.json` extra.apiUrl for different environments.

### Tailwind Colors

Custom agricultural theme colors:
- **Primary**: Green shades for agriculture
- **Secondary**: Orange shades for harvest/warmth

## Development Commands

```bash
npm start              # Start Expo dev server
npm run start:clear    # Start with cache cleared
npm run type-check     # TypeScript checking
npm run lint           # ESLint (when configured)
```

## Building

```bash
# EAS Build (Production)
npm run build:android
npm run build:ios
```

## Features Integration

### Backend API Endpoints

- `POST /api/v1/crop/diagnose` - Crop disease identification
- `POST /api/v1/voice/speech-to-text` - Kannada speech processing
- `GET /api/v1/market/current` - Current market prices

### NativeWind Usage

```tsx
// Tailwind classes work directly
<View className="flex-1 bg-primary-50 p-4">
  <Text className="text-lg font-bold text-primary-700">
    🌾 Project Kisan
  </Text>
</View>
```

---

**"Your Personal Agronomist in Your Pocket" 🚀🌾** 