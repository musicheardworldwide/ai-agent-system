#!/bin/bash

# AI Agent System Deployment Script

echo "Starting AI Agent System deployment..."

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
LLM_MODEL=llama3.2:3b-instruct-q4_0
EMBEDDING_MODEL=nomic-embed-text
DATABASE_URI=sqlite:///data/ai_agent.db
DEBUG=False
PORT=5000
EOL
    echo "Please edit the .env file to add your API_KEY and other sensitive information."
fi

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "Running in Docker environment..."
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Start the application
    python app.py
else
    echo "Running in local environment..."
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo "Python 3 is not installed. Please install Python 3 and try again."
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    # Initialize the database
    echo "Initializing database..."
    python -c "from backend.app.models import init_db; init_db()"
    
    # Start the application
    echo "Starting the application..."
    python app.py
fi
