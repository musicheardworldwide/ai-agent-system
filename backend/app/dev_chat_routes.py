"""
Routes for the DevChat interpreter model
"""
from flask import Blueprint, request, jsonify
from .dev_chat import DevChatInterpreter
import os

# Create blueprint
dev_chat_api = Blueprint('dev_chat_api', __name__)

# Initialize DevChat interpreter
dev_chat = None

def init_dev_chat(app):
    """Initialize the DevChat interpreter"""
    global dev_chat
    
    # Get project root from config or use current directory
    project_root = app.config.get('PROJECT_ROOT', os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    
    # Get API credentials
    api_base_url = app.config.get('API_BASE_URL', 'https://api.lastwinnersllc.com')
    api_key = app.config.get('API_KEY')
    
    # Initialize DevChat interpreter
    dev_chat = DevChatInterpreter(
        project_root=project_root,
        api_base_url=api_base_url,
        api_key=api_key
    )
    
    # Register blueprint
    app.register_blueprint(dev_chat_api, url_prefix='/api/dev-chat')

@dev_chat_api.route('/query', methods=['POST'])
def query():
    """Process a natural language query about the codebase"""
    if not dev_chat:
        return jsonify({"error": "DevChat interpreter not initialized"}), 500
    
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Query is required"}), 400
    
    query_text = data.get('query')
    
    # Process the query
    result = dev_chat.process_query(query_text)
    
    return jsonify(result)

@dev_chat_api.route('/files', methods=['GET'])
def list_files():
    """List all files in the codebase"""
    if not dev_chat:
        return jsonify({"error": "DevChat interpreter not initialized"}), 500
    
    return jsonify({
        "files": list(dev_chat.file_info.keys())
    })

@dev_chat_api.route('/files/<path:file_path>', methods=['GET'])
def get_file_info(file_path):
    """Get information about a specific file"""
    if not dev_chat:
        return jsonify({"error": "DevChat interpreter not initialized"}), 500
    
    file_info = dev_chat.get_file_info(file_path)
    
    if not file_info:
        return jsonify({"error": "File not found"}), 404
    
    return jsonify(file_info)

@dev_chat_api.route('/impact/<path:file_path>', methods=['GET'])
def get_impact_analysis(file_path):
    """Get impact analysis for a specific file"""
    if not dev_chat:
        return jsonify({"error": "DevChat interpreter not initialized"}), 500
    
    impact = dev_chat.get_impact_analysis(file_path)
    
    return jsonify(impact)

@dev_chat_api.route('/database-interactions', methods=['GET'])
def get_database_interactions():
    """Get all functions that interact with the database"""
    if not dev_chat:
        return jsonify({"error": "DevChat interpreter not initialized"}), 500
    
    interactions = dev_chat.get_database_interactions()
    
    return jsonify({
        "database_interactions": interactions
    })

@dev_chat_api.route('/search', methods=['GET'])
def search_code():
    """Search the codebase using semantic search"""
    if not dev_chat:
        return jsonify({"error": "DevChat interpreter not initialized"}), 500
    
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    n_results = int(request.args.get('n', 5))
    
    results = dev_chat.search_code(query, n_results)
    
    return jsonify({
        "query": query,
        "results": results
    })

@dev_chat_api.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics about the codebase"""
    if not dev_chat:
        return jsonify({"error": "DevChat interpreter not initialized"}), 500
    
    stats = dev_chat.get_system_stats()
    
    return jsonify(stats)

@dev_chat_api.route('/map', methods=['GET'])
def get_code_map():
    """Get a visual map of the code"""
    if not dev_chat:
        return jsonify({"error": "DevChat interpreter not initialized"}), 500
    
    map_data = dev_chat.generate_code_map()
    
    return jsonify(map_data)

@dev_chat_api.route('/rescan', methods=['POST'])
def rescan_project():
    """Rescan the entire project"""
    if not dev_chat:
        return jsonify({"error": "DevChat interpreter not initialized"}), 500
    
    # Stop watching
    dev_chat.stop_watching()
    
    # Scan project
    dev_chat.scan_project()
    
    # Start watching again
    dev_chat.start_watching()
    
    return jsonify({
        "status": "Project rescanned successfully",
        "stats": dev_chat.get_system_stats()
    })
