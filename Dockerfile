FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p data logs

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend code
COPY frontend/ ./frontend/

# Build frontend
WORKDIR /app/frontend
RUN npm install
RUN npm run build

# Back to app directory
WORKDIR /app

# Copy run script and other files
COPY run.py .
COPY app.py .

# Create .env file with default values
RUN echo "API_BASE_URL=https://api.lastwinnersllc.com\n\
API_KEY=test_key\n\
CHAT_MODEL=llama3.2\n\
EMBEDDING_MODEL=nomic-embed-text\n\
DATABASE_URI=sqlite:///data/ai_agent.db\n\
PORT=8080\n\
HOST=0.0.0.0\n\
MASTER_KEY=change-this-in-production" > .env

# Initialize database
RUN python run.py init-db

# Expose port
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py

# Run the application
CMD ["python", "run.py"]
