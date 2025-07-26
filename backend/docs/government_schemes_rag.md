# Government Schemes RAG Agent Documentation

## Overview

The Government Schemes RAG Agent is a specialized AI agent that helps farmers navigate Indian government agricultural schemes using Retrieval-Augmented Generation (RAG) technology. It provides accurate, contextual information about subsidies, eligibility requirements, and application processes in simple terms.

## Architecture

### Components

1. **RAG Manager** (`rag_manager.py`)
   - Manages Vertex AI RAG corpus
   - Handles document ingestion and processing
   - Configures embedding and retrieval settings

2. **Core Agent** (`agent.py`)
   - Main agent with RAG-enabled Gemini model
   - Query processing and response generation
   - Integration with specialized tools

3. **Specialized Tools** (`tools.py`)
   - Eligibility checking
   - Document validation
   - Scheme categorization
   - Application status tracking

4. **Backend Integration**
   - FastAPI endpoints for web access
   - Service layer for business logic
   - Pydantic models for data validation

## Features

### 🌾 Scheme Information
- Comprehensive information about 50+ agricultural schemes
- Eligibility criteria in simple terms
- Required documents and application processes
- Direct links to official portals

### 🔍 Smart Query Processing
- Natural language understanding in Hindi, English, and Kannada
- Intent recognition for different scheme categories
- Context-aware responses based on farmer profile

### ✅ Eligibility Checking
- Automated eligibility assessment
- Personalized recommendations
- Document requirement validation

### 📊 Scheme Categories
- **Irrigation**: PMKSY, Drip irrigation subsidies
- **Income Support**: PM-KISAN, Direct benefit transfers
- **Crop Insurance**: PM Fasal Bima Yojana
- **Credit Support**: Kisan Credit Card, Agricultural loans
- **Input Subsidies**: Fertilizer, seed, machinery subsidies
- **Technology**: Digital agriculture, precision farming

## API Endpoints

### Core Endpoints

#### 1. Query Schemes
```http
POST /api/v1/government-schemes/query
```

**Request:**
```json
{
  "query": "मुझे ड्रिप सिंचाई के लिए सब्सिडी चाहिए",
  "language": "hindi",
  "user_context": {
    "location": "Punjab",
    "crop_type": "wheat"
  }
}
```

**Response:**
```json
{
  "success": true,
  "response": "🌾 **Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)**\n\n**विवरण**: ड्रिप सिंचाई सिस्टम के लिए 90% तक सब्सिडी...",
  "source": "rag_model",
  "query": "मुझे ड्रिप सिंचाई के लिए सब्सिडी चाहिए",
  "timestamp": "2024-01-26T23:33:15+05:30"
}
```

#### 2. Check Eligibility
```http
POST /api/v1/government-schemes/eligibility-check
```

**Request:**
```json
{
  "query": "Which schemes am I eligible for?",
  "farmer_profile": {
    "land_size": "2 acres",
    "crop_type": "rice",
    "location": "Punjab",
    "farmer_category": "small"
  }
}
```

#### 3. Get Scheme Categories
```http
GET /api/v1/government-schemes/categories
```

#### 4. Validate Documents
```http
POST /api/v1/government-schemes/validate-documents
```

#### 5. Application Status
```http
POST /api/v1/government-schemes/application-status
```

#### 6. Corpus Management
```http
GET /api/v1/government-schemes/corpus-status
POST /api/v1/government-schemes/refresh-corpus
```

## Setup Instructions

### 1. Environment Configuration

Create `.env` file in the agents directory:
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_STAGING_BUCKET=your-staging-bucket
SCHEMES_DOCUMENTS_PATH=./schemes_documents
```

### 2. Document Preparation

Place government scheme documents in the `schemes_documents` directory:
```
schemes_documents/
├── pm_kisan_scheme.pdf
├── pmksy_irrigation.pdf
├── pm_fasal_bima.pdf
├── kisan_credit_card.pdf
└── state_specific_schemes/
    ├── punjab_schemes.pdf
    └── karnataka_schemes.pdf
```

Supported formats:
- PDF files (`.pdf`)
- Text files (`.txt`)
- Word documents (`.docx`, `.doc`)

### 3. Installation

Install dependencies in the agents directory:
```bash
cd agents
uv sync
```

### 4. Initialize the Agent

Run the startup script:
```bash
cd agents/government_schemes_agent
python startup.py
```

### 5. Start the Backend

```bash
cd backend
uv run python -m uvicorn app.main:app --reload
```

## Usage Examples

### Example 1: Subsidy Query (Hindi)
```python
import requests

response = requests.post("http://localhost:8000/api/v1/government-schemes/query", json={
    "query": "मुझे ड्रिप सिंचाई के लिए सब्सिडी चाहिए",
    "language": "hindi"
})

