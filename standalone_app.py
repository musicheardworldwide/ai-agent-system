"""
Standalone application with configurable port to avoid conflicts
"""
import os
import sys
import logging
from dotenv import load_dotenv
from flask import Flask, send_from_directory, jsonify, request
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime
import requests
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create SQLAlchemy Base
Base = declarative_base()

# Define models directly in this file to avoid import issues
class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    conversation_metadata = Column(Text, nullable=True)  # Renamed from metadata

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    conversation = relationship("Conversation", back_populates="messages")

class KnowledgeItem(Base):
    __tablename__ = 'knowledge_items'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    embedding_id = Column(String(255), nullable=True)
    item_metadata = Column(Text, nullable=True)  # Renamed from metadata

class Tool(Base):
    __tablename__ = 'tools'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    function_code = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    tool_metadata = Column(Text, nullable=True)  # Renamed from metadata

class Environment(Base):
    __tablename__ = 'environments'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=False, unique=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

# Create Flask app
app = Flask(__name__, static_folder='frontend/build', static_url_path='')

# Configure app
app.config.from_mapping(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
    DATABASE_URI=os.environ.get('DATABASE_URI', 'sqlite:///data/ai_agent.db'),
    API_BASE_URL=os.environ.get('API_BASE_URL', 'https://api.lastwinnersllc.com'),
    API_KEY=os.environ.get('API_KEY', ''),
    LLM_MODEL=os.environ.get('LLM_MODEL', 'llama3.2'),
    EMBEDDING_MODEL=os.environ.get('EMBEDDING_MODEL', 'nomic-embed-text'),
    PROJECT_ROOT=os.path.abspath(os.path.dirname(__file__))
)

# Initialize database
engine = create_engine(app.config['DATABASE_URI'])
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db_session = Session()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.close()

# API Routes
@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint that uses the open-interpreter"""
    data = request.json
    
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400
    
    user_message = data['message']
    conversation_id = data.get('conversation_id')
    
    # Log the incoming message
    logger.info(f"Received message: {user_message}")
    
    # Call the API
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {app.config["API_KEY"]}'
        }
        
        api_data = {
            'model': app.config['LLM_MODEL'],
            'messages': [{'role': 'user', 'content': user_message}],
            'temperature': 0.7
        }
        
        response = requests.post(
            f"{app.config['API_BASE_URL']}/v1/chat/completions",
            headers=headers,
            json=api_data
        )
        
        if response.status_code != 200:
            logger.error(f"API error: {response.text}")
            return jsonify({'error': 'Failed to get response from API'}), 500
        
        result = response.json()
        assistant_message = result['choices'][0]['message']['content']
        
        # Store in database
        if conversation_id:
            conversation = db_session.query(Conversation).filter_by(id=conversation_id).first()
        else:
            # Create new conversation
            conversation = Conversation(
                user_id='user',
                title=user_message[:50] + '...' if len(user_message) > 50 else user_message
            )
            db_session.add(conversation)
            db_session.commit()
        
        # Add user message
        user_msg = Message(
            conversation_id=conversation.id,
            role='user',
            content=user_message
        )
        db_session.add(user_msg)
        
        # Add assistant message
        assistant_msg = Message(
            conversation_id=conversation.id,
            role='assistant',
            content=assistant_message
        )
        db_session.add(assistant_msg)
        db_session.commit()
        
        return jsonify({
            'response': assistant_message,
            'conversation_id': conversation.id
        })
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations"""
    try:
        conversations = db_session.query(Conversation).all()
        result = []
        
        for conv in conversations:
            result.append({
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat()
            })
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error getting conversations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get a specific conversation with all messages"""
    try:
        conversation = db_session.query(Conversation).filter_by(id=conversation_id).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        messages = db_session.query(Message).filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()
        
        result = {
            'id': conversation.id,
            'title': conversation.title,
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat(),
            'messages': []
        }
        
        for msg in messages:
            result['messages'].append({
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at.isoformat()
            })
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tools', methods=['GET'])
def get_tools():
    """Get all tools"""
    try:
        tools = db_session.query(Tool).all()
        result = []
        
        for tool in tools:
            result.append({
                'id': tool.id,
                'name': tool.name,
                'description': tool.description,
                'created_at': tool.created_at.isoformat(),
                'updated_at': tool.updated_at.isoformat()
            })
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error getting tools: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tools', methods=['POST'])
def create_tool():
    """Create a new tool"""
    try:
        data = request.json
        
        if not data or 'name' not in data or 'description' not in data or 'function_code' not in data:
            return jsonify({'error': 'Name, description, and function_code are required'}), 400
        
        tool = Tool(
            name=data['name'],
            description=data['description'],
            function_code=data['function_code']
        )
        
        db_session.add(tool)
        db_session.commit()
        
        return jsonify({
            'id': tool.id,
            'name': tool.name,
            'description': tool.description,
            'created_at': tool.created_at.isoformat(),
            'updated_at': tool.updated_at.isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error creating tool: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/environment', methods=['GET'])
def get_environment():
    """Get all environment variables"""
    try:
        env_vars = db_session.query(Environment).all()
        result = []
        
        for env in env_vars:
            result.append({
                'id': env.id,
                'key': env.key,
                'value': '********' if 'key' in env.key.lower() or 'secret' in env.key.lower() or 'password' in env.key.lower() else env.value,
                'description': env.description,
                'created_at': env.created_at.isoformat(),
                'updated_at': env.updated_at.isoformat()
            })
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error getting environment variables: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/environment', methods=['POST'])
def create_environment():
    """Create a new environment variable"""
    try:
        data = request.json
        
        if not data or 'key' not in data or 'value' not in data:
            return jsonify({'error': 'Key and value are required'}), 400
        
        env = Environment(
            key=data['key'],
            value=data['value'],
            description=data.get('description', '')
        )
        
        db_session.add(env)
        db_session.commit()
        
        return jsonify({
            'id': env.id,
            'key': env.key,
            'value': '********' if 'key' in env.key.lower() or 'secret' in env.key.lower() or 'password' in env.key.lower() else env.value,
            'description': env.description,
            'created_at': env.created_at.isoformat(),
            'updated_at': env.updated_at.isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error creating environment variable: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

# Serve frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join('frontend/build', path)):
        return send_from_directory('frontend/build', path)
    else:
        return send_from_directory('frontend/build', 'index.html')

if __name__ == '__main__':
    # Run app
    port = int(os.environ.get('PORT', 8080))  # Changed default port to 8080 to avoid conflicts
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting AI Agent System on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
