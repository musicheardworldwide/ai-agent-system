"""
Routes for the AI Agent System
"""
from flask import Blueprint, request, jsonify, Response, stream_with_context
from .models import init_db, Conversation, Tool, Task, KnowledgeBase, EnvironmentVariable
from .interpreter_system import InterpreterSystem
from .rag import RAGMemorySystem
import json
from datetime import datetime

# Create blueprint
api = Blueprint('api', __name__)

# Initialize database session
db_session = None

# Initialize systems
interpreter_system = None
rag_system = None

def init_app(app):
    """Initialize the application with routes and systems"""
    global db_session, interpreter_system, rag_system
    
    # Initialize database
    db_session = init_db(app)
    
    # Initialize systems
    rag_system = RAGMemorySystem(app)
    interpreter_system = InterpreterSystem(app, db_session)
    
    # Register blueprint
    app.register_blueprint(api, url_prefix='/api')

@api.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint that processes queries through the interpreter system
    This is the primary interface for the AI Agent System
    """
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Query is required"}), 400
    
    query = data.get('query')
    stream = data.get('stream', False)
    
    if stream:
        # Stream response
        def generate():
            for chunk in interpreter_system.process_chat(query, stream=True):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        
        return Response(stream_with_context(generate()), 
                       mimetype='text/event-stream')
    else:
        # Regular response
        result = interpreter_system.process_chat(query)
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify(result)

@api.route('/tools', methods=['GET', 'POST'])
def tools():
    """Endpoint for managing tools"""
    if request.method == 'POST':
        # Register a new tool
        data = request.json
        required_fields = ['name', 'code', 'description']
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        success, result = interpreter_system.register_tool(
            data['code'], 
            data['name'], 
            data['description'],
            data.get('parameters'),
            data.get('examples')
        )
        
        if not success:
            return jsonify({"error": result}), 400
        
        # Store tool in database
        new_tool = Tool(
            name=data['name'],
            code=data['code'],
            description=data['description'],
            parameters=json.dumps(data.get('parameters', {})),
            examples=json.dumps(data.get('examples', []))
        )
        
        db_session.add(new_tool)
        db_session.commit()
        
        return jsonify({"status": "Tool registered successfully", "tool": result})
    
    else:
        # Get all tools
        tools = db_session.query(Tool).all()
        return jsonify([tool.to_dict() for tool in tools])

@api.route('/tools/<int:tool_id>', methods=['GET', 'PUT', 'DELETE'])
def tool(tool_id):
    """Endpoint for managing a specific tool"""
    tool = db_session.query(Tool).filter_by(id=tool_id).first()
    
    if not tool:
        return jsonify({"error": "Tool not found"}), 404
    
    if request.method == 'GET':
        return jsonify(tool.to_dict())
    
    elif request.method == 'PUT':
        data = request.json
        
        if 'name' in data:
            tool.name = data['name']
        
        if 'code' in data:
            tool.code = data['code']
        
        if 'description' in data:
            tool.description = data['description']
        
        if 'parameters' in data:
            tool.parameters = json.dumps(data['parameters'])
        
        if 'examples' in data:
            tool.examples = json.dumps(data['examples'])
        
        tool.updated_at = datetime.utcnow()
        db_session.commit()
        
        # Re-register tool with interpreter
        interpreter_system.register_tool(
            tool.code,
            tool.name,
            tool.description,
            json.loads(tool.parameters) if tool.parameters else {},
            json.loads(tool.examples) if tool.examples else []
        )
        
        return jsonify({"status": "Tool updated successfully"})
    
    elif request.method == 'DELETE':
        db_session.delete(tool)
        db_session.commit()
        
        # Reset interpreter to remove the tool
        interpreter_system.reset_interpreter()
        
        return jsonify({"status": "Tool deleted successfully"})

@api.route('/tasks', methods=['GET', 'POST'])
def tasks():
    """Endpoint for managing tasks"""
    if request.method == 'POST':
        # Create a new task
        data = request.json
        
        if 'description' not in data:
            return jsonify({"error": "Description is required"}), 400
        
        # Generate embedding
        embedding = rag_system.store_task(
            data['description'],
            data.get('priority', 1)
        )
        
        # Store task in database
        new_task = Task(
            description=data['description'],
            priority=data.get('priority', 1),
            context_embedding=json.dumps(embedding)
        )
        
        db_session.add(new_task)
        db_session.commit()
        
        return jsonify({"status": "Task created successfully", "task_id": new_task.id})
    
    else:
        # Get all tasks
        tasks = db_session.query(Task).all()
        return jsonify([task.to_dict() for task in tasks])

@api.route('/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
def task(task_id):
    """Endpoint for managing a specific task"""
    task = db_session.query(Task).filter_by(id=task_id).first()
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    if request.method == 'GET':
        return jsonify(task.to_dict())
    
    elif request.method == 'PUT':
        data = request.json
        
        if 'description' in data:
            task.description = data['description']
            
            # Update embedding
            embedding = rag_system.store_task(
                data['description'],
                data.get('priority', task.priority)
            )
            task.context_embedding = json.dumps(embedding)
        
        if 'priority' in data:
            task.priority = data['priority']
        
        if 'status' in data:
            task.status = data['status']
            
            if data['status'] == 'completed' and not task.completed_at:
                task.completed_at = datetime.utcnow()
        
        if 'result' in data:
            task.result = data['result']
        
        db_session.commit()
        
        return jsonify({"status": "Task updated successfully"})
    
    elif request.method == 'DELETE':
        db_session.delete(task)
        db_session.commit()
        
        return jsonify({"status": "Task deleted successfully"})

@api.route('/tasks/<int:task_id>/execute', methods=['POST'])
def execute_task(task_id):
    """Endpoint for executing a specific task"""
    task = db_session.query(Task).filter_by(id=task_id).first()
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # Execute task using interpreter
    result = interpreter_system.process_chat(f"Execute the following task: {task.description}")
    
    # Update task
    task.status = 'completed'
    task.completed_at = datetime.utcnow()
    task.result = result.get('response', '')
    
    db_session.commit()
    
    return jsonify({
        "status": "Task executed successfully",
        "result": result
    })

@api.route('/knowledge', methods=['GET', 'POST'])
def knowledge():
    """Endpoint for managing knowledge base entries"""
    if request.method == 'POST':
        # Create a new knowledge base entry
        data = request.json
        required_fields = ['question', 'answer']
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Generate embedding
        embedding = rag_system.store_knowledge(
            data['question'],
            data['answer'],
            data.get('source'),
            data.get('confidence')
        )
        
        # Store in database
        new_entry = KnowledgeBase(
            question=data['question'],
            answer=data['answer'],
            source=data.get('source'),
            confidence=data.get('confidence'),
            embedding=json.dumps(embedding)
        )
        
        db_session.add(new_entry)
        db_session.commit()
        
        return jsonify({"status": "Knowledge base entry created successfully", "entry_id": new_entry.id})
    
    else:
        # Get all knowledge base entries
        entries = db_session.query(KnowledgeBase).all()
        return jsonify([entry.to_dict() for entry in entries])

@api.route('/knowledge/<int:entry_id>', methods=['GET', 'PUT', 'DELETE'])
def knowledge_entry(entry_id):
    """Endpoint for managing a specific knowledge base entry"""
    entry = db_session.query(KnowledgeBase).filter_by(id=entry_id).first()
    
    if not entry:
        return jsonify({"error": "Knowledge base entry not found"}), 404
    
    if request.method == 'GET':
        return jsonify(entry.to_dict())
    
    elif request.method == 'PUT':
        data = request.json
        
        if 'question' in data:
            entry.question = data['question']
        
        if 'answer' in data:
            entry.answer = data['answer']
        
        if 'source' in data:
            entry.source = data['source']
        
        if 'confidence' in data:
            entry.confidence = data['confidence']
        
        # Update embedding if question or answer changed
        if 'question' in data or 'answer' in data:
            embedding = rag_system.store_knowledge(
                entry.question,
                entry.answer,
                entry.source,
                entry.confidence
            )
            entry.embedding = json.dumps(embedding)
        
        db_session.commit()
        
        return jsonify({"status": "Knowledge base entry updated successfully"})
    
    elif request.method == 'DELETE':
        db_session.delete(entry)
        db_session.commit()
        
        return jsonify({"status": "Knowledge base entry deleted successfully"})

@api.route('/env', methods=['GET', 'POST'])
def environment():
    """Endpoint for managing environment variables"""
    if request.method == 'POST':
        # Create or update an environment variable
        data = request.json
        required_fields = ['key', 'value']
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Check if variable exists
        env_var = db_session.query(EnvironmentVariable).filter_by(key=data['key']).first()
        
        if env_var:
            # Update existing variable
            env_var.value = data['value']
            env_var.is_secret = data.get('is_secret', env_var.is_secret)
            env_var.updated_at = datetime.utcnow()
        else:
            # Create new variable
            env_var = EnvironmentVariable(
                key=data['key'],
                value=data['value'],
                is_secret=data.get('is_secret', False)
            )
            db_session.add(env_var)
        
        db_session.commit()
        
        return jsonify({"status": "Environment variable set successfully"})
    
    else:
        # Get all environment variables
        env_vars = db_session.query(EnvironmentVariable).all()
        return jsonify([var.to_dict() for var in env_vars])

@api.route('/env/<string:key>', methods=['GET', 'DELETE'])
def environment_variable(key):
    """Endpoint for managing a specific environment variable"""
    env_var = db_session.query(EnvironmentVariable).filter_by(key=key).first()
    
    if not env_var:
        return jsonify({"error": "Environment variable not found"}), 404
    
    if request.method == 'GET':
        return jsonify(env_var.to_dict())
    
    elif request.method == 'DELETE':
        db_session.delete(env_var)
        db_session.commit()
        
        return jsonify({"status": "Environment variable deleted successfully"})

@api.route('/conversations', methods=['GET'])
def conversations():
    """Endpoint for retrieving conversation history"""
    conversations = db_session.query(Conversation).order_by(Conversation.created_at.desc()).all()
    return jsonify([conv.to_dict() for conv in conversations])

@api.route('/system/reset', methods=['POST'])
def reset_system():
    """Endpoint for resetting the interpreter system"""
    interpreter_system.reset_interpreter()
    return jsonify({"status": "System reset successfully"})

@api.route('/system/status', methods=['GET'])
def system_status():
    """Endpoint for checking system status"""
    return jsonify({
        "status": "online",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "interpreter": "active",
            "rag": "active",
            "database": "connected"
        }
    })
