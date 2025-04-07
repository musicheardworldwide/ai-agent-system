#!/bin/bash

# AI Agent System Installation Script
# This script sets up the AI Agent System with all its components

set -e  # Exit on error

# Print colored messages
print_message() {
  echo -e "\e[1;34m>> $1\e[0m"
}

print_success() {
  echo -e "\e[1;32m>> $1\e[0m"
}

print_error() {
  echo -e "\e[1;31m>> $1\e[0m"
}

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
  print_message "Note: Running without sudo. Some operations might require elevated privileges."
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
  print_message "Creating .env file..."
  cat > .env << EOL
# AI Agent System Environment Variables
API_BASE_URL=https://api.lastwinnersllc.com
API_KEY=
LLM_MODEL=llama3.2
EMBEDDING_MODEL=nomic-embed-text
DATABASE_URI=sqlite:///ai_agent.db
MASTER_KEY=change-this-in-production
EOL
  print_success "Created .env file. Please edit it with your API key and other settings."
else
  print_message ".env file already exists. Skipping creation."
fi

# Check for Python 3.8+
print_message "Checking Python version..."
if command -v python3 &>/dev/null; then
  python_version=$(python3 --version | cut -d " " -f 2)
  python_major=$(echo $python_version | cut -d. -f1)
  python_minor=$(echo $python_version | cut -d. -f2)
  
  if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 8 ]); then
    print_error "Python 3.8+ is required. Found Python $python_version"
    exit 1
  else
    print_success "Found Python $python_version"
  fi
else
  print_error "Python 3 not found. Please install Python 3.8 or higher."
  exit 1
fi

# Check for pip
print_message "Checking for pip..."
if ! command -v pip3 &>/dev/null; then
  print_error "pip3 not found. Please install pip for Python 3."
  exit 1
else
  print_success "Found pip3"
fi

# Check for Node.js
print_message "Checking for Node.js..."
if ! command -v node &>/dev/null; then
  print_error "Node.js not found. Please install Node.js 14 or higher."
  exit 1
else
  node_version=$(node --version)
  print_success "Found Node.js $node_version"
fi

# Check for npm
print_message "Checking for npm..."
if ! command -v npm &>/dev/null; then
  print_error "npm not found. Please install npm."
  exit 1
else
  npm_version=$(npm --version)
  print_success "Found npm $npm_version"
fi

# Install Python dependencies
print_message "Installing Python dependencies..."
pip3 install -r requirements.txt

# Install frontend dependencies
print_message "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Initialize the database
print_message "Initializing the database..."
python3 run.py init-db

# Build the frontend
print_message "Building the frontend..."
cd frontend
npm run build
cd ..

print_success "Installation completed successfully!"
print_message "To start the system, run: python3 run.py"
print_message "The web interface will be available at: http://localhost:5000"
