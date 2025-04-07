"""
Configuration settings for the AI Agent System
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Configuration class for the application"""
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-development-only')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///ai_agent.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API configuration
    API_BASE_URL = os.environ.get('API_BASE_URL', 'https://api.lastwinnersllc.com')
    LLM_MODEL = os.environ.get('LLM_MODEL', 'llama3.2')
    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'nomic-embed-text')
    API_KEY = os.environ.get('API_KEY', '')
    
    # Vector database configuration
    VECTOR_DB_PATH = os.environ.get('VECTOR_DB_PATH', './chroma_db')
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
