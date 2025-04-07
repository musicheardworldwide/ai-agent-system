"""
Test API routes for the AI Agent System
"""
from flask import Blueprint, jsonify, request, Response, current_app
import time
import json
import threading
import queue
import logging
from datetime import datetime
import traceback

# Create blueprint
tests_api = Blueprint('tests_api', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store test results
test_results = {}

# Store test status
test_status = {
    'chat': 'pending',
    'database': 'pending',
    'rag': 'pending',
    'tools': 'pending',
    'env': 'pending',
    'devchat': 'pending'
}

# Store test logs
test_logs = {
    'chat': [],
    'database': [],
    'rag': [],
    'tools': [],
    'env': [],
    'devchat': []
}

# Queue for streaming logs
log_queues = {
    'chat': queue.Queue(),
    'database': queue.Queue(),
    'rag': queue.Queue(),
    'tools': queue.Queue(),
    'env': queue.Queue(),
    'devchat': queue.Queue()
}

def init_tests_routes(app):
    """Initialize test routes"""
    app.register_blueprint(tests_api, url_prefix='/api/tests')

def add_log(component, level, message):
    """Add a log entry for a component"""
    log_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'level': level,
        'message': message
    }
    test_logs[component].append(log_entry)
    log_queues[component].put(log_entry)

def run_test_in_thread(component, test_func):
    """Run a test in a separate thread"""
    def wrapper():
        try:
            test_status[component] = 'running'
            
            # Clear previous logs
            test_logs[component] = []
            
            # Log test start
            add_log(component, 'info', f'Starting {component} tests')
            
            # Run the test
            start_time = time.time()
            result = test_func()
            duration = int((time.time() - start_time) * 1000)
            
            # Add duration to result
            result['duration'] = duration
            
            # Store the result
            test_results[component] = result
            
            # Update status
            test_status[component] = 'success' if result['success'] else 'failed'
            
            # Log test completion
            status_level = 'success' if result['success'] else 'error'
            add_log(component, status_level, 
                   f"Tests completed: {result['testsPassed']}/{result['testsRun']} passed")
            
        except Exception as e:
            # Log error
            error_msg = f"Error running tests: {str(e)}"
            add_log(component, 'error', error_msg)
            add_log(component, 'error', traceback.format_exc())
            
            # Update status
            test_status[component] = 'failed'
            
            # Store error result
            test_results[component] = {
                'success': False,
                'testsRun': 0,
                'testsPassed': 0,
                'testsFailed': 0,
                'error': str(e),
                'duration': 0
            }
    
    thread = threading.Thread(target=wrapper)
    thread.daemon = True
    thread.start()
    return thread

@tests_api.route('/run/<component>', methods=['POST'])
def run_test(component):
    """Run tests for a specific component"""
    if component not in ['chat', 'database', 'rag', 'tools', 'env', 'devchat', 'all']:
        return jsonify({'error': 'Invalid component'}), 400
    
    if component == 'all':
        return run_all_tests()
    
    # Get the test function for the component
    test_func = get_test_function(component)
    
    # Run the test in a separate thread
    run_test_in_thread(component, test_func)
    
    return jsonify({'status': 'started', 'component': component})

@tests_api.route('/run/all', methods=['POST'])
def run_all_tests():
    """Run all tests"""
    components = ['chat', 'database', 'rag', 'tools', 'env', 'devchat']
    
    for component in components:
        # Get the test function for the component
        test_func = get_test_function(component)
        
        # Run the test in a separate thread
        run_test_in_thread(component, test_func)
    
    return jsonify({'status': 'started', 'components': components})

@tests_api.route('/status/<component>')
def get_test_status(component):
    """Get the status of a test"""
    if component not in ['chat', 'database', 'rag', 'tools', 'env', 'devchat', 'all']:
        return jsonify({'error': 'Invalid component'}), 400
    
    if component == 'all':
        # Check if all tests are completed
        all_completed = all(status != 'running' for status in test_status.values())
        
        return jsonify({
            'statuses': test_status,
            'allCompleted': all_completed
        })
    
    return jsonify({'status': test_status[component]})

@tests_api.route('/results/<component>')
def get_test_results(component):
    """Get the results of a test"""
    if component not in ['chat', 'database', 'rag', 'tools', 'env', 'devchat']:
        return jsonify({'error': 'Invalid component'}), 400
    
    if component not in test_results:
        return jsonify({'error': 'No results available'}), 404
    
    return jsonify(test_results[component])

