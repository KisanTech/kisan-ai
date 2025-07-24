# Kisan AI - Backend API

AI-Powered Agricultural Assistant for Google Agentic AI Day Hackathon

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
# Basic Settings
DEBUG=true
ENVIRONMENT=development

# Google Cloud (Required for AI features)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Indian Government APIs (For real market data)
DATA_GOV_API_KEY=your-data-gov-api-key
ENAM_API_KEY=your-enam-api-key

# Optional overrides (defaults work fine)
VERTEX_AI_REGION=us-central1
GEMINI_MODEL=gemini-2.0-flash-exp
SPEECH_LANGUAGE_CODE=kn-IN
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
uv run ruff check --fix && uv run ruff format && echo "✅ Code is clean!"
```

#### Configuration
Ruff is configured in `pyproject.toml` with:
- Line length: 100 characters
- Python 3.13 compatibility
- Import sorting (isort style)
- Selected linting rules for code quality
- Excludes `app/ai/prompts/` (contains template files)

## AI Architecture

### New Organized Structure 🧠
```
app/ai/
├── agents/          # Multi-Agent System
│   ├── orchestrator.py     # Routes queries to specialized agents
│   ├── crop_agent.py       # Disease identification (Gemini 2.0 Flash)
│   ├── voice_agent.py      # Kannada speech processing
│   └── market_agent.py     # Real-time price analysis
└── prompts/         # Prompt Engineering
    ├── crop_diagnosis/     # Disease identification prompts
    ├── voice_processing/   # Speech-to-text prompts
    └── market_analysis/    # Price analysis prompts
```

### Benefits of This Structure
- **Separation of Concerns**: Agents focus on AI logic, APIs handle HTTP
- **Prompt Management**: Centralized prompt templates for easy iteration
- **Testability**: Each agent can be tested independently
- **Scalability**: Easy to add new agents and prompts

## Core Features (MVP)

### 1. Crop Disease Identification
- **Endpoint**: `POST /api/v1/crop/diagnose`
- **Purpose**: Upload crop images for AI-powered disease diagnosis
- **Status**: 🚧 Needs Implementation

### 2. Voice Interface (Kannada)
- **Endpoints**: 
  - `POST /api/v1/voice/speech-to-text`
  - `POST /api/v1/voice/text-to-speech`
  - `POST /api/v1/voice/voice-query`
- **Purpose**: Kannada voice interaction for farmers
- **Status**: 🚧 Needs Implementation

### 3. Market Price Display  
- **Endpoints**:
  - `GET /api/v1/market/current`
  - `GET /api/v1/market/trends/{crop}`
  - `GET /api/v1/market/markets`
- **Purpose**: Real-time crop price information
- **Status**: 🚧 Needs Implementation

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point ✅
│   ├── core/
│   │   └── config.py        # Configuration management ✅
|   ├── agents/              # AI Agents
│   ├── api/v1/
│   │   ├── crop_diagnosis.py    # Crop disease endpoints 🚧
│   │   ├── voice_interface.py   # Voice/speech endpoints 🚧
│   │   └── market_prices.py     # Market data endpoints 🚧
│   ├── models/              # Pydantic models 📝
│   └── services/            # Business logic 📝
├── pyproject.toml           # uv configuration ✅
└── README.md               # This file ✅
```

## Implementation TODOs

### High Priority (Hackathon MVP)
- [ ] **AI Agents**: Implement in `app/ai/agents/` directory
  - [ ] **Crop Diagnosis Agent**: Gemini 2.0 Flash integration
  - [ ] **Voice Assistant Agent**: Kannada speech processing  
  - [ ] **Market Intelligence Agent**: Real-time price analysis
  - [ ] **Agent Orchestrator**: Basic routing logic
- [ ] **Prompt Management**: Structured prompts in `app/ai/prompts/`
- [ ] **API Integration**: Connect agents to FastAPI endpoints
- [ ] **Image Upload**: Google Cloud Storage integration
- [ ] **Basic Error Handling**: Graceful API error responses

### Medium Priority  
- [ ] **Pydantic Models**: Request/response validation
- [ ] **Service Layer**: Business logic separation in `app/services/`
- [ ] **Prompt Engineering**: Advanced prompt templates
- [ ] **Agent Context**: Memory and conversation state
- [ ] **Caching**: Redis for market price caching
- [ ] **Logging**: Structured logging for debugging

### Low Priority (Post-Hackathon)
- [ ] **Authentication**: User management system
- [ ] **Rate Limiting**: API usage controls
- [ ] **Monitoring**: Health checks and metrics
- [ ] **Docker**: Containerization

## Google Cloud Services

### Required APIs
1. **Vertex AI API** - Gemini 2.0 Flash for crop diagnosis
2. **Speech-to-Text API** - Kannada voice recognition
3. **Text-to-Speech API** - Kannada voice responses  
4. **Cloud Storage API** - Image and audio file storage

### Setup Commands
```bash
# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable speech.googleapis.com 
gcloud services enable texttospeech.googleapis.com
gcloud services enable storage.googleapis.com

# Create service account
gcloud iam service-accounts create project-kisan-sa
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:project-kisan-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

## Development Workflow

1. **Start with placeholders**: All endpoints return mock data ✅
2. **Implement one feature at a time**: Focus on working demos
3. **Test early and often**: Use the `/docs` endpoint for testing
4. **Keep it simple**: MVP focus, no over-engineering

## Team Coordination

### Zero-Setup Environment
The `.python-version` file ensures **everyone automatically uses Python 3.13**:
- New team members just run `uv sync` - no Python installation needed
- Consistent environment across all development machines
- No "works on my machine" issues during the hackathon

### Parallel Development
- **Backend Dev**: Implement API endpoints in `app/api/v1/` and Google Cloud integration
- **AI/ML Engineer**: Focus on agents in `app/ai/agents/` and prompts in `app/ai/prompts/`
- **Frontend Dev**: Use placeholder responses to build UI
- **Full-Stack**: Connect agents to APIs and help with testing

### AI Development Workflow
1. **Prompt Development**: Create and test prompts in `app/ai/prompts/`
2. **Agent Implementation**: Build agents in `app/ai/agents/` 
3. **API Integration**: Connect agents to FastAPI endpoints
4. **Testing**: Use `/docs` endpoint for agent testing

### Communication
- Update TODO comments as you implement features
- Test endpoints using FastAPI docs at `/docs`
- Commit frequently with clear messages

## Troubleshooting

### Common Issues
1. **Google Cloud Auth**: Ensure `GOOGLE_APPLICATION_CREDENTIALS` path is correct
2. **Import Errors**: Run `uv sync` to install dependencies
3. **Port Conflicts**: Change port in uvicorn command if 8000 is busy

### Debug Mode
Set `DEBUG=true` in `.env` for detailed error messages.

---

**Ready to build! 🚀**

The placeholder endpoints are working - now let's implement the real AI magic! 