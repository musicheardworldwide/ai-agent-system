# AI Agent System Documentation

## Overview

The AI Agent System is a comprehensive open-interpreter system with smart memory capabilities, built around the core principles of extensibility, intelligence, and self-improvement. The system leverages the power of large language models (specifically llama3.2) and embeddings (nomic-embed-text) to provide a versatile AI assistant that can understand, learn from, and adapt to user interactions.

## System Architecture

The system is built with a modular architecture consisting of the following core components:

1. **Core Interpreter System**: Based on open-interpreter, this component serves as the central brain of the system, processing user queries and coordinating responses.

2. **RAG Memory System**: A Retrieval-Augmented Generation system that enhances the interpreter's responses with relevant context from past conversations and knowledge.

3. **Database Agent**: An intelligent component that manages the system's knowledge base, organizing information for efficient retrieval and learning.

4. **Custom Tools Manager**: Allows the system to dynamically add and use custom tools with context awareness.

5. **Environment Manager**: Securely handles API keys, secrets, and environment variables.

6. **Frontend Interface**: A comprehensive web interface with full logging capabilities for monitoring system activity.

7. **DevChat Interpreter Model**: A specialized component that maintains a structured understanding of the codebase, enabling code intelligence and self-improvement.

## Key Features

- **Smart Memory System**: Backed by RAG on level one, the system remembers past conversations and learns from them.
- **Knowledge Base Management**: Automatically organizes information into a structured database.
- **Custom Tools**: Can be added dynamically with context awareness.
- **Real-time Context**: Maintains awareness of past conversation knowledge.
- **Environment Management**: Special functions to view/add API and other secrets securely.
- **Self-Improvement**: The DevChat interpreter model continuously monitors the codebase, identifies potential improvements, and proposes changes.
- **Comprehensive Logging**: Full visibility into system operations, success/failure of actions.

## Installation Options

The system can be deployed in three different ways:

### 1. Using the Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Create a default .env file if it doesn't exist
- Check for required dependencies
- Install Python and Node.js dependencies
- Initialize the database
- Build the frontend

### 2. Using Docker

```bash
docker-compose up -d
```

This will build and start the system in a containerized environment.

### 3. Manual Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install and build frontend
cd frontend
npm install
npm run build
cd ..

# Initialize database
python run.py init-db

# Start the application
python run.py
```

## API Endpoints

### Core Chat API

- `POST /api/chat`: Main endpoint for interacting with the interpreter
  - Parameters: `query` (string), `stream` (boolean, optional)

### Tools API

- `GET /api/tools`: List all registered tools
- `POST /api/tools`: Register a new tool
- `GET /api/tools/{id}`: Get a specific tool
- `PUT /api/tools/{id}`: Update a tool
- `DELETE /api/tools/{id}`: Delete a tool

### Tasks API

- `GET /api/tasks`: List all tasks
- `POST /api/tasks`: Create a new task
- `GET /api/tasks/{id}`: Get a specific task
- `PUT /api/tasks/{id}`: Update a task
- `DELETE /api/tasks/{id}`: Delete a task
- `POST /api/tasks/{id}/execute`: Execute a specific task

### Knowledge API

- `GET /api/knowledge`: List all knowledge base entries
- `POST /api/knowledge`: Create a new knowledge base entry
- `GET /api/knowledge/{id}`: Get a specific knowledge base entry
- `PUT /api/knowledge/{id}`: Update a knowledge base entry
- `DELETE /api/knowledge/{id}`: Delete a knowledge base entry

### Environment API

- `GET /api/env`: List all environment variables
- `POST /api/env`: Create or update an environment variable
- `GET /api/env/{key}`: Get a specific environment variable
- `DELETE /api/env/{key}`: Delete an environment variable

### DevChat API

- `POST /api/dev-chat/query`: Process a natural language query about the codebase
- `GET /api/dev-chat/files`: List all files in the codebase
- `GET /api/dev-chat/files/{file_path}`: Get information about a specific file
- `GET /api/dev-chat/impact/{file_path}`: Get impact analysis for a specific file
- `GET /api/dev-chat/database-interactions`: Get all functions that interact with the database
- `GET /api/dev-chat/search`: Search the codebase using semantic search
- `GET /api/dev-chat/stats`: Get statistics about the codebase
- `GET /api/dev-chat/map`: Get a visual map of the code
- `POST /api/dev-chat/rescan`: Rescan the entire project

## Frontend Components

The system includes a comprehensive web interface with the following components:

1. **Dashboard**: Overview of system status and statistics
2. **Chat**: Main interface for interacting with the interpreter
3. **Tools**: Interface for managing custom tools
4. **Tasks**: Interface for creating and managing tasks
5. **Logs**: Comprehensive logging interface
6. **Code Development Agent**: Interface for the self-improving code development agent
7. **DevChat**: Interface for querying the codebase

## DevChat Interpreter Model

The DevChat interpreter model is a specialized component that maintains a structured understanding of the codebase. It provides the following capabilities:

1. **Dynamic Code Mapping**: Continuously parses and indexes all source files in the project.
2. **Relationship Awareness**: Captures and represents how modules interact.
3. **Realtime Updates**: Automatically detects code changes and updates the internal map.
4. **Code Intelligence Memory**: Stores code relationships in a vector database for semantic access.
5. **Integration Interface**: Provides a chat-based interface to query the live system map.

## Configuration

The system is configured using environment variables, which can be set in a `.env` file:

```
# API Configuration
API_BASE_URL=https://api.lastwinnersllc.com
API_KEY=your_api_key_here
LLM_MODEL=llama3.2
EMBEDDING_MODEL=nomic-embed-text