@tests_api.route('/results')
def get_all_test_results():
    """Get all test results"""
    return jsonify({'results': test_results})

@tests_api.route('/logs/<component>')
def stream_logs(component):
    """Stream logs for a component"""
    if component not in ['chat', 'database', 'rag', 'tools', 'env', 'devchat']:
        return jsonify({'error': 'Invalid component'}), 400
    
    def generate():
        # First, send any existing logs
        for log in test_logs[component]:
            yield f"data: {json.dumps(log)}\n\n"
        
        # Then, stream new logs as they come in
        while True:
            try:
                # Get log from queue with timeout
                log = log_queues[component].get(timeout=1)
                yield f"data: {json.dumps(log)}\n\n"
            except queue.Empty:
                # Send a heartbeat to keep the connection alive
                yield f"data: {json.dumps({'heartbeat': True})}\n\n"
            
            # Check if test is completed
            if test_status[component] not in ['running', 'pending']:
                break
    
    return Response(generate(), mimetype='text/event-stream')

def get_test_function(component):
    """Get the test function for a component"""
    if component == 'chat':
        return test_chat_agent
    elif component == 'database':
        return test_database_agent
    elif component == 'rag':
        return test_rag_memory
    elif component == 'tools':
        return test_custom_tools
    elif component == 'env':
        return test_environment_manager
    elif component == 'devchat':
        return test_devchat_interpreter
    else:
        raise ValueError(f"Unknown component: {component}")

def test_chat_agent():
    """Test the Chat Agent"""
    from .interpreter_system import InterpreterSystem
    
    add_log('chat', 'info', 'Initializing Chat Agent test')
    
    # Initialize test results
    results = {
        'success': True,
        'testsRun': 0,
        'testsPassed': 0,
        'testsFailed': 0,
        'details': []
    }
    
    try:
        # Initialize interpreter system
        interpreter = InterpreterSystem()
        add_log('chat', 'info', 'Chat Agent initialized successfully')
        
        # Test 1: Basic response
        add_log('chat', 'info', 'Testing basic response')
        results['testsRun'] += 1
        
        response = interpreter.process_query("Hello, how are you?")
        
        if response and isinstance(response, str) and len(response) > 0:
            results['testsPassed'] += 1
            add_log('chat', 'success', 'Basic response test passed')
            results['details'].append({
                'name': 'Basic response',
                'success': True
            })
        else:
            results['testsFailed'] += 1
            results['success'] = False
            add_log('chat', 'error', 'Basic response test failed')
            results['details'].append({
                'name': 'Basic response',
                'success': False,
                'error': 'No valid response received'
            })
        
        # Test 2: Code execution
        add_log('chat', 'info', 'Testing code execution')
        results['testsRun'] += 1
        
        code_query = "Calculate the sum of numbers from 1 to 10 using Python"
        response = interpreter.process_query(code_query)
        
        if response and "55" in response:
            results['testsPassed'] += 1
            add_log('chat', 'success', 'Code execution test passed')
            results['details'].append({
                'name': 'Code execution',
                'success': True
            })
        else:
            results['testsFailed'] += 1
            results['success'] = False
            add_log('chat', 'error', 'Code execution test failed')
            results['details'].append({
                'name': 'Code execution',
                'success': False,
                'error': 'Expected result not found in response'
            })
        
        # Test 3: Memory retention
        add_log('chat', 'info', 'Testing memory retention')
        results['testsRun'] += 1
        
        # First message to remember
        interpreter.process_query("My name is Tester")
        
        # Second message to check memory
        response = interpreter.process_query("What is my name?")
        
        if response and "Tester" in response:
            results['testsPassed'] += 1
            add_log('chat', 'success', 'Memory retention test passed')
            results['details'].append({
                'name': 'Memory retention',
                'success': True
            })
        else:
            results['testsFailed'] += 1
            results['success'] = False
            add_log('chat', 'error', 'Memory retention test failed')
            results['details'].append({
                'name': 'Memory retention',
                'success': False,
                'error': 'Memory information not retained'
            })
        
    except Exception as e:
        results['success'] = False
        add_log('chat', 'error', f'Error during Chat Agent test: {str(e)}')
        add_log('chat', 'error', traceback.format_exc())
    
    return results

