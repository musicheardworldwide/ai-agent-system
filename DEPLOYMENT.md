# AI Agent System Deployment Guide

This guide provides instructions for deploying the AI Agent System using different methods.

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher (for frontend development)
- Docker and Docker Compose (optional, for containerized deployment)
- API key for lastwinnersllc.com

## Deployment Options

The AI Agent System can be deployed using one of the following methods:

### 1. Using the Deployment Script

The simplest way to deploy the system is using the provided deployment script:

```bash
./deploy.sh
```

This script will:
- Create necessary directories
- Set up a virtual environment
- Install dependencies
- Initialize the database
- Start the application

### 2. Using Docker Compose

For containerized deployment, use Docker Compose:

```bash
docker-compose up -d
```

This will build and start the application in a Docker container, exposing it on port 5000.

### 3. Manual Deployment

If you prefer to deploy manually:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in a `.env` file:
   ```
   API_BASE_URL=https://api.lastwinnersllc.com
   LLM_MODEL=llama3.2
   EMBEDDING_MODEL=nomic-embed-text
   API_KEY=your_api_key_here
   DATABASE_URI=sqlite:///data/ai_agent.db
   DEBUG=False
   PORT=5000
   ```

4. Initialize the database:
   ```bash
   python -c "from backend.app.models import init_db; init_db()"
   ```

5. Start the application:
   ```bash
   python app.py
   ```

## Accessing the Application

Once deployed, the application will be available at:

- Local deployment: http://localhost:5000
- Docker deployment: http://localhost:5000

## Configuration

The system can be configured through:

1. Environment variables in the `.env` file
2. The Settings interface in the web application
3. Command-line arguments when starting the application

## Troubleshooting

If you encounter issues during deployment:

1. Check the logs in the `logs` directory
2. Ensure all required environment variables are set
3. Verify that the API key is valid
4. Check that the required ports are available

## Security Considerations

- The API key should be kept secure and not shared
- For production deployments, consider using HTTPS
- Regularly update dependencies to address security vulnerabilities