print(response.json()["response"])
```

**Expected Output:**
```
🌾 **Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)**

**विवरण**: ड्रिप सिंचाई सिस्टम के लिए 90% तक सब्सिडी

**पात्रता**:
✅ सभी श्रेणी के किसान
✅ न्यूनतम 0.5 एकड़ भूमि

**लाभ**:
💰 90% तक सब्सिडी (छोटे किसानों के लिए)
💰 40-60% पानी की बचत

**आवश्यक दस्तावेज**:
📄 आधार कार्ड
📄 भूमि के कागजात
📄 बैंक पासबुक

🔗 **Direct Link**: https://pmksy.gov.in/microIrrigation/
📞 **Helpline**: 1800-180-1551
```

### Example 2: Eligibility Check
```python
response = requests.post("http://localhost:8000/api/v1/government-schemes/eligibility-check", json={
    "query": "Which schemes am I eligible for?",
    "farmer_profile": {
        "land_size": "1.5 acres",
        "crop_type": "vegetables",
        "location": "Karnataka",
        "farmer_category": "small"
    }
})

eligible_schemes = response.json()["eligible_schemes"]
for scheme in eligible_schemes:
    print(f"✅ {scheme['scheme_name']}: {scheme['reasons'][0]}")
```

### Example 3: Document Validation
```python
response = requests.post("http://localhost:8000/api/v1/government-schemes/validate-documents", json={
    "scheme_type": "pm_kisan",
    "available_documents": [
        "aadhaar_card",
        "land_records",
        "bank_account"
    ]
})

result = response.json()
if result["valid"]:
    print("✅ All required documents available!")
else:
    print("❌ Missing documents:")
    for doc in result["missing_documents"]:
        print(f"  - {doc}")
```

## RAG Configuration

### Embedding Model
- **Model**: `text-embedding-005`
- **Dimensions**: 768
- **Language Support**: Multilingual

### Chunking Strategy
- **Chunk Size**: 512 tokens
- **Overlap**: 100 tokens
- **Strategy**: Semantic chunking with paragraph boundaries

### Retrieval Settings
- **Top-K**: 5 relevant chunks
- **Similarity Threshold**: 0.7
- **Reranking**: Enabled for better relevance

## Monitoring and Maintenance

### Health Checks
```bash
curl http://localhost:8000/api/v1/government-schemes/health
```

### Corpus Status
```bash
curl http://localhost:8000/api/v1/government-schemes/corpus-status
```

### Refresh Corpus
```bash
curl -X POST http://localhost:8000/api/v1/government-schemes/refresh-corpus \
  -H "Content-Type: application/json" \
  -d '{"force_reimport": false}'
```

## Performance Metrics

### Target Performance
- **Response Time**: < 3 seconds
- **Accuracy**: > 90% relevant scheme retrieval
- **Language Support**: Hindi, English, Kannada
- **Concurrent Users**: 100+

### Monitoring
- Query response times
- RAG retrieval accuracy
- User satisfaction scores
- Error rates and types

## Troubleshooting

### Common Issues

1. **RAG Corpus Not Initialized**
   ```
   Error: RAG corpus not initialized
   ```
   **Solution**: Check environment variables and run startup script

2. **No Documents Found**
   ```
   Warning: No documents found in ./schemes_documents
   ```
   **Solution**: Add scheme documents to the configured directory

3. **Authentication Error**
   ```
   Error: Failed to authenticate with Google Cloud
   ```
   **Solution**: Set up Application Default Credentials

4. **Model Not Available**
   ```
   Error: The video model is currently not supported for language
   ```
   **Solution**: Agent automatically handles model selection per language

### Debug Mode
Enable debug logging:
```python
import logging
logging.getLogger("project-kisan").setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features
- Real-time scheme updates from government APIs
- Application status tracking integration
- Voice-based scheme queries
- Regional scheme variations
- Personalized recommendations based on farmer history

### Integration Opportunities
- Integration with existing voice chat system
- Mobile app notifications for new schemes
- WhatsApp bot for scheme information
- SMS alerts for application deadlines

## Security Considerations

### Data Privacy
- No personal information stored in RAG corpus
- Secure handling of farmer profile data
- Compliance with data protection regulations

### Access Control
- API rate limiting
- Authentication for sensitive operations
- Audit logging for all queries

## Support

### Documentation
- API documentation: `/docs` endpoint
- Code examples in repository
- Integration guides for developers

### Contact
- Technical issues: Create GitHub issue
- Feature requests: Submit enhancement request
- General support: Contact development team

---

*This documentation is part of the Kisan AI platform. For the latest updates, check the repository.*
