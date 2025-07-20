# Project Kisan 🌾 - AI-Powered Agricultural Assistant

## Overview
Project Kisan is a mono-repo for an AI-powered agricultural assistant designed for Indian farmers. Built for a 30-hour hackathon with Google Cloud Vertex AI, focusing on crop disease diagnosis, Kannada voice interface, and real-time market intelligence.

## Architecture

- **backend/**: FastAPI (Python 3.13) + Multi-Agent AI System
- **mobile/**: React Native
- **docs/**: Project documentation and specifications

## Folder Structure

```
codekheti.ai/
├── backend/         # FastAPI + AI Agents (Vertex AI + Gemini 2.0)
├── mobile/          # Mobile app (Future)
├── docs/            # Project specs and documentation
└── README.md        # This file
```

## Setup Instructions

### Prerequisites
- **Node.js** (v22+ required for husky)
- **Python 3.13** (auto-managed via uv)
- **uv** (modern Python package manager)
- **Google Cloud Account** with Vertex AI enabled

### Initial Setup

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd codekheti.ai
   ```

2. **Install uv (if not already installed):**
   ```sh
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Or via Homebrew
   brew install uv
   ```

3. **Root setup (husky pre-commit hooks):**
   ```sh
   npm install
   ```
   After installing dependencies, ensure hooks are executable:
   ```sh
   chmod +x .husky/pre-commit
   ```

4. **Backend:**
   ```sh
   cd backend
   # Install Python 3.13 and dependencies (uv handles everything)
   uv sync
   # Copy environment variables
   cp .env.example .env
   ```

## Development Tools

### Backend (Python)
- **📦 uv**: Ultra-fast package manager (10-100x faster than pip)
- **🦀 Ruff**: Ultra-fast linter and formatter 
- **🐍 Python 3.13**: Latest Python with enhanced performance
- **🧠 Vertex AI**: Google Cloud AI platform with Gemini 2.0 Flash

## Pre-commit Hooks (Formatting & Linting)

Husky automatically runs on every commit:
- **Backend**: Ruff formatting and linting for Python code
- **Standards**: 100 char line length, isort imports, type hints

## Quick Start Commands

### Backend
```sh
cd backend

# Run development server
uv run uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs

# Code quality
uv run ruff check --fix     # Fix linting issues
uv run ruff format          # Format code

# Add dependencies
uv add google-cloud-speech
```

### Root Commands
```sh
# Format entire codebase
npm run format

# Lint entire codebase  
npm run lint
```

## MVP Features

### ✅ Core Features
1. **Crop Disease Identification** - Gemini 2.0 Flash image analysis
2. **Voice Interface (Kannada)** - Vertex AI Speech APIs
3. **Market Price Display** - Real-time commodity prices

### 🔧 Tech Stack
- **AI**: Google Cloud Vertex AI + Gemini 2.0 Flash
- **Speech**: Vertex AI Speech APIs (Kannada)
- **Backend**: FastAPI + Python 3.13 + uv
- **Data**: Firestore + BigQuery + Cloud Storage

## API Documentation

- **Development Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Key Endpoints**:
  - `POST /api/v1/crop/diagnose` - Disease identification
  - `POST /api/v1/voice/speech-to-text` - Kannada speech
  - `GET /api/v1/market/current` - Market prices

## Component Documentation

- **Backend Development**: [backend/README.md](./backend/README.md)
- **Project Specification**: [docs/project_kisan_specification.md](./docs/project_kisan_specification.md)

---

**"Your Personal Agronomist in Your Pocket" 🚀🌾** 