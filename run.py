import os
import sys
import argparse
from dotenv import load_dotenv
from flask import Flask, send_from_directory
from backend.app import init_db
from backend.app.routes import init_app
from backend.app.dev_chat_routes import init_dev_chat

# Load environment variables
load_dotenv()

def create_app():
    """Create and configure the Flask application"""
    # Create Flask app
    app = Flask(__name__, 
                static_folder='frontend/build',
                static_url_path='')
    
    # Configure app
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DATABASE_URI=os.environ.get('DATABASE_URI', 'sqlite:///ai_agent.db'),
        API_BASE_URL=os.environ.get('API_BASE_URL', 'https://api.lastwinnersllc.com'),
        API_KEY=os.environ.get('API_KEY', ''),
        LLM_MODEL=os.environ.get('LLM_MODEL', 'llama3.2'),
        EMBEDDING_MODEL=os.environ.get('EMBEDDING_MODEL', 'nomic-embed-text'),
        PROJECT_ROOT=os.path.abspath(os.path.dirname(__file__))
    )
    
    # Initialize database
    init_db(app)
    
    # Initialize API routes
    init_app(app)
    
    # Initialize DevChat interpreter
    init_dev_chat(app)
    
    # Serve frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
    
    return app

def init_database():
    """Initialize the database"""
    app = create_app()
    with app.app_context():
        from backend.app.models import init_db
        db = init_db(app)
        print("Database initialized successfully")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AI Agent System')
    parser.add_argument('command', nargs='?', default='run',
                        choices=['run', 'init-db'],
                        help='Command to execute (run or init-db)')
    parser.add_argument('--host', default='0.0.0.0',
                        help='Host to run the server on')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to run the server on')
    parser.add_argument('--debug', action='store_true',
                        help='Run in debug mode')
    
    args = parser.parse_args()
    
    if args.command == 'init-db':
        init_database()
    else:
        app = create_app()
        app.run(host=args.host, port=args.port, debug=args.debug)
