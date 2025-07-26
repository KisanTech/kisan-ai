# Government Schemes RAG Agent Implementation Plan

## Overview
Create a RAG (Retrieval-Augmented Generation) agent that helps farmers navigate government agricultural schemes by providing information about subsidies, eligibility requirements, and application processes in simple terms.

## Architecture Components

### 1. RAG Corpus Setup
- **Purpose**: Store and index government scheme documents
- **Data Source**: Local government scheme documents (PDFs, text files)
- **Embedding Model**: `text-embedding-005` for semantic search
- **Chunking Strategy**: 512 tokens with 100 token overlap for optimal retrieval

### 2. Agent Structure (Following existing pattern)
```
agents/government_schemes_agent/
├── __init__.py
├── agent.py           # Main agent configuration with RAG integration
├── rag_manager.py     # RAG corpus management and retrieval
├── prompt.py          # System prompts for government schemes
├── tools.py           # Scheme-specific tools and utilities
└── startup.py         # Initialization and corpus setup
```

### 3. Key Features

#### A. Document Processing
- **Input**: Government scheme documents in local directory
- **Processing**: Automatic chunking and embedding
- **Storage**: Vertex AI RAG Corpus for efficient retrieval

#### B. Query Understanding
- **Intent Detection**: Identify scheme categories (irrigation, fertilizer, crop insurance, etc.)
- **Entity Extraction**: Extract crop types, location, farmer category
- **Language Support**: Process queries in native languages (Hindi, Kannada)

#### C. Response Generation
- **Retrieval**: Top-K relevant scheme documents
- **Generation**: Gemini model with RAG context
- **Output Format**: 
  - Scheme name and brief description
  - Eligibility criteria in simple terms
  - Required documents
  - Application process steps
  - Direct portal links
  - Contact information

### 4. Implementation Steps

#### Step 1: Create RAG Manager
- Initialize Vertex AI RAG corpus
- Implement document ingestion pipeline
- Configure embedding and chunking parameters
- Add corpus management utilities

#### Step 2: Design Agent Prompts
- System prompt for government scheme assistance
- Context-aware response formatting
- Multilingual support instructions
- Safety guidelines for official information

#### Step 3: Implement Core Agent
- RAG-enabled Gemini model setup
- Query processing and retrieval logic
- Response formatting and validation
- Error handling for missing schemes

#### Step 4: Add Specialized Tools
- Scheme eligibility checker
- Document requirement generator
- Application status tracker (if APIs available)
- Portal link validator

#### Step 5: Integration & Testing
- Backend API endpoints
- Frontend integration
- Multi-language testing
- Accuracy validation with sample queries

## Technical Specifications

### Dependencies
```python
# Core RAG dependencies
from vertexai import rag
from vertexai.generative_models import GenerativeModel, Tool
from google.adk.agents import Agent

# Document processing
import PyPDF2  # For PDF processing
import docx    # For Word documents
```

### Environment Variables
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
SCHEMES_DOCUMENTS_PATH=/path/to/government/schemes
RAG_CORPUS_NAME=government-schemes-corpus
```

### API Endpoints
- `POST /api/v1/schemes/query` - Main scheme query endpoint
- `GET /api/v1/schemes/categories` - Available scheme categories
- `POST /api/v1/schemes/eligibility-check` - Check eligibility for specific schemes
- `GET /api/v1/schemes/corpus-status` - RAG corpus health check

## Sample Interactions

### Query 1: Subsidy Information
**Input**: "मुझे ड्रिप सिंचाई के लिए सब्सिडी चाहिए" (I need subsidy for drip irrigation)
**Output**:
```
🌾 **Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)**

**योजना का विवरण**: ड्रिप सिंचाई सिस्टम के लिए 90% तक सब्सिडी

**पात्रता**:
- सभी श्रेणी के किसान
- न्यूनतम 0.5 एकड़ भूमि
- भूमि का स्वामित्व प्रमाण

**आवश्यक दस्तावेज**:
- आधार कार्ड
- भूमि के कागजात
- बैंक पासबुक

**आवेदन प्रक्रिया**:
1. pmksy.gov.in पर जाएं
2. ऑनलाइन आवेदन भरें
3. दस्तावेज अपलोड करें
4. सत्यापन की प्रतीक्षा करें

🔗 **Direct Link**: https://pmksy.gov.in/microIrrigation/
📞 **Helpline**: 1800-180-1551
```

### Query 2: Crop Insurance
**Input**: "What insurance schemes are available for wheat crop?"
**Output**: Detailed information about PM Fasal Bima Yojana with eligibility and process.

## Success Metrics
- **Accuracy**: >90% relevant scheme retrieval
- **Coverage**: Support for 50+ major agricultural schemes
- **Languages**: Hindi, English, Kannada support
- **Response Time**: <3 seconds for scheme queries
- **User Satisfaction**: Clear, actionable information

## Future Enhancements
- Real-time scheme updates from government APIs
- Application status tracking integration
- Personalized scheme recommendations
- Voice-based scheme queries
- Regional scheme variations