def test_database_agent():
    """Test the Database Agent"""
    from .database_agent import DatabaseAgent
    
    add_log('database', 'info', 'Initializing Database Agent test')
    
    # Initialize test results
    results = {
        'success': True,
        'testsRun': 0,
        'testsPassed': 0,
        'testsFailed': 0,
        'details': []
    }
    
    try:
        # Initialize database agent
        db_agent = DatabaseAgent()
        add_log('database', 'info', 'Database Agent initialized successfully')
        
        # Test 1: Add knowledge
        add_log('database', 'info', 'Testing knowledge addition')
        results['testsRun'] += 1
        
        test_content = "The capital of France is Paris"
        result = db_agent.add_knowledge("geography", test_content)
        
        if result and result.get('success'):
            results['testsPassed'] += 1
            add_log('database', 'success', 'Knowledge addition test passed')
            results['details'].append({
                'name': 'Knowledge addition',
                'success': True
            })
            
            # Store the entry ID for later tests
            entry_id = result.get('entry_id')
        else:
            results['testsFailed'] += 1
            results['success'] = False
            add_log('database', 'error', 'Knowledge addition test failed')
            results['details'].append({
                'name': 'Knowledge addition',
                'success': False,
                'error': 'Failed to add knowledge'
            })
            entry_id = None
        
        # Test 2: Query knowledge
        if entry_id:
            add_log('database', 'info', 'Testing knowledge query')
            results['testsRun'] += 1
            
            query_result = db_agent.query_knowledge("capital of France")
            
            if query_result and "Paris" in str(query_result):
                results['testsPassed'] += 1
                add_log('database', 'success', 'Knowledge query test passed')
                results['details'].append({
                    'name': 'Knowledge query',
                    'success': True
                })
            else:
                results['testsFailed'] += 1
                results['success'] = False
                add_log('database', 'error', 'Knowledge query test failed')
                results['details'].append({
                    'name': 'Knowledge query',
                    'success': False,
                    'error': 'Expected result not found in query response'
                })
            
            # Test 3: Update knowledge
            add_log('database', 'info', 'Testing knowledge update')
            results['testsRun'] += 1
            
            update_content = "The capital of France is Paris, and the language is French"
            update_result = db_agent.update_knowledge(entry_id, update_content)
            
            if update_result and update_result.get('success'):
                results['testsPassed'] += 1
                add_log('database', 'success', 'Knowledge update test passed')
                results['details'].append({
                    'name': 'Knowledge update',
                    'success': True
                })
                
                # Test 4: Delete knowledge
                add_log('database', 'info', 'Testing knowledge deletion')
                results['testsRun'] += 1
                
                delete_result = db_agent.delete_knowledge(entry_id)
                
                if delete_result and delete_result.get('success'):
                    results['testsPassed'] += 1
                    add_log('database', 'success', 'Knowledge deletion test passed')
                    results['details'].append({
                        'name': 'Knowledge deletion',
                        'success': True
                    })
                else:
                    results['testsFailed'] += 1
                    results['success'] = False
                    add_log('database', 'error', 'Knowledge deletion test failed')
                    results['details'].append({
                        'name': 'Knowledge deletion',
                        'success': False,
                        'error': 'Failed to delete knowledge'
                    })
            else:
                results['testsFailed'] += 1
                results['success'] = False
                add_log('database', 'error', 'Knowledge update test failed')
                results['details'].append({
                    'name': 'Knowledge update',
                    'success': False,
                    'error': 'Failed to update knowledge'
                })
        
    except Exception as e:
        results['success'] = False
        add_log('database', 'error', f'Error during Database Agent test: {str(e)}')
        add_log('database', 'error', traceback.format_exc())
    
    return results