# Database Configuration
DATABASE_URI=sqlite:///ai_agent.db

# Security
SECRET_KEY=change_this_to_a_secure_random_string
MASTER_KEY=change_this_in_production

# Development Settings
FLASK_ENV=development
DEBUG=True
```

## Usage Examples

### Chat Interaction

The primary way to interact with the system is through the chat interface. Simply type your query and the system will respond with the most appropriate answer, leveraging its memory and knowledge base.

### Adding Custom Tools

Custom tools can be added through the Tools interface. Each tool requires:
- A name
- A description
- Python code that implements the tool functionality
- Optional parameters and examples

### Creating Tasks

Tasks can be created through the Tasks interface. Each task requires:
- A description
- An optional priority level

Tasks can be executed manually or automatically by the system.

### Querying the Codebase

The DevChat interface allows you to query the codebase with natural language. Example queries:
- "What modules are impacted if I change auth.py?"
- "Show me all functions that write to the database."
- "Where is the function process_query used?"
- "How does the RAG memory system work?"

## Security Considerations

- The Environment Manager securely stores sensitive information like API keys.
- The system uses encryption for storing secrets.
- The MASTER_KEY environment variable should be changed in production.

## Extending the System

The system is designed to be easily extensible:

1. **Adding New Tools**: Create new tools through the Tools interface or by adding them directly to the database.
2. **Enhancing the Knowledge Base**: The system automatically learns from conversations, but you can also manually add knowledge base entries.
3. **Customizing the Frontend**: The frontend is built with React and can be customized by modifying the components.
4. **Adding New API Endpoints**: New API endpoints can be added by extending the routes.py file.

## Troubleshooting

Common issues and their solutions:

1. **API Connection Issues**: Ensure your API_KEY is correctly set in the .env file.
2. **Database Errors**: Check the DATABASE_URI setting and ensure the database file is writable.
3. **Frontend Not Loading**: Make sure you've built the frontend with `npm run build`.
4. **Custom Tools Not Working**: Verify that the tool code is valid Python and follows the required format.

## Conclusion

The AI Agent System provides a powerful, extensible platform for building intelligent applications with memory, learning capabilities, and self-improvement. By leveraging the open-interpreter framework and enhancing it with RAG, database integration, and code intelligence, the system offers a comprehensive solution for a wide range of AI assistant needs.
