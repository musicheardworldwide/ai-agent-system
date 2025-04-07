"""
Custom tools functionality for the AI Agent System
"""
import json
import importlib
import inspect
import re
from .models import Tool

class ToolManager:
    """
    Tool manager that handles custom tool registration, validation, and execution.
    This component allows the system to dynamically add and use custom tools.
    """
    
    def __init__(self, db_session=None, interpreter_system=None):
        """Initialize the tool manager"""
        self.db_session = db_session
        self.interpreter_system = interpreter_system
        self.registered_tools = {}
        self.load_tools_from_db()
    
    def load_tools_from_db(self):
        """Load tools from the database"""
        if not self.db_session:
            return
        
        tools = self.db_session.query(Tool).all()
        for tool in tools:
            self.registered_tools[tool.name] = {
                "id": tool.id,
                "code": tool.code,
                "description": tool.description,
                "parameters": json.loads(tool.parameters) if tool.parameters else {},
                "examples": json.loads(tool.examples) if tool.examples else []
            }
    
    def validate_tool_code(self, code):
        """
        Validate tool code for security and correctness
        
        Args:
            code (str): Tool code to validate
            
        Returns:
            tuple: (is_valid, message)
        """
        # Check for potentially dangerous imports
        dangerous_imports = [
            "subprocess", "os.system", "eval", "exec", 
            "__import__", "importlib.import_module", "pty", 
            "popen", "call", "Popen"
        ]
        
        for imp in dangerous_imports:
            if re.search(r'[^a-zA-Z0-9_]' + re.escape(imp) + r'[^a-zA-Z0-9_]', ' ' + code + ' '):
                return False, f"Potentially dangerous import or function: {imp}"
        
        # Check for proper function definition
        if not re.search(r'def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(', code):
            return False, "No function definition found"
        
        # Check for docstring
        if not re.search(r'""".*?"""', code, re.DOTALL) and not re.search(r"'''.*?'''", code, re.DOTALL):
            return False, "Missing docstring"
        
        # Try to compile the code to check for syntax errors
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        
        return True, "Tool code is valid"
    
    def extract_function_info(self, code):
        """
        Extract function information from code
        
        Args:
            code (str): Tool code
            
        Returns:
            dict: Function information
        """
        try:
            # Create a temporary module
            module_code = compile(code, '<string>', 'exec')
            module = type('module', (), {})
            exec(module_code, module.__dict__)
            
            # Find the function
            function = None
            function_name = None
            
            for name, obj in module.__dict__.items():
                if callable(obj) and not name.startswith('__'):
                    function = obj
                    function_name = name
                    break
            
            if not function:
                return {"error": "No function found in code"}
            
            # Get function signature
            sig = inspect.signature(function)
            params = {}
            
            for name, param in sig.parameters.items():
                param_type = "any"
                
                # Try to extract type hints
                if param.annotation != inspect.Parameter.empty:
                    if hasattr(param.annotation, "__name__"):
                        param_type = param.annotation.__name__
                    else:
                        param_type = str(param.annotation)
                
                # Get default value if any
                default = None
                has_default = param.default != inspect.Parameter.empty
                if has_default:
                    default = param.default
                
                params[name] = {
                    "type": param_type,
                    "required": not has_default,
                    "default": default
                }
            
            # Extract docstring
            docstring = inspect.getdoc(function) or ""
            
            return {
                "name": function_name,
                "parameters": params,
                "docstring": docstring,
                "return_type": str(sig.return_annotation) if sig.return_annotation != inspect.Signature.empty else "any"
            }
        
        except Exception as e:
            return {"error": f"Error extracting function info: {str(e)}"}
    
    def register_tool(self, name, code, description, parameters=None, examples=None):
        """
        Register a new tool
        
        Args:
            name (str): Tool name
            code (str): Tool code
            description (str): Tool description
            parameters (dict, optional): Tool parameters
            examples (list, optional): Tool usage examples
            
        Returns:
            dict: Registration status
        """
        # Validate tool code
        is_valid, message = self.validate_tool_code(code)
        if not is_valid:
            return {"success": False, "error": message}
        
        # Extract function info if parameters not provided
        if not parameters:
            func_info = self.extract_function_info(code)
            if "error" in func_info:
                return {"success": False, "error": func_info["error"]}
            
            parameters = func_info["parameters"]
            
            # Use extracted name if not provided
            if not name:
                name = func_info["name"]
            
            # Use docstring as description if not provided
            if not description and "docstring" in func_info:
                description = func_info["docstring"]
        
        # Register with interpreter system
        if self.interpreter_system:
            success, result = self.interpreter_system.register_tool(
                code, name, description, parameters, examples
            )
            
            if not success:
                return {"success": False, "error": result}
        
        # Store in database if session available
        if self.db_session:
            try:
                # Check if tool already exists
                existing_tool = self.db_session.query(Tool).filter_by(name=name).first()
                
                if existing_tool:
                    # Update existing tool
                    existing_tool.code = code
                    existing_tool.description = description
                    existing_tool.parameters = json.dumps(parameters) if parameters else None
                    existing_tool.examples = json.dumps(examples) if examples else None
                    tool_id = existing_tool.id
                else:
                    # Create new tool
                    new_tool = Tool(
                        name=name,
                        code=code,
                        description=description,
                        parameters=json.dumps(parameters) if parameters else None,
                        examples=json.dumps(examples) if examples else None
                    )
                    self.db_session.add(new_tool)
                    self.db_session.flush()
                    tool_id = new_tool.id
                
                self.db_session.commit()
                
                # Update registered tools
                self.registered_tools[name] = {
                    "id": tool_id,
                    "code": code,
                    "description": description,
                    "parameters": parameters or {},
                    "examples": examples or []
                }
                
                return {
                    "success": True, 
                    "message": "Tool registered successfully",
                    "tool_id": tool_id
                }
            
            except Exception as e:
                self.db_session.rollback()
                return {"success": False, "error": str(e)}
        
        # If no database session, just store in memory
        self.registered_tools[name] = {
            "id": len(self.registered_tools) + 1,
            "code": code,
            "description": description,
            "parameters": parameters or {},
            "examples": examples or []
        }
        
        return {
            "success": True, 
            "message": "Tool registered in memory only",
            "tool_id": self.registered_tools[name]["id"]
        }
    
    def get_tool(self, name):
        """
        Get tool by name
        
        Args:
            name (str): Tool name
            
        Returns:
            dict: Tool information or None
        """
        return self.registered_tools.get(name)
    
    def list_tools(self):
        """
        List all registered tools
        
        Returns:
            list: List of tool information
        """
        return [
            {
                "id": info["id"],
                "name": name,
                "description": info["description"],
                "parameters": info["parameters"],
                "examples": info["examples"]
            }
            for name, info in self.registered_tools.items()
        ]
    
    def delete_tool(self, name):
        """
        Delete a tool
        
        Args:
            name (str): Tool name
            
        Returns:
            dict: Deletion status
        """
        if name not in self.registered_tools:
            return {"success": False, "error": "Tool not found"}
        
        # Delete from database if session available
        if self.db_session:
            try:
                tool = self.db_session.query(Tool).filter_by(name=name).first()
                
                if tool:
                    self.db_session.delete(tool)
                    self.db_session.commit()
            
            except Exception as e:
                self.db_session.rollback()
                return {"success": False, "error": str(e)}
        
        # Delete from memory
        del self.registered_tools[name]
        
        # Reset interpreter to remove the tool
        if self.interpreter_system:
            self.interpreter_system.reset_interpreter()
        
        return {"success": True, "message": "Tool deleted successfully"}
    
    def generate_tool_documentation(self):
        """
        Generate documentation for all tools
        
        Returns:
            str: Markdown documentation
        """
        if not self.registered_tools:
            return "No tools registered."
        
        docs = "# Custom Tools Documentation\n\n"
        
        for name, info in self.registered_tools.items():
            docs += f"## {name}\n\n"
            docs += f"{info['description']}\n\n"
            
            if info["parameters"]:
                docs += "### Parameters\n\n"
                for param_name, param_info in info["parameters"].items():
                    required = "Required" if param_info.get("required", False) else "Optional"
                    default = f", Default: `{param_info.get('default')}`" if "default" in param_info and param_info["default"] is not None else ""
                    docs += f"- `{param_name}` ({param_info.get('type', 'any')}): {required}{default}\n"
                docs += "\n"
            
            if info["examples"]:
                docs += "### Examples\n\n"
                for example in info["examples"]:
                    docs += f"```python\n{example}\n```\n\n"
            
            docs += "---\n\n"
        
        return docs
