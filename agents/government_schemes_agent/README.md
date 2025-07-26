# Government Schemes RAG Agent

A specialized AI agent that helps farmers navigate Indian government agricultural schemes using Retrieval-Augmented Generation (RAG) technology.

## Architecture Overview

This agent uses a **decoupled architecture** where:
- **Corpus Setup** is done once manually via `corpus_setup.py`
- **Agent Runtime** simply references the existing corpus via `corpus_manager.py`

This approach provides better performance and clearer separation of concerns.

## Components

### 1. One-Time Setup Components

#### `corpus_setup.py`
- Creates and configures the Vertex AI RAG corpus
- Ingests government scheme documents
- Saves corpus configuration to `corpus_config.json`
- **Run once during deployment**

#### `startup.py`
- Creates sample government scheme documents
- Environment validation
- **Run once for development setup**

### 2. Runtime Components

#### `corpus_manager.py`
- Lightweight manager that references existing corpus
- Loads configuration from `corpus_config.json`
- Creates retrieval tools for the agent
- **Used by agent at runtime**

#### `agent.py`
- Main agent with RAG-enabled Gemini model
- Uses corpus manager for retrieval
- Handles query processing and response generation

#### `tools.py`
- Specialized tools for eligibility checking
- Document validation
- Scheme categorization

#### `prompt.py`
- System prompts and response templates
- Multilingual support (Hindi, English, Kannada)

## Setup Instructions

### 1. Environment Setup

Set required environment variables:
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
export SCHEMES_DOCUMENTS_PATH=./schemes_documents
```

### 2. One-Time Corpus Setup

#### Option A: Automated Setup (Recommended)
```bash
cd agents
python setup_government_schemes.py
```

#### Option B: Manual Setup
```bash
cd agents/government_schemes_agent

# Create sample documents
python startup.py

# Setup RAG corpus
python corpus_setup.py --project-id YOUR_PROJECT_ID

# Check status
python corpus_setup.py --project-id YOUR_PROJECT_ID --status-only
```

### 3. Verify Setup

Check that `corpus_config.json` was created:
```bash
cat corpus_config.json
```

Expected output:
```json
{
  "corpus_name": "projects/PROJECT_ID/locations/us-central1/ragCorpora/CORPUS_ID",
  "display_name": "government-schemes-corpus",
  "project_id": "your-project-id",
  "location": "us-central1",
  "embedding_model": "text-embedding-005",
  "chunk_size": 512,
  "chunk_overlap": 100,
  "file_count": 4,
  "created_at": "2024-01-26T23:42:35+05:30",
  "status": "ready"
}
```

## Usage

### Backend Integration

The agent is automatically available via the backend API:

```bash
# Start backend
cd backend
uv run python -m uvicorn app.main:app --reload

# Test health
curl http://localhost:8000/api/v1/government-schemes/health

# Query schemes
curl -X POST http://localhost:8000/api/v1/government-schemes/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is PM-KISAN scheme?"}'
```

### Direct Agent Usage

```python
from government_schemes_agent.agent import GovernmentSchemesAgent

# Initialize agent (fast - just loads existing corpus)
agent = GovernmentSchemesAgent()
await agent.initialize()

# Query schemes
result = await agent.query_schemes("I need subsidy for drip irrigation")
print(result['response'])
```

## API Endpoints

- `POST /api/v1/government-schemes/query` - Main scheme queries
- `POST /api/v1/government-schemes/eligibility-check` - Eligibility checking
- `GET /api/v1/government-schemes/categories` - Scheme categories
- `POST /api/v1/government-schemes/validate-documents` - Document validation
- `GET /api/v1/government-schemes/corpus-status` - Corpus health check

## Maintenance

### Adding New Documents

1. Add documents to `schemes_documents/` directory
2. Re-run corpus setup:
   ```bash
   python corpus_setup.py --project-id YOUR_PROJECT_ID --force-recreate
   ```
3. Restart backend service

### Updating Corpus Configuration

1. Modify settings in `corpus_setup.py`
2. Re-run setup with `--force-recreate`
3. Restart backend service

### Monitoring

Check corpus status:
```bash
curl http://localhost:8000/api/v1/government-schemes/corpus-status
```

## Benefits of Decoupled Architecture

### ✅ Performance
- Agent initialization is fast (no corpus setup)
- No document processing during runtime
- Consistent response times

### ✅ Reliability
- Corpus setup failures don't affect runtime
- Clear separation of setup vs runtime concerns
- Easier debugging and monitoring

### ✅ Scalability
- Multiple agent instances can share same corpus
- Corpus updates are independent of agent deployments
- Better resource utilization

### ✅ Maintenance
- Clear setup procedures
- Easier to update documents
- Simpler deployment process

## Troubleshooting

### Agent Initialization Fails
```
Error: Failed to initialize corpus manager
```
**Solution**: Run corpus setup first:
```bash
python corpus_setup.py --project-id YOUR_PROJECT_ID
```

### Corpus Not Found
```
Error: Corpus configuration file not found
```
**Solution**: Ensure `corpus_config.json` exists in the agent directory

### Authentication Issues
```
Error: Failed to authenticate with Google Cloud
```
**Solution**: Set up Application Default Credentials:
```bash
gcloud auth application-default login
```

### No Documents in Corpus
```
Warning: file_count: 0
```
**Solution**: Add documents and re-run setup with `--force-recreate`

## File Structure

```
government_schemes_agent/
├── README.md                 # This file
├── corpus_config.json        # Generated corpus configuration
├── corpus_setup.py          # One-time corpus setup
├── corpus_manager.py        # Runtime corpus manager
├── agent.py                 # Main agent
├── tools.py                 # Specialized tools
├── prompt.py                # System prompts
└── startup.py               # Development utilities
```

## Development

### Testing
```bash
cd agents
python test_government_schemes.py
```

### Adding New Tools
1. Add function to `tools.py`
2. Import in `agent.py`
3. Add to agent tools list

### Modifying Prompts
1. Update prompts in `prompt.py`
2. Restart backend service
3. Test with sample queries

---

For more detailed documentation, see `/backend/docs/government_schemes_rag.md`
