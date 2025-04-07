"""
Core interpreter system for the AI Agent System
"""
import json
import requests
from interpreter import interpreter
from .config import Config
from .rag import RAGMemorySystem

class InterpreterSystem:
    """
    Core interpreter system that integrates open-interpreter with
    the RAG memory system and custom tools.
    """
    
    def __init__(self, app=None, db_session=None):
        """Initialize the interpreter system"""
        self.app = app
        self.db_session = db_session
        self.api_base_url = Config.API_BASE_URL
        self.api_key = Config.API_KEY
        self.llm_model = Config.LLM_MODEL
        
        # Initialize RAG memory system
        self.rag = RAGMemorySystem(app)
        
        # Configure open-interpreter
        self._configure_interpreter()
    
    def _configure_interpreter(self):
        """Configure open-interpreter with the specified settings"""
        # Set up the LLM configuration
        interpreter.llm.api_base = self.api_base_url
        interpreter.llm.model = self.llm_model
        
        if self.api_key:
            interpreter.llm.api_key = self.api_key
        
        # Set interpreter to auto-run code
        interpreter.auto_run = True
        
        # Set system message to make the model aware of its capabilities
        interpreter.system_message = """
        You are an advanced AI assistant with access to a powerful interpreter system.
        You can execute code, use tools, and access a memory system with RAG capabilities.
        
        Your capabilities include:
        1. Running Python code to solve problems
        2. Using custom tools that have been registered with the system
        3. Accessing and updating a knowledge base
        4. Creating and managing tasks
        5. Using RAG to retrieve relevant context for queries
        
        When responding to user queries:
        - Use the most appropriate approach to solve the problem
        - Leverage your code execution capabilities when needed
        - Access relevant context from the memory system
        - Create and use custom tools as needed
        - Maintain a conversational and helpful tone
        
        You should always strive to provide the most accurate and helpful responses.
        """
    
    def register_tool(self, tool_code, tool_name, tool_description, parameters=None, examples=None):
        """Register a new tool with the interpreter"""
        try:
            # Execute the tool code to register it
            interpreter.computer.run("python", tool_code)
            
            # Store tool information for future reference
            if parameters is None:
                parameters = {}
            
            if examples is None:
                examples = []
            
            tool_info = {
                "name": tool_name,
                "description": tool_description,
                "parameters": parameters,
                "examples": examples
            }
            
            return True, tool_info
        except Exception as e:
            return False, str(e)
    
    def process_chat(self, query, stream=False):
        """
        Process a chat query using the interpreter with RAG enhancement
        """
        try:
            # Augment query with relevant context
            augmented_query = self.rag.augment_query(query)
            
            # Get response from interpreter
            if stream:
                # For streaming response
                response_chunks = []
                for chunk in interpreter.chat(augmented_query, stream=True, display=False):
                    if isinstance(chunk, dict):
                        if chunk.get("type") == "message":
                            response_chunks.append(chunk.get("content", ""))
                            yield chunk.get("content", "")
                    elif isinstance(chunk, str):
                        response_chunks.append(chunk)
                        yield chunk
                
                # Store conversation after streaming is complete
                full_response = "".join(response_chunks)
                embedding = self.rag.store_conversation(query, full_response)
                
                # Return None to indicate streaming is complete
                return None
            else:
                # For non-streaming response
                response = interpreter.chat(augmented_query, stream=False, display=False)
                
                # Extract response text
                if isinstance(response, list):
                    response_text = "\n".join([msg.get("content", "") for msg in response if msg.get("role") == "assistant"])
                else:
                    response_text = str(response)
                
                # Store conversation
                embedding = self.rag.store_conversation(query, response_text)
                
                return {
                    "response": response_text,
                    "augmented_query": augmented_query
                }
        
        except Exception as e:
            error_message = f"Error processing chat: {str(e)}"
            return {"error": error_message}
    
    def execute_code(self, code, language="python"):
        """Execute code using the interpreter"""
        try:
            result = interpreter.computer.run(language, code)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}
    
    def reset_interpreter(self):
        """Reset the interpreter to its initial state"""
        interpreter.reset()
        self._configure_interpreter()
        return {"status": "Interpreter reset successfully"}