def test_rag_memory():
    """Test the RAG Memory System"""
    from .rag import RAGMemory
    
    add_log('rag', 'info', 'Initializing RAG Memory test')
    
    # Initialize test results
    results = {
        'success': True,
        'testsRun': 0,
        'testsPassed': 0,
        'testsFailed': 0,
        'details': []
    }
    
    try:
        # Initialize RAG memory
        rag_memory = RAGMemory()
        add_log('rag', 'info', 'RAG Memory initialized successfully')
        
        # Test 1: Add memory
        add_log('rag', 'info', 'Testing memory addition')
        results['testsRun'] += 1
        
        test_content = "The user's favorite color is blue"
        result = rag_memory.add_memory(test_content)
        
        if result and result.get('success'):
            results['testsPassed'] += 1
            add_log('rag', 'success', 'Memory addition test passed')
            results['details'].append({
                'name': 'Memory addition',
                'success': True
            })
        else:
            results['testsFailed'] += 1
            results['success'] = False
            add_log('rag', 'error', 'Memory addition test failed')
            results['details'].append({
                'name': 'Memory addition',
                'success': False,
                'error': 'Failed to add memory'
            })
        
        # Test 2: Retrieve memory
        add_log('rag', 'info', 'Testing memory retrieval')
        results['testsRun'] += 1
        
        query = "What is the user's favorite color?"
        retrieved_memories = rag_memory.retrieve_relevant_memories(query)
        
        if retrieved_memories and any("blue" in str(memory) for memory in retrieved_memories):
            results['testsPassed'] += 1
            add_log('rag', 'success', 'Memory retrieval test passed')
            results['details'].append({
                'name': 'Memory retrieval',
                'success': True
            })
        else:
            results['testsFailed'] += 1
            results['success'] = False
            add_log('rag', 'error', 'Memory retrieval test failed')
            results['details'].append({
                'name': 'Memory retrieval',
                'success': False,
                'error': 'Expected memory not found in retrieved memories'
            })
        
        # Test 3: Generate context
        add_log('rag', 'info', 'Testing context generation')
        results['testsRun'] += 1
        
        context = rag_memory.generate_context(query)
        
        if context and "blue" in context:
            results['testsPassed'] += 1
            add_log('rag', 'success', 'Context generation test passed')
            results['details'].append({
                'name': 'Context generation',
                'success': True
            })
        else:
            results['testsFailed'] += 1
            results['success'] = False
            add_log('rag', 'error', 'Context generation test failed')
            results['details'].append({
                'name': 'Context generation',
                'success': False,
                'error': 'Expected information not found in generated context'
            })
        
    except Exception as e:
        results['success'] = False
        add_log('rag', 'error', f'Error during RAG Memory test: {str(e)}')
        add_log('rag', 'error', traceback.format_exc())
    
    return results

def test_custom_tools():
    """Test the Custom Tools System"""
    from .tools import ToolManager
    
    add_log('tools', 'info', 'Initializing Custom Tools test')
    
    # Initialize test results
    results = {
        'success': True,
        'testsRun': 0,
        'testsPassed': 0,
        'testsFailed': 0,
        'details': []
    }
    
    try:
        # Initialize tool manager
        tool_manager = ToolManager()
        add_log('tools', 'info', 'Tool Manager initialized successfully')
        
        # Test 1: Register tool
        add_log('tools', 'info', 'Testing tool registration')
        results['testsRun'] += 1
        
        test_tool = {
            'name': 'calculator',
            'description': 'Perform basic arithmetic operations',
            'code': 'def calculator(a, b, operation):\n    if operation == "add":\n        return a + b\n    elif operation == "subtract":\n        return a - b\n    elif operation == "multiply":\n        return a * b\n    elif operation == "divide":\n        if b == 0:\n            return "Error: Division by zero"\n        return a / b\n    else:\n        return "Error: Invalid operation"',
            'parameters': {
                'a': {'type': 'number', 'description': 'First number'},
                'b': {'type': 'number', 'description': 'Second number'},
                'operation': {'type': 'string', 'description': 'Operation to perform', 'enum': ['add', 'subtract', 'multiply', 'divide']}
            }
        }
        
        result = tool_manager.register_tool(test_tool)
        
        if result and result.get('success'):
            results['testsPassed'] += 1
            add_log('tools', 'success', 'Tool registration test passed')
            results['details'].append({
                'name': 'Tool registration',
                'success': True
            })
            
            # Store the tool ID for later tests
            tool_id = result.get('tool_id')
        else:
            results['testsFailed'] += 1
            results['success'] = False
            add_log('tools', 'error', 'Tool registration test failed')
            results['details'].append({
                'name': 'Tool registration',
                'success': False,
                'error': 'Failed to register tool'
            })
            tool_id = None
        
        # Test 2: Execute tool
        if tool_id:
            add_log('tools', 'info', 'Testing tool execution')
            results['testsRun'] += 1
            
            params = {'a': 5, 'b': 3, 'operation': 'add'}
            execution_result = tool_manager.execute_tool('calculator', params)
            
            if execution_result and execution_result.get('result') == 8:
                results['testsPassed'] += 1
                add_log('tools', 'success', 'Tool execution test passed')
                results['details'].append({
                    'name': 'Tool execution',
                    'success': True
                })
            else:
                results['testsFailed'] += 1
                results['success'] = False
                add_log('tools', 'error', 'Tool execution test failed')
                results['details'].append({
                    'name': 'Tool execution',
                    'success': False,
                    'error': 'Unexpected execution result'
                })
            
            # Test 3: Get tool
            add_log('tools', 'info', 'Testing tool retrieval')
            results['testsRun'] += 1
            
            get_result = tool_manager.get_tool('calculator')
            
            if get_result and get_result.get('name') == 'calculator':
                results['testsPassed'] += 1
                add_log('tools', 'success', 'Tool retrieval test passed')
                results['details'].append({
                    'name': 'Tool retrieval',
                    'success': True
                })
            else:
                results['testsFailed'] += 1
                results['success'] = False
                add_log('tools', 'error', 'Tool retrieval test failed')
                results['details'].append({
                    'name': 'Tool retrieval',
                    'success': False,
                    'error': 'Failed to retrieve tool'
                })
            
            # Test 4: Delete tool
            add_log('tools', 'info', 'Testing tool deletion')
            results['testsRun'] += 1
            
            delete_result = tool_manager.delete_tool('calculator')
            
            if delete_result and delete_result.get('success'):
                results['testsPassed'] += 1
                add_log('tools', 'success', 'Tool deletion test passed')
                results['details'].append({
                    'name': 'Tool deletion',
                    'success': True
                })
            else:
                results['testsFailed'] += 1
                results['success'] = False
                add_log('tools', 'error', 'Tool deletion test failed')
                results['details'].append({
                    'name': 'Tool deletion',
                    'success': False,
                    'error': 'Failed to delete tool'
                })
        
    except Exception as e:
        results['success'] = False
        add_log('tools', 'error', f'Error during Custom Tools test: {str(e)}')
        add_log('tools', 'error', traceback.format_exc())
    
    return results

