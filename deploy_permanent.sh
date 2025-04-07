#!/bin/bash

# AI Agent System Permanent Deployment Script

echo "Starting AI Agent System permanent deployment..."

# Create necessary directories
mkdir -p data
mkdir -p logs
mkdir -p screenshots

# Check if .env file exists, create if not
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOL
# AI Agent System Environment Variables
API_BASE_URL=https://api.lastwinnersllc.com
LLM_MODEL=llama3.2
EMBEDDING_MODEL=nomic-embed-text
DATABASE_URI=sqlite:///data/ai_agent.db
DEBUG=False
PORT=5000
EOL
    echo "Please edit the .env file to add your API_KEY and other sensitive information."
fi

# Build the frontend
echo "Building frontend for production deployment..."
python build_frontend.py

# Check if deployment platform is specified
if [ -z "$1" ]; then
    echo "No deployment platform specified. Usage: ./deploy_permanent.sh [netlify|vercel|github]"
    echo "Defaulting to netlify deployment."
    PLATFORM="netlify"
else
    PLATFORM=$1
fi

# Check if API key is provided
if [ -z "$2" ]; then
    echo "No API key provided. Usage: ./deploy_permanent.sh [platform] [api_key] [site_name]"
    echo "Please provide an API key for the selected platform."
    exit 1
else
    API_KEY=$2
fi

# Check if site name is provided
if [ -z "$3" ]; then
    SITE_NAME="ai-agent-system"
    echo "No site name provided. Using default: $SITE_NAME"
else
    SITE_NAME=$3
fi

# Create deployment configuration
echo "Creating deployment configuration..."
cat > deployment_config.json << EOL
{
    "apiKey": "$API_KEY",
    "siteName": "$SITE_NAME",
    "deploymentType": "$PLATFORM"
}
EOL

# Start the deployment process
echo "Starting deployment to $PLATFORM..."
python -c "
import json
import requests
import time
import sys

# Load deployment configuration
with open('deployment_config.json', 'r') as f:
    config = json.load(f)

# Start deployment
response = requests.post('http://localhost:5000/api/deploy/website', json=config)
if response.status_code != 200:
    print(f'Error starting deployment: {response.text}')
    sys.exit(1)

deployment_data = response.json()
deployment_id = deployment_data['deploymentId']
print(f'Deployment started with ID: {deployment_id}')

# Poll for deployment status
max_attempts = 60
attempts = 0
while attempts < max_attempts:
    status_response = requests.get(f'http://localhost:5000/api/deploy/status/{deployment_id}')
    if status_response.status_code == 200:
        status_data = status_response.json()
        if status_data['status'] == 'success':
            print(f'Deployment successful! Your website is available at: {status_data.get(\"url\")}')
            break
        elif status_data['status'] == 'failed':
            print(f'Deployment failed: {status_data.get(\"message\")}')
            sys.exit(1)
        else:
            print(f'Deployment status: {status_data[\"status\"]}')
    
    attempts += 1
    time.sleep(5)

if attempts >= max_attempts:
    print('Deployment timed out. Please check the logs for more information.')
    sys.exit(1)
"

# Clean up deployment configuration
rm deployment_config.json

echo "Deployment process completed."
