# Kisan AI - Backend API

AI-Powered Agricultural Assistant for Google Agentic AI Day Hackathon

## DEMO Video
- [DEMO Video](https://drive.google.com/file/d/1rusxMNTvu3lcugK1KyeqOd-ykMpKpL3I/view?usp=sharing)

## Quick Start

### Prerequisites
- uv package manager (will auto-install Python 3.13)
- Google Cloud Account with Vertex AI enabled

> **Note**: The `.python-version` file ensures everyone uses Python 3.13 automatically!

### Setup

1. **Install uv** (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Install dependencies** (uv will auto-install Python 3.13)
```bash
cd backend
uv sync  # Automatically uses Python 3.13 from .python-version file
```

3. **Environment Configuration**

**Quick Setup (Recommended):**
```bash
# Copy the template file and customize it
cp env.template .env
# Edit .env with your actual API keys and credentials
```

**Manual Setup:**
Create a `.env` file with your actual credentials:
```bash
DEBUG=true
ENVIRONMENT=dev

GOOGLE_CLOUD_PROJECT=<your-gcp-project-id>
GOOGLE_APPLICATION_CREDENTIALS=<path-to-service-account-key.json>

# Google Cloud Services
FIRESTORE_DATABASE=<your-firestore-database-name>
CLOUD_STORAGE_BUCKET=<your-cloud-storage-bucket-name>

# Vertex AI Configuration
VERTEX_AI_REGION=<your-vertex-ai-region>
GEMINI_MODEL=gemini-2.5-flash
GOOGLE_GENAI_USE_VERTEXAI=1

# Vertex Backend Config
GOOGLE_CLOUD_PROJECT=<your-gcp-project-id>
GOOGLE_CLOUD_LOCATION=<your-gcp-location>
GOOGLE_CLOUD_STAGING_BUCKET=<your-gcp-staging-bucket-name>

DATA_GOV_API_KEY=<your-data-gov-api-key>
```

4. **Run the development server**
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access API Documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Keys Setup

### Google Cloud Setup (Required for AI Features)
1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create new project or select existing one
   - Note the Project ID

2. **Enable APIs**
   ```bash
   # Enable required APIs
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable speech.googleapis.com
   gcloud services enable storage.googleapis.com
   ```

3. **Create Service Account**
   - Go to IAM & Admin > Service Accounts
   - Create new service account
   - Download JSON key file
   - Set `GOOGLE_APPLICATION_CREDENTIALS` to the file path

### Indian Government APIs (Optional for Real Data)

#### Data.gov.in API
1. Register at [data.gov.in](https://data.gov.in/user/register)
2. Apply for API access for agriculture data
3. Add your API key to `DATA_GOV_API_KEY`

#### e-NAM API (Optional)
1. Contact [e-NAM support](https://enam.gov.in) for API access
2. Add your API key to `ENAM_API_KEY`

> **🚀 For Hackathon**: Skip API keys setup! The app works with mock data for demo purposes.

## Environment Variables Security

### ⚠️ Important Security Notes
- **NEVER commit `.env` files** to version control
- The `.env` file is already in `.gitignore`
- Use `env.template` as reference for required variables
- Use different API keys for development/staging/production

### For New Team Members
```bash
# 1. Copy the template
cp env.template .env

# 2. Ask team lead for actual API keys
# 3. Update .env with real credentials
# 4. Verify .env is NOT tracked by git
git status  # Should not show .env file
```

## Code Quality & Formatting

### Linting and Formatting with uv + ruff

We use **ruff** for both linting and formatting to maintain consistent code quality across the team.

#### Quick Commands
```bash
# Check code style and lint issues
uv run ruff check

# Auto-fix linting issues where possible
uv run ruff check --fix

# Format code automatically
uv run ruff format

# Check formatting without making changes
uv run ruff format --check

# Run both linting and formatting together
uv run ruff check --fix && uv run ruff format
```

#### Pre-Commit Workflow (Recommended)
Before committing code during the hackathon:
```bash
# 1. Fix any linting issues
uv run ruff check --fix

# 2. Format all code
uv run ruff format

# 3. Verify everything is clean
uv run ruff check && uv run ruff format --check
```

#### One-Command Clean (Super Quick!)
```bash
# Fix everything in one go
uv run ruff check --fix && uv run ruff format
```

#### Configuration
Ruff is configured in `pyproject.toml` with:
- Line length: 100 characters
- Python 3.13 compatibility
- Import sorting (isort style)
- Selected linting rules for code quality
- Excludes `app/ai/prompts/` (contains template files)

## AI Architecture

### Multi-Agent System 🧠
```
app/agents/
├── coordinator_agent/       # Main Router & Intent Classifier
│   ├── agent.py            # Coordinator with 4 specialized agents
│   └── __init__.py
├── crop_diagnosis_agent/    # Disease Identification (Gemini 2.5 Flash)
│   ├── agent.py            # Crop health analysis with Google Search
│   ├── prompt.py           # Specialized crop diagnosis prompts
│   └── __init__.py
├── market_agent/           # Market Data & Price Analysis
│   ├── agent.py            # Market intelligence with API tools
│   ├── prompt.py           # Market analysis prompts
│   ├── tools.py            # Smart API integration tools
│   └── __init__.py
├── rag_agent/              # Government Policies & Schemes
│   ├── agent.py            # RAG-based policy information
│   ├── prompt.py           # Government schemes prompts
│   └── __init__.py
└── general_query_agent/     # General Agricultural Guidance
    ├── agent.py            # General farming advice
    └── __init__.py
```

### Agent Capabilities
- **🎯 Coordinator Agent**: Routes queries to specialized agents with intelligent intent classification
- **🔬 Crop Diagnosis Agent**: AI-powered disease identification with treatment recommendations
- **🌾 Market Agent**: Real-time price analysis, trends, and revenue calculations
- **🏛️ RAG Agent**: Government schemes, subsidies, and agricultural policies
- **💬 General Query Agent**: Best practices, cultivation tips, and seasonal advice

## Core Features (Implemented)

### 1. AI Agent Invocation APIs ✅
- **Endpoints**: 
  - `POST /api/v1/invoke/voice` - Voice-to-voice AI interaction
  - `POST /api/v1/invoke/text` - Text-based AI interaction
- **Features**: Multilingual support, session management, intelligent routing
- **Status**: ✅ Fully Implemented

### 2. Crop Disease Diagnosis ✅
- **Endpoints**:
  - `POST /api/v1/crop-diagnosis/analyze-image` - Analyze from GCS URL
  - `POST /api/v1/crop-diagnosis/analyze-upload` - Upload & analyze
- **Features**: Image upload to GCS, structured diagnosis, treatment recommendations
- **Status**: ✅ Fully Implemented

### 3. Supporting APIs ✅
- **Speech Processing**: `/api/v1/speech/transcribe`, `/api/v1/speech/synthesize`
- **Translation**: `/api/v1/translation/translate`, `/api/v1/translation/detect`
- **Market Data**: `/api/v1/market/*` endpoints
- **Status**: ✅ Fully Implemented

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point ✅
│   ├── agents/              # Multi-Agent System ✅
│   │   ├── coordinator_agent/   # Main router ✅
│   │   ├── crop_diagnosis_agent/ # Disease analysis ✅
│   │   ├── market_agent/        # Market intelligence ✅
│   │   ├── rag_agent/           # Government policies ✅
│   │   └── general_query_agent/ # General advice ✅
│   ├── api/v1/              # REST API Endpoints
│   │   ├── agent_invocation.py  # AI agent APIs ✅
│   │   ├── crop_diagnosis.py    # Crop analysis APIs ✅
│   │   ├── speech.py           # Speech processing ✅
│   │   ├── translation.py      # Translation APIs ✅
│   │   └── market_prices.py    # Market data APIs ✅
│   ├── models/              # Pydantic models ✅
│   ├── services/            # Business logic ✅
│   ├── core/                # Configuration ✅
│   └── utils/               # Utilities ✅
├── scripts/
│   └── deploy_simple.sh     # Cloud Run deployment ✅
├── pyproject.toml           # uv configuration ✅
└── README.md               # This file ✅
```