def test_environment_manager():
    """Test the Environment Manager"""
    from .env_manager import EnvironmentManager
    
    add_log('env', 'info', 'Initializing Environment Manager test')
    
    # Initialize test results
    results = {
        'success': True,
        'testsRun': 0,
        'testsPassed': 0,
        'testsFailed': 0,
        'details': []
    }
    
    try:
        # Initialize environment manager
        env_manager = EnvironmentManager()
        add_log('env', 'info', 'Environment Manager initialized successfully')
        
        # Test 1: Set variable
        add_log('env', 'info', 'Testing variable setting')
        results['testsRun'] += 1
        
        test_key = 'TEST_VAR'
        test_value = 'test_value_123'
        result = env_manager.set_variable(test_key, test_value)
        
        if result and result.get('success'):
            results['testsPassed'] += 1
            add_log('env', 'success', 'Variable setting test passed')
            results['details'].append({
                'name': 'Variable setting',
                'success': True
            })
        else:
            results['testsFailed'] += 1
            results['success'] = False
            add_log('env', 'error', 'Variable setting test failed')
            results['details'].append({
                'name': 'Variable setting',
                'success': False,
                'error': 'Failed to set variable'
            })
        
        # Test 2: Get variable
        add_log('env', 'info', 'Testing variable retrieval')
        results['testsRun'] += 1
        
        get_result = env_manager.get_variable(test_key)
        
        if get_result and get_result.get('value') == test_value:
            results['testsPassed'] += 1
            add_log('env', 'success', 'Variable retrieval test passed')
            results['details'].append({
                'name': 'Variable retrieval',
                'success': True
            })
        else:
            results['testsFailed'] += 1
            results['success'] = False
            add_log('env', 'error', 'Variable retrieval test failed')
            results['details'].append({
                'name': 'Variable retrieval',
                'success': False,
                'error': 'Retrieved value does not match expected value'
            })
        
        # Test 3: Update variable
        add_log('env', 'info', 'Testing variable update')
        results['testsRun'] += 1
        
        updated_value = 'updated_value_456'
        update_result = env_manager.set_variable(test_key, updated_value)
        
        if update_result and update_result.get('success'):
            # Verify the update
            verify_result = env_manager.get_variable(test_key)
            
            if verify_result and verify_result.get('value') == updated_value:
                results['testsPassed'] += 1
                add_log('env', 'success', 'Variable update test passed')
                results['details'].append({
                    'name': 'Variable update',
                    'success': True
                })
            else:
                results['testsFailed'] += 1
                results['success'] = False
                add_log('env', 'error', 'Variable update verification failed')
                results['details'].append({
                    'name': 'Variable update',
                    'success': False,
                    'error': 'Updated value not correctly stored'
                })
        else:
            results['testsFailed'] += 1
            results['success'] = False
            add_log('env', 'error', 'Variable update test failed')
            results['details'].append({
                'name': 'Variable update',
                'success': False,
                'error': 'Failed to update variable'
            })
        
        # Test 4: Delete variable
        add_log('env', 'info', 'Testing variable deletion')
        results['testsRun'] += 1
        
        delete_result = env_manager.delete_variable(test_key)
        
        if delete_result and delete_result.get('success'):
            # Verify the deletion
            verify_result = env_manager.get_variable(test_key)
            
            if verify_result and verify_result.get('error'):
                results['testsPassed'] += 1
                add_log('env', 'success', 'Variable deletion test passed')
                results['details'].append({
                    'name': 'Variable deletion',
                    'success': True
                })
            else:
                results['testsFailed'] += 1
                results['success'] = False
                add_log('env', 'error', 'Variable deletion verification failed')
                results['details'].append({
                    'name': 'Variable deletion',
                    'success': False,
                    'error': 'Variable still exists after deletion'
                })
        else:
            results['testsFailed'] += 1
            results['success'] = False
            add_log('env', 'error', 'Variable deletion test failed')
            results['details'].append({
                'name': 'Variable deletion',
                'success': False,
                'error': 'Failed to delete variable'
            })
        
    except Exception as e:
        results['success'] = False
        add_log('env', 'error', f'Error during Environment Manager test: {str(e)}')
        add_log('env', 'error', traceback.format_exc())
    
    return results

