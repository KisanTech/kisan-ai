# Kisan AI 🌾 - AI-Powered Agricultural Assistant

## 🚀 Demo & Overview

**Kisan AI** is an AI-powered agricultural assistant designed specifically for Indian farmers. Our mobile application provides crop disease diagnosis, Kannada voice interface, market intelligence, and government scheme information - all powered by Google Cloud Vertex AI and Gemini 2.0.

### 📱 Live Demo
🔗 **[Watch Mobile App Demo](DEMO_LINK_HERE)** *(Add your demo link here)*

### 🎯 Key Features
- **🔍 Crop Disease Diagnosis** - AI-powered image analysis using Gemini 2.0 Flash
- **🗣️ Voice Interface** - Hindi speech-to-text and text-to-speech
- **📈 Real-time Market Prices** - Live commodity pricing data
- **🏛️ Government Schemes** - Information about agricultural schemes and subsidies

## 🏗️ Architecture

```
Kisan AI/
├── 📱 frontend/     # React Native Mobile App (Expo + NativeWind)
├── ⚡ backend/      # FastAPI + Multi-Agent AI System (Python 3.13)
└── 📚 docs/         # Project documentation
```

- **Mobile App**: React Native with Expo for cross-platform development
- **Backend API**: FastAPI with Python 3.13 and Google Cloud Vertex AI
- **AI Engine**: Multi-agent system powered by Gemini 2.0 Flash
- **Cloud**: Google Cloud Platform (Vertex AI, Speech APIs, Firestore, Cloud storage)

## 🛠️ Quick Setup Guide

### Prerequisites
- **Node.js** (v22+)
- **Python 3.13** 
- **uv** (Python package manager)
- **Expo CLI** for mobile development
- **Google Cloud Account** with Vertex AI enabled

### 📦 Step 1: Clone & Install Dependencies

```bash
# Clone the repository
git clone https://github.com/KisanTech/kisan-ai.git
cd kisan-ai

# Install root dependencies (for pre-commit hooks)
npm install
```

### 🐍 Step 2: Backend Setup

```bash
cd backend

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python dependencies
uv sync

# Setup environment variables
cp env.template .env
# Edit .env with your Google Cloud credentials and API keys

# Run the backend server
uv run python -m uvicorn app.main:app --reload
```

**Backend will be running at**: `http://127.0.0.1:8000`  
**API Documentation**: `http://127.0.0.1:8000/doc`

### 📱 Step 3: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run ios --clear
```

**Mobile App Options**:
- **📱 Physical Device**: Scan QR code with Expo Go app
- **🤖 Android**: `npm run android` (requires Android Studio)
- **🍎 iOS**: `npm run ios` (requires Xcode on macOS)

### ⚙️ Step 4: Environment Configuration

#### Backend Environment (.env)
```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json

# API Configuration
FASTAPI_ENV=development
LOG_LEVEL=INFO
```

#### Frontend Configuration
Update `frontend/src/config/app.ts` with your backend URL:
```typescript
export const API_BASE_URL = 'http://localhost:8000'; // For local development
```

## 🚀 Development Commands

### Root Commands
```bash
npm run dev:backend     # Start FastAPI server
npm run dev:frontend    # Start Expo development server
npm run install:all     # Install all dependencies
npm run format          # Format entire codebase
npm run lint            # Lint entire codebase
```

### Backend Commands
```bash
cd backend
uv run uvicorn app.main:app --reload  # Development server
uv run ruff check --fix               # Fix linting issues
uv run ruff format                    # Format code
uv add package-name                   # Add new dependency
```

### Frontend Commands
```bash
cd frontend
npm start              # Start development server
npm run android        # Run on Android
npm run ios           # Run on iOS
npm run web           # Run on web
npm test              # Run tests
```

## 📋 API Endpoints

### Core Endpoints
- `POST /api/v1/voice/speech-to-text` - Kannada speech recognition
- `POST /api/v1/voice/text-to-speech` - Kannada text-to-speech
- `POST /api/v1/crop-diagnosis/analyze` - Crop disease diagnosis
- `GET /api/v1/market/current` - Current market prices
- `GET /api/v1/government-schemes` - Available schemes

### Health Check
- `GET /health` - API health status



## 🏗️ Tech Stack

### Frontend
- **React Native** with Expo
- **NativeWind** (Tailwind CSS for React Native)
- **TypeScript**
- **Expo Router** for navigation

### Backend
- **FastAPI** (Python 3.13)
- **Google Cloud Vertex AI** 
- **Gemini 2.0 Flash** for AI processing
- **uv** for dependency management
- **Ruff** for linting and formatting

### Cloud & AI
- **Google Cloud Platform**
- **Vertex AI Speech APIs** (Multilingual support)
- **Firestore** for data storage
- **Cloud Storage** for file management

## 📁 Project Structure

```
kisan-ai/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── agents/       # AI agents
│   │   ├── models/       # Pydantic models
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utilities
│   └── tests/            # Backend tests
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── screens/      # App screens
│   │   ├── services/     # API services
│   │   └── types/        # TypeScript types
│   └── assets/           # Images and icons
└── docs/                 # Documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Google Cloud Vertex AI and Gemini 2.0
- Designed for Indian farmers with multilingual support
- Developed during a 30-hour hackathon challenge

---

**"Your Personal Agronomist in Your Pocket" 🚀🌾**

*Empowering Indian farmers with AI-driven agricultural intelligence* 