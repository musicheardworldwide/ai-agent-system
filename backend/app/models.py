"""
Database models for the AI Agent System
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Conversation(Base):
    """Model for storing conversation history with embeddings"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    embedding = Column(JSON)  # Stores vector embeddings
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'query': self.query,
            'response': self.response,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }

class Tool(Base):
    """Model for storing custom tools"""
    __tablename__ = 'tools'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(Text, nullable=False)
    description = Column(Text)
    parameters = Column(JSON)
    examples = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters,
            'examples': self.examples,
            'created_at': self.created_at.isoformat()
        }

class Task(Base):
    """Model for storing tasks"""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    description = Column(Text, nullable=False)
    status = Column(String(20), default='pending')
    priority = Column(Integer, default=1)
    result = Column(Text)
    context_embedding = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'result': self.result,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class KnowledgeBase(Base):
    """Model for storing knowledge base entries"""
    __tablename__ = 'knowledge_base'
    
    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    source = Column(Text)
    confidence = Column(Integer)
    embedding = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'source': self.source,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat()
        }

class EnvironmentVariable(Base):
    """Model for storing environment variables"""
    __tablename__ = 'environment_variables'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    is_secret = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value if not self.is_secret else '********',
            'is_secret': self.is_secret,
            'created_at': self.created_at.isoformat()
        }

# Initialize database connection
def init_db(app):
    """Initialize database connection and create tables if they don't exist"""
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