def test_devchat_interpreter():
    """Test the DevChat Interpreter Model"""
    from .dev_chat import DevChatInterpreter
    
    add_log('devchat', 'info', 'Initializing DevChat Interpreter test')
    
    # Initialize test results
    results = {
        'success': True,
        'testsRun': 0,
        'testsPassed': 0,
        'testsFailed': 0,
        'details': []
    }
    
    try:
        # Initialize DevChat interpreter
        dev_chat = DevChatInterpreter()
        add_log('devchat', 'info', 'DevChat Interpreter initialized successfully')
        
        # Test 1: Scan project
        add_log('devchat', 'info', 'Testing project scanning')
        results['testsRun'] += 1
        
        scan_result = dev_chat.scan_project()
        
        if scan_result and scan_result.get('success'):
            results['testsPassed'] += 1
            add_log('devchat', 'success', 'Project scanning test passed')
            results['details'].append({
                'name': 'Project scanning',
                'success': True
            })
        else:
            results['testsFailed'] += 1
            results['success'] = False
            add_log('devchat', 'error', 'Project scanning test failed')
            results['details'].append({
                'name': 'Project scanning',
                'success': False,
                'error': 'Failed to scan project'
            })
        
        # Test 2: Query code structure
        add_log('devchat', 'info', 'Testing code structure query')
        results['testsRun'] += 1
        
        query = "What files are in the project?"
        query_result = dev_chat.query(query)
        
        if query_result and query_result.get('response'):
            results['testsPassed'] += 1
            add_log('devchat', 'success', 'Code structure query test passed')
            results['details'].append({
                'name': 'Code structure query',
                'success': True
            })
        else:
            results['testsFailed'] += 1
            results['success'] = False
            add_log('devchat', 'error', 'Code structure query test failed')
            results['details'].append({
                'name': 'Code structure query',
                'success': False,
                'error': 'Failed to query code structure'
            })
        
        # Test 3: Impact analysis
        add_log('devchat', 'info', 'Testing impact analysis')
        results['testsRun'] += 1
        
        impact_query = "What would be affected if I change the InterpreterSystem class?"
        impact_result = dev_chat.query(impact_query)
        
        if impact_result and impact_result.get('response'):
            results['testsPassed'] += 1
            add_log('devchat', 'success', 'Impact analysis test passed')
            results['details'].append({
                'name': 'Impact analysis',
                'success': True
            })
        else:
            results['testsFailed'] += 1
            results['success'] = False
            add_log('devchat', 'error', 'Impact analysis test failed')
            results['details'].append({
                'name': 'Impact analysis',
                'success': False,
                'error': 'Failed to perform impact analysis'
            })
        
    except Exception as e:
        results['success'] = False
        add_log('devchat', 'error', f'Error during DevChat Interpreter test: {str(e)}')
        add_log('devchat', 'error', traceback.format_exc())
    
    return results
