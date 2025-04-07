"""
DevChat interpreter model for code understanding and analysis
"""
import os
import re
import ast
import time
import json
import threading
import networkx as nx
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import chromadb
from chromadb.utils import embedding_functions
import requests

class CodeParser:
    """
    Parses Python code to extract structure and relationships
    """
    
    def __init__(self):
        """Initialize the code parser"""
        pass
    
    def parse_file(self, file_path):
        """
        Parse a Python file to extract its structure
        
        Args:
            file_path (str): Path to the Python file
            
        Returns:
            dict: File structure information
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST
            tree = ast.parse(content)
            
            # Extract imports
            imports = self._extract_imports(tree)
            
            # Extract classes and functions
            classes = self._extract_classes(tree)
            functions = self._extract_functions(tree)
            
            # Extract function calls
            function_calls = self._extract_function_calls(tree)
            
            return {
                'path': file_path,
                'imports': imports,
                'classes': classes,
                'functions': functions,
                'function_calls': function_calls,
                'content': content
            }
        
        except Exception as e:
            return {
                'path': file_path,
                'error': str(e)
            }
    
    def _extract_imports(self, tree):
        """Extract imports from AST"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append({
                        'type': 'import',
                        'name': name.name,
                        'alias': name.asname
                    })
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module
                for name in node.names:
                    imports.append({
                        'type': 'importfrom',
                        'module': module,
                        'name': name.name,
                        'alias': name.asname
                    })
        
        return imports
    
    def _extract_classes(self, tree):
        """Extract classes from AST"""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Get base classes
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(f"{self._get_attribute_full_name(base)}")
                
                # Get methods
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append({
                            'name': item.name,
                            'lineno': item.lineno,
                            'args': self._extract_function_args(item),
                            'docstring': ast.get_docstring(item)
                        })
                
                classes.append({
                    'name': node.name,
                    'lineno': node.lineno,
                    'bases': bases,
                    'methods': methods,
                    'docstring': ast.get_docstring(node)
                })
        
        return classes
    
    def _extract_functions(self, tree):
        """Extract functions from AST"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not isinstance(node.parent, ast.ClassDef):
                functions.append({
                    'name': node.name,
                    'lineno': node.lineno,
                    'args': self._extract_function_args(node),
                    'docstring': ast.get_docstring(node)
                })
        
        return functions
    
    def _extract_function_args(self, func_node):
        """Extract function arguments"""
        args = []
        
        for arg in func_node.args.args:
            arg_info = {'name': arg.arg}
            
            # Get type annotation if available
            if arg.annotation:
                if isinstance(arg.annotation, ast.Name):
                    arg_info['type'] = arg.annotation.id
                elif isinstance(arg.annotation, ast.Attribute):
                    arg_info['type'] = self._get_attribute_full_name(arg.annotation)
            
            args.append(arg_info)
        
        return args
    
    def _extract_function_calls(self, tree):
        """Extract function calls from AST"""
        calls = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append({
                        'name': node.func.id,
                        'lineno': node.lineno
                    })
                elif isinstance(node.func, ast.Attribute):
                    calls.append({
                        'name': self._get_attribute_full_name(node.func),
                        'lineno': node.lineno
                    })
        
        return calls
    
    def _get_attribute_full_name(self, node):
        """Get the full name of an attribute (e.g., module.submodule.function)"""
        parts = []
        
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        
        if isinstance(node, ast.Name):
            parts.append(node.id)
        
        return '.'.join(reversed(parts))


class CodeWatcher(FileSystemEventHandler):
    """
    Watches for file changes in the codebase
    """
    
    def __init__(self, dev_chat):
        """Initialize the code watcher"""
        self.dev_chat = dev_chat
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        # Check if it's a Python file
        if event.src_path.endswith('.py'):
            self.dev_chat.update_file(event.src_path)
    
    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return
        
        # Check if it's a Python file
        if event.src_path.endswith('.py'):
            self.dev_chat.add_file(event.src_path)
    
    def on_deleted(self, event):
        """Handle file deletion events"""
        if event.is_directory:
            return
        
        # Check if it's a Python file
        if event.src_path.endswith('.py'):
            self.dev_chat.remove_file(event.src_path)


class DevChatInterpreter:
    """
    DevChat interpreter model that maintains a live, structured understanding of the codebase
    """
    
    def __init__(self, project_root, api_base_url=None, api_key=None):
        """
        Initialize the DevChat interpreter
        
        Args:
            project_root (str): Root directory of the project
            api_base_url (str, optional): API base URL for embeddings
            api_key (str, optional): API key for embeddings
        """
        self.project_root = os.path.abspath(project_root)
        self.api_base_url = api_base_url or "https://api.lastwinnersllc.com"
        self.api_key = api_key
        
        # Initialize components
        self.parser = CodeParser()
        self.code_graph = nx.DiGraph()
        self.file_info = {}
        
        # Initialize embedding function
        self.embedding_function = self._initialize_embedding_function()
        
        # Initialize vector database
        self.db_client = chromadb.Client()
        self.code_collection = self.db_client.create_collection(
            name="code_embeddings",
            embedding_function=self.embedding_function
        )
        
        # Initialize file watcher
        self.observer = None
        self.event_handler = CodeWatcher(self)
        
        # Scan the project
        self.scan_project()
        
        # Start watching for changes
        self.start_watching()
    
    def _initialize_embedding_function(self):
        """Initialize the embedding function"""
        try:
            # Use the nomic-embed-text model
            return embedding_functions.RemoteEmbeddingFunction(
                api_url=f"{self.api_base_url}/embeddings",
                api_key=self.api_key,
                model_name="nomic-embed-text"
            )
        except Exception as e:
            print(f"Error initializing embedding function: {e}")
            # Fall back to default embedding function
            return embedding_functions.DefaultEmbeddingFunction()
    
    def scan_project(self):
        """Scan the entire project and build the code graph"""
        print(f"Scanning project: {self.project_root}")
        
        # Find all Python files
        python_files = []
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        # Parse each file
        for file_path in python_files:
            self.add_file(file_path)
        
        # Build relationships
        self._build_relationships()
        
        print(f"Scanned {len(python_files)} Python files")
    
    def add_file(self, file_path):
        """
        Add a file to the code graph
        
        Args:
            file_path (str): Path to the Python file
        """
        # Parse the file
        file_info = self.parser.parse_file(file_path)
        
        # Store file info
        rel_path = os.path.relpath(file_path, self.project_root)
        self.file_info[rel_path] = file_info
        
        # Add to code graph
        self.code_graph.add_node(rel_path, type='file', info=file_info)
        
        # Add to vector database
        self._add_to_vector_db(rel_path, file_info)
    
    def update_file(self, file_path):
        """
        Update a file in the code graph
        
        Args:
            file_path (str): Path to the Python file
        """
        # Remove the file first
        self.remove_file(file_path)
        
        # Add it again
        self.add_file(file_path)
        
        # Rebuild relationships
        self._build_relationships()
    
    def remove_file(self, file_path):
        """
        Remove a file from the code graph
        
        Args:
            file_path (str): Path to the Python file
        """
        rel_path = os.path.relpath(file_path, self.project_root)
        
        # Remove from file info
        if rel_path in self.file_info:
            del self.file_info[rel_path]
        
        # Remove from code graph
        if self.code_graph.has_node(rel_path):
            self.code_graph.remove_node(rel_path)
        
        # Remove from vector database
        try:
            self.code_collection.delete(ids=[rel_path])
            
            # Also remove any function or class entries
            for id in self.code_collection.get()['ids']:
                if id.startswith(f"{rel_path}:"):
                    self.code_collection.delete(ids=[id])
        except Exception as e:
            print(f"Error removing from vector database: {e}")
    
    def _add_to_vector_db(self, rel_path, file_info):
        """Add file information to the vector database"""
        try:
            # Add the file itself
            content = file_info.get('content', '')
            if content:
                # Create a summary of the file
                summary = f"File: {rel_path}\n"
                
                # Add imports
                imports = file_info.get('imports', [])
                if imports:
                    summary += "Imports:\n"
                    for imp in imports:
                        if imp['type'] == 'import':
                            summary += f"  import {imp['name']}"
                            if imp['alias']:
                                summary += f" as {imp['alias']}"
                            summary += "\n"
                        else:
                            summary += f"  from {imp['module']} import {imp['name']}"
                            if imp['alias']:
                                summary += f" as {imp['alias']}"
                            summary += "\n"
                
                # Add classes
                classes = file_info.get('classes', [])
                if classes:
                    summary += "Classes:\n"
                    for cls in classes:
                        summary += f"  class {cls['name']}"
                        if cls['bases']:
                            summary += f"({', '.join(cls['bases'])})"
                        summary += "\n"
                        if cls['docstring']:
                            summary += f"    \"{cls['docstring']}\"\n"
                
                # Add functions
                functions = file_info.get('functions', [])
                if functions:
                    summary += "Functions:\n"
                    for func in functions:
                        summary += f"  def {func['name']}("
                        args = func.get('args', [])
                        arg_strs = []
                        for arg in args:
                            arg_str = arg['name']
                            if 'type' in arg:
                                arg_str += f": {arg['type']}"
                            arg_strs.append(arg_str)
                        summary += ", ".join(arg_strs)
                        summary += ")\n"
                        if func['docstring']:
                            summary += f"    \"{func['docstring']}\"\n"
                
                # Add to vector database
                self.code_collection.add(
                    ids=[rel_path],
                    documents=[summary],
                    metadatas=[{
                        'type': 'file',
                        'path': rel_path,
                        'last_updated': time.time()
                    }]
                )
                
                # Add individual classes and functions
                for cls in classes:
                    cls_id = f"{rel_path}:class:{cls['name']}"
                    cls_doc = cls['docstring'] or f"Class {cls['name']} in {rel_path}"
                    self.code_collection.add(
                        ids=[cls_id],
                        documents=[cls_doc],
                        metadatas=[{
                            'type': 'class',
                            'name': cls['name'],
                            'file': rel_path,
                            'lineno': cls['lineno'],
                            'last_updated': time.time()
                        }]
                    )
                
                for func in functions:
                    func_id = f"{rel_path}:function:{func['name']}"
                    func_doc = func['docstring'] or f"Function {func['name']} in {rel_path}"
                    self.code_collection.add(
                        ids=[func_id],
                        documents=[func_doc],
                        metadatas=[{
                            'type': 'function',
                            'name': func['name'],
                            'file': rel_path,
                            'lineno': func['lineno'],
                            'last_updated': time.time()
                        }]
                    )
        
        except Exception as e:
            print(f"Error adding to vector database: {e}")
    
    def _build_relationships(self):
        """Build relationships between files, classes, and functions"""
        # Clear existing relationships
        edges_to_remove = [e for e in self.code_graph.edges()]
        self.code_graph.remove_edges_from(edges_to_remove)
        
        # Build import relationships
        for file_path, file_info in self.file_info.items():
            imports = file_info.get('imports', [])
            
            for imp in imports:
                if imp['type'] == 'import':
                    # Try to find the imported module
                    imported_module = imp['name']
                    self._add_import_edge(file_path, imported_module)
                
                elif imp['type'] == 'importfrom':
                    # Try to find the imported module
                    imported_module = imp['module']
                    self._add_import_edge(file_path, imported_module)
        
        # Build function call relationships
        for file_path, file_info in self.file_info.items():
            function_calls = file_info.get('function_calls', [])
            
            for call in function_calls:
                # Try to find the called function
                called_function = call['name']
                
                # Check if it's a method call (contains a dot)
                if '.' in called_function:
                    parts = called_function.split('.')
                    module_name = parts[0]
                    
                    # Try to find the module
                    for other_file, other_info in self.file_info.items():
                        # Check if this file defines a class with the module name
                        for cls in other_info.get('classes', []):
                            if cls['name'] == module_name:
                                # Add edge from file to class
                                self.code_graph.add_edge(
                                    file_path, 
                                    f"{other_file}:class:{cls['name']}",
                                    type='calls'
                                )
                
                # Check if it's a direct function call
                else:
                    for other_file, other_info in self.file_info.items():
                        # Check if this file defines the function
                        for func in other_info.get('functions', []):
                            if func['name'] == called_function:
                                # Add edge from file to function
                                self.code_graph.add_edge(
                                    file_path, 
                                    f"{other_file}:function:{func['name']}",
                                    type='calls'
                                )
    
    def _add_import_edge(self, file_path, imported_module):
        """Add an import edge to the code graph"""
        # Convert module name to potential file path
        module_path = imported_module.replace('.', '/')
        
        # Try different variations
        variations = [
            f"{module_path}.py",
            f"{module_path}/__init__.py"
        ]
        
        for var in variations:
            # Check if this file exists in our file_info
            for other_file in self.file_info.keys():
                if other_file.endswith(var):
                    # Add edge from file to imported file
                    self.code_graph.add_edge(file_path, other_file, type='imports')
                    return
    
    def start_watching(self):
        """Start watching for file changes"""
        if self.observer is None:
            self.observer = Observer()
            self.observer.schedule(self.event_handler, self.project_root, recursive=True)
            self.observer.start()
            print(f"Started watching for changes in {self.project_root}")
    
    def stop_watching(self):
        """Stop watching for file changes"""
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            print("Stopped watching for changes")
    
    def get_file_info(self, file_path):
        """
        Get information about a file
        
        Args:
            file_path (str): Path to the file (relative to project root)
            
        Returns:
            dict: File information
        """
        return self.file_info.get(file_path)
    
    def get_dependencies(self, file_path):
        """
        Get dependencies of a file
        
        Args:
            file_path (str): Path to the file (relative to project root)
            
        Returns:
            list: Dependencies
        """
        dependencies = []
        
        # Check if the file exists in the graph
        if not self.code_graph.has_node(file_path):
            return dependencies
        
        # Get outgoing edges (imports)
        for _, target, data in self.code_graph.out_edges(file_path, data=True):
            if data.get('type') == 'imports':
                dependencies.append({
                    'type': 'imports',
                    'target': target
                })
        
        return dependencies
    
    def get_dependents(self, file_path):
        """
        Get files that depend on this file
        
        Args:
            file_path (str): Path to the file (relative to project root)
            
        Returns:
            list: Dependents
        """
        dependents = []
        
        # Check if the file exists in the graph
        if not self.code_graph.has_node(file_path):
            return dependents
        
        # Get incoming edges (imported by)
        for source, _, data in self.code_graph.in_edges(file_path, data=True):
            if data.get('type') == 'imports':
                dependents.append({
                    'type': 'imported_by',
                    'source': source
                })
        
        return dependents
    
    def get_function_calls(self, function_name):
        """
        Get files that call a specific function
        
        Args:
            function_name (str): Function name
            
        Returns:
            list: Files that call this function
        """
        callers = []
        
        # Find the function in the graph
        for node in self.code_graph.nodes():
            if ':function:' in node and node.endswith(f":{function_name}"):
                # Get incoming edges (calls)
                for source, _, data in self.code_graph.in_edges(node, data=True):
                    if data.get('type') == 'calls':
                        callers.append({
                            'type': 'called_by',
                            'source': source
                        })
        
        return callers
    
    def search_code(self, query, n_results=5):
        """
        Search the codebase using semantic search
        
        Args:
            query (str): Search query
            n_results (int): Number of results to return
            
        Returns:
            list: Search results
        """
        try:
            results = self.code_collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            search_results = []
            
            for i, (id, document, metadata) in enumerate(zip(
                results['ids'][0],
                results['documents'][0],
                results['metadatas'][0]
            )):
                search_results.append({
                    'id': id,
                    'document': document,
                    'metadata': metadata,
                    'score': results['distances'][0][i] if 'distances' in results else None
                })
            
            return search_results
        
        except Exception as e:
            print(f"Error searching code: {e}")
            return []
    
    def get_impact_analysis(self, file_path):
        """
        Analyze the impact of changing a file
        
        Args:
            file_path (str): Path to the file (relative to project root)
            
        Returns:
            dict: Impact analysis
        """
        # Get direct dependents
        direct_dependents = self.get_dependents(file_path)
        
        # Get transitive dependents (files that depend on the dependents)
        transitive_dependents = []
        visited = set([file_path])
        
        def visit_dependents(path):
            deps = self.get_dependents(path)
            for dep in deps:
                dep_path = dep['source']
                if dep_path not in visited:
                    visited.add(dep_path)
                    transitive_dependents.append({
                        'type': 'transitively_imported_by',
                        'source': dep_path,
                        'via': path
                    })
                    visit_dependents(dep_path)
        
        for dep in direct_dependents:
            visit_dependents(dep['source'])
        
        # Get functions defined in this file
        functions = []
        file_info = self.get_file_info(file_path)
        if file_info:
            functions = file_info.get('functions', [])
        
        # Get classes defined in this file
        classes = []
        if file_info:
            classes = file_info.get('classes', [])
        
        return {
            'file': file_path,
            'direct_dependents': direct_dependents,
            'transitive_dependents': transitive_dependents,
            'functions': functions,
            'classes': classes,
            'total_impact_count': len(direct_dependents) + len(transitive_dependents)
        }
    
    def get_database_interactions(self):
        """
        Find all functions that interact with the database
        
        Returns:
            list: Functions that interact with the database
        """
        db_functions = []
        
        # Look for common database interaction patterns
        db_patterns = [
            r'\.execute\(',
            r'\.query\(',
            r'\.commit\(',
            r'\.rollback\(',
            r'\.cursor\(',
            r'\.connection',
            r'session\.add\(',
            r'session\.delete\(',
            r'session\.commit\(',
            r'db\.session',
            r'database',
            r'Database',
            r'SQLAlchemy',
            r'Model\.',
            r'models\.'
        ]
        
        # Check each file
        for file_path, file_info in self.file_info.items():
            content = file_info.get('content', '')
            
            # Check if any pattern matches
            if any(re.search(pattern, content) for pattern in db_patterns):
                # Find functions in this file
                for func in file_info.get('functions', []):
                    db_functions.append({
                        'file': file_path,
                        'function': func['name'],
                        'lineno': func['lineno']
                    })
                
                # Find methods in classes
                for cls in file_info.get('classes', []):
                    for method in cls.get('methods', []):
                        db_functions.append({
                            'file': file_path,
                            'class': cls['name'],
                            'method': method['name'],
                            'lineno': method['lineno']
                        })
        
        return db_functions
    
    def process_query(self, query):
        """
        Process a natural language query about the codebase
        
        Args:
            query (str): Natural language query
            
        Returns:
            dict: Response
        """
        # Check for specific query patterns
        if re.search(r'impact|affect|change', query, re.IGNORECASE) and re.search(r'\.py', query):
            # Extract file name from query
            file_match = re.search(r'(\w+\.py)', query)
            if file_match:
                file_name = file_match.group(1)
                
                # Find the file in the project
                for file_path in self.file_info.keys():
                    if file_path.endswith(file_name):
                        # Get impact analysis
                        impact = self.get_impact_analysis(file_path)
                        return {
                            'type': 'impact_analysis',
                            'query': query,
                            'file': file_path,
                            'impact': impact
                        }
        
        elif re.search(r'database|db|sql', query, re.IGNORECASE):
            # Find database interactions
            db_functions = self.get_database_interactions()
            return {
                'type': 'database_interactions',
                'query': query,
                'functions': db_functions
            }
        
        elif re.search(r'function|call|method', query, re.IGNORECASE) and re.search(r'\w+\(', query):
            # Extract function name from query
            func_match = re.search(r'(\w+)\(', query)
            if func_match:
                function_name = func_match.group(1)
                
                # Get function calls
                callers = self.get_function_calls(function_name)
                return {
                    'type': 'function_calls',
                    'query': query,
                    'function': function_name,
                    'callers': callers
                }
        
        # Default to semantic search
        search_results = self.search_code(query)
        return {
            'type': 'semantic_search',
            'query': query,
            'results': search_results
        }
    
    def get_system_stats(self):
        """
        Get statistics about the codebase
        
        Returns:
            dict: System statistics
        """
        return {
            'files': len(self.file_info),
            'nodes': self.code_graph.number_of_nodes(),
            'edges': self.code_graph.number_of_edges(),
            'vector_items': len(self.code_collection.get()['ids']) if self.code_collection.count() > 0 else 0
        }
    
    def generate_code_map(self, output_file=None):
        """
        Generate a visual map of the code
        
        Args:
            output_file (str, optional): Path to save the map
            
        Returns:
            dict: Map data
        """
        # Create a simplified graph for visualization
        vis_graph = {
            'nodes': [],
            'links': []
        }
        
        # Add nodes
        for node in self.code_graph.nodes():
            node_type = 'file'
            if ':class:' in node:
                node_type = 'class'
            elif ':function:' in node:
                node_type = 'function'
            
            vis_graph['nodes'].append({
                'id': node,
                'type': node_type,
                'name': node.split(':')[-1] if ':' in node else node
            })
        
        # Add links
        for source, target, data in self.code_graph.edges(data=True):
            vis_graph['links'].append({
                'source': source,
                'target': target,
                'type': data.get('type', 'unknown')
            })
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(vis_graph, f, indent=2)
        
        return vis_graph
