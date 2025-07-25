#!/bin/bash
# Kisan AI - Simple Cloud Run Deployment Script
# ==============================================
# This script handles everything from gcloud setup to deployment

set -e  # Exit on any error

# Configuration
PROJECT_ID="kisanai-466809"
SERVICE_NAME="kisan-ai-api"
REGION="asia-south1"  # Mumbai region
SERVICE_ACCOUNT="kisan-ai-service-account@${PROJECT_ID}.iam.gserviceaccount.com"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Kisan AI - Cloud Run Deployment${NC}"
echo "====================================="
echo "Project: ${PROJECT_ID}"
echo "Service: ${SERVICE_NAME}"
echo "Region: ${REGION}"
echo ""

# Function to check if gcloud is installed
check_gcloud() {
    if command -v gcloud &> /dev/null; then
        echo -e "${GREEN}✅ gcloud CLI is installed${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  gcloud CLI not found${NC}"
        return 1
    fi
}

# Function to setup gcloud authentication and project
setup_gcloud() {
    echo -e "${BLUE}🔐 Setting up gcloud authentication...${NC}"
    
    # Check if already authenticated
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        echo -e "${GREEN}✅ Already authenticated with gcloud${NC}"
    else
        echo "Opening browser for authentication..."
        gcloud auth login
    fi
    
    # Set project
    echo -e "${BLUE}🎯 Setting project to ${PROJECT_ID}...${NC}"
    gcloud config set project ${PROJECT_ID}
    
    # Verify project
    CURRENT_PROJECT=$(gcloud config get-value project)
    if [ "${CURRENT_PROJECT}" != "${PROJECT_ID}" ]; then
        echo -e "${RED}❌ Failed to set project. Current: ${CURRENT_PROJECT}${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Project set to ${PROJECT_ID}${NC}"
}

# Function to generate requirements.txt from pyproject.toml
generate_requirements() {
    echo -e "${BLUE}📦 Generating requirements.txt from pyproject.toml...${NC}"
    
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}❌ uv not found. Please install it first: pip install uv${NC}"
        exit 1
    fi
    
    # Generate requirements.txt and remove problematic editable install line
    uv export --format requirements-txt --no-hashes | sed '/^-e \.$/d' > requirements.txt
    
    # Verify uvicorn is included
    if grep -q "uvicorn" requirements.txt; then
        echo -e "${GREEN}✅ requirements.txt generated successfully (uvicorn included)${NC}"
    else
        echo -e "${RED}❌ uvicorn not found in requirements.txt${NC}"
        exit 1
    fi
}

# Function to read environment variables from .env file
load_env_vars() {
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  No .env file found. Using default production values.${NC}"
        return
    fi
    
    echo -e "${BLUE}📄 Loading environment variables from .env file...${NC}"
    
    # Read .env file and build env vars string
    ENV_VARS=""
    
    # Variables to exclude from Cloud Run (local development only)
    EXCLUDE_VARS=("GOOGLE_APPLICATION_CREDENTIALS" "DEBUG" "HOST" "PORT")
    
    while IFS= read -r line; do
        # Skip comments and empty lines
        if [[ $line =~ ^#.*$ ]] || [[ -z "$line" ]]; then
            continue
        fi
        
        # Extract key=value pairs
        if [[ $line =~ ^([A-Z_][A-Z0-9_]*)=(.*)$ ]]; then
            key="${BASH_REMATCH[1]}"
            value="${BASH_REMATCH[2]}"
            
            # Skip excluded variables
            skip=false
            for exclude in "${EXCLUDE_VARS[@]}"; do
                if [[ "$key" == "$exclude" ]]; then
                    skip=true
                    break
                fi
            done
            
            if [[ "$skip" == false ]]; then
                if [[ -n "$ENV_VARS" ]]; then
                    ENV_VARS="${ENV_VARS},${key}=${value}"
                else
                    ENV_VARS="${key}=${value}"
                fi
            fi
        fi
    done < .env
    
    # Add production-specific overrides
    if [[ -n "$ENV_VARS" ]]; then
        ENV_VARS="ENVIRONMENT=production,DEBUG=false,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},VERTEX_AI_REGION=${REGION},${ENV_VARS}"
    else
        ENV_VARS="ENVIRONMENT=production,DEBUG=false,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},VERTEX_AI_REGION=${REGION}"
    fi
    
    echo -e "${GREEN}✅ Environment variables loaded${NC}"
}

# Function to deploy to Cloud Run
deploy_service() {
    echo -e "${BLUE}🚀 Deploying Kisan AI API to Cloud Run...${NC}"
    
    # Load environment variables
    load_env_vars
    
    # Deploy using source-based deployment
    gcloud run deploy ${SERVICE_NAME} \
        --source . \
        --region ${REGION} \
        --allow-unauthenticated \
        --memory 1Gi \
        --cpu 1 \
        --timeout 300 \
        --concurrency 100 \
        --min-instances 0 \
        --max-instances 10 \
        --service-account="${SERVICE_ACCOUNT}" \
        --set-env-vars="${ENV_VARS}" \
        --quiet
    
    echo -e "${GREEN}✅ Deployment completed!${NC}"
}

# Function to get and test service URL
test_deployment() {
    echo -e "${BLUE}🧪 Testing deployment...${NC}"
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
        --region ${REGION} \
        --format 'value(status.url)')
    
    if [ -z "${SERVICE_URL}" ]; then
        echo -e "${RED}❌ Failed to get service URL${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}🌐 Service URL: ${SERVICE_URL}${NC}"
    
    # Test health endpoint
    echo "Testing health endpoint..."
    if curl -f "${SERVICE_URL}/health" &> /dev/null; then
        echo -e "${GREEN}✅ Health check passed!${NC}"
    else
        echo -e "${YELLOW}⚠️  Health check failed (this is normal for first deployment)${NC}"
    fi
    
    # Display useful URLs
    echo ""
    echo -e "${GREEN}🎉 Deployment Successful!${NC}"
    echo "=============================="
    echo -e "${GREEN}🌐 API URL: ${SERVICE_URL}${NC}"
    echo -e "${GREEN}📊 Health: ${SERVICE_URL}/health${NC}"
    echo -e "${GREEN}📚 Docs: ${SERVICE_URL}/docs${NC}"
    echo -e "${GREEN}🔍 Redoc: ${SERVICE_URL}/redoc${NC}"
    echo ""
    echo -e "${BLUE}📝 Useful commands:${NC}"
    echo "• View logs: gcloud logs tail /projects/${PROJECT_ID}/logs/run.googleapis.com%2Frequests"
    echo "• Update service: gcloud run deploy ${SERVICE_NAME} --source . --region ${REGION}"
    echo "• Delete service: gcloud run services delete ${SERVICE_NAME} --region ${REGION}"
}

# Main execution
main() {
    # Check if we're in the right directory
    if [ ! -f "pyproject.toml" ] || [ ! -f "app/main.py" ]; then
        echo -e "${RED}❌ Please run this script from the backend directory${NC}"
        echo "Expected files: pyproject.toml, app/main.py"
        exit 1
    fi
    
    # Step 1: Check gcloud CLI
    if ! check_gcloud; then
        echo -e "${RED}❌ gcloud CLI not found. Please install it first:${NC}"
        echo "  brew install --cask google-cloud-sdk"
        exit 1
    fi
    
    # Step 2: Setup authentication and project
    setup_gcloud
    
    # Step 3: Generate requirements.txt from pyproject.toml
    generate_requirements
    
    # Step 4: Deploy the service
    deploy_service
    
    # Step 5: Test the deployment
    test_deployment
}

# Run main function
main "$@" 