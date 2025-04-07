"""
Settings API routes for the AI Agent System
"""
from flask import Blueprint, request, jsonify, current_app
import os
from dotenv import load_dotenv, set_key
import json
from .env_manager import EnvironmentManager

# Create blueprint
settings_api = Blueprint('settings_api', __name__)

# Initialize environment manager
env_manager = EnvironmentManager()

def init_settings_routes(app):
    """Initialize settings routes"""
    app.register_blueprint(settings_api, url_prefix='/api/settings')

@settings_api.route('/general', methods=['GET'])
def get_general_settings():
    """Get general settings"""
    settings = {
        'apiBaseUrl': os.environ.get('API_BASE_URL', 'https://api.lastwinnersllc.com'),
        'llmModel': os.environ.get('LLM_MODEL', 'llama3.2'),
        'embeddingModel': os.environ.get('EMBEDDING_MODEL', 'nomic-embed-text'),
        'debugMode': os.environ.get('DEBUG', 'False').lower() == 'true'
    }
    
    return jsonify(settings)

@settings_api.route('/general', methods=['POST'])
def update_general_settings():
    """Update general settings"""
    data = request.json
    
    # Update environment variables
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    
    # Ensure .env file exists
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write("# AI Agent System Environment Variables\n")
    
    # Update values
    if 'apiBaseUrl' in data:
        set_key(env_file, 'API_BASE_URL', data['apiBaseUrl'])
    
    if 'llmModel' in data:
        set_key(env_file, 'LLM_MODEL', data['llmModel'])
    
    if 'embeddingModel' in data:
        set_key(env_file, 'EMBEDDING_MODEL', data['embeddingModel'])
    
    if 'debugMode' in data:
        set_key(env_file, 'DEBUG', str(data['debugMode']))
    
    # Reload environment variables
    load_dotenv(env_file, override=True)
    
    # Update app config
    current_app.config['API_BASE_URL'] = os.environ.get('API_BASE_URL')
    current_app.config['LLM_MODEL'] = os.environ.get('LLM_MODEL')
    current_app.config['EMBEDDING_MODEL'] = os.environ.get('EMBEDDING_MODEL')
    
    return jsonify({'status': 'success', 'message': 'General settings updated successfully'})

@settings_api.route('/security', methods=['GET'])
def get_security_settings():
    """Get security settings (masked)"""
    # For security, we don't return actual values, just masked placeholders if set
    settings = {
        'apiKey': mask_value(os.environ.get('API_KEY', '')),
        'masterKey': mask_value(os.environ.get('MASTER_KEY', '')),
        'secretKey': mask_value(os.environ.get('SECRET_KEY', ''))
    }
    
    return jsonify(settings)

@settings_api.route('/security', methods=['POST'])
def update_security_settings():
    """Update security settings"""
    data = request.json
    
    # Update environment variables
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    
    # Ensure .env file exists
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write("# AI Agent System Environment Variables\n")
    
    # Only update if not masked (i.e., user has entered a new value)
    if 'apiKey' in data and not is_masked(data['apiKey']):
        set_key(env_file, 'API_KEY', data['apiKey'])
    
    if 'masterKey' in data and not is_masked(data['masterKey']):
        set_key(env_file, 'MASTER_KEY', data['masterKey'])
    
    if 'secretKey' in data and not is_masked(data['secretKey']):
        set_key(env_file, 'SECRET_KEY', data['secretKey'])
    
    # Reload environment variables
    load_dotenv(env_file, override=True)
    
    # Update app config
    if 'apiKey' in data and not is_masked(data['apiKey']):
        current_app.config['API_KEY'] = os.environ.get('API_KEY')
    
    if 'secretKey' in data and not is_masked(data['secretKey']):
        current_app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    
    return jsonify({'status': 'success', 'message': 'Security settings updated successfully'})

@settings_api.route('/database', methods=['GET'])
def get_database_settings():
    """Get database settings"""
    settings = {
        'databaseUri': os.environ.get('DATABASE_URI', 'sqlite:///ai_agent.db'),
        'autoBackup': os.environ.get('AUTO_BACKUP', 'False').lower() == 'true',
        'backupInterval': int(os.environ.get('BACKUP_INTERVAL', '24'))
    }
    
    return jsonify(settings)

@settings_api.route('/database', methods=['POST'])
def update_database_settings():
    """Update database settings"""
    data = request.json
    
    # Update environment variables
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    
    # Ensure .env file exists
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write("# AI Agent System Environment Variables\n")
    
    # Update values
    if 'databaseUri' in data:
        set_key(env_file, 'DATABASE_URI', data['databaseUri'])
    
    if 'autoBackup' in data:
        set_key(env_file, 'AUTO_BACKUP', str(data['autoBackup']))
    
    if 'backupInterval' in data:
        set_key(env_file, 'BACKUP_INTERVAL', str(data['backupInterval']))
    
    # Reload environment variables
    load_dotenv(env_file, override=True)
    
    # Update app config
    if 'databaseUri' in data:
        current_app.config['DATABASE_URI'] = os.environ.get('DATABASE_URI')
    
    return jsonify({'status': 'success', 'message': 'Database settings updated successfully'})

@settings_api.route('/ui', methods=['GET'])
def get_ui_settings():
    """Get UI settings"""
    # Try to load from file first
    ui_settings_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ui_settings.json')
    
    if os.path.exists(ui_settings_file):
        try:
            with open(ui_settings_file, 'r') as f:
                settings = json.load(f)
                return jsonify(settings)
        except Exception as e:
            print(f"Error loading UI settings: {e}")
    
    # Default settings
    settings = {
        'theme': 'light',
        'codeTheme': 'vs-dark',
        'fontSize': 14,
        'showMetadata': True
    }
    
    return jsonify(settings)

@settings_api.route('/ui', methods=['POST'])
def update_ui_settings():
    """Update UI settings"""
    data = request.json
    
    # Save to file
    ui_settings_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ui_settings.json')
    
    try:
        with open(ui_settings_file, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to save UI settings: {str(e)}'}), 500
    
    return jsonify({'status': 'success', 'message': 'UI settings updated successfully'})

def mask_value(value):
    """Mask a value for security"""
    if not value:
        return ''
    
    # Show first and last character, mask the rest
    if len(value) <= 2:
        return '*' * len(value)
    
    return value[0] + '*' * (len(value) - 2) + value[-1]

def is_masked(value):
    """Check if a value is masked"""
    if not value:
        return False
    
    # Check if the value contains only the first and last character with asterisks in between
    return '*' in value and (len(value) <= 2 or (value[1:-1].count('*') == len(value) - 2))
