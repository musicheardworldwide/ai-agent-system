# DevChat Interpreter Model Instructions

## Overview

The DevChat Interpreter Model is an advanced component of the AI Agent System that maintains a live, structured understanding of the entire codebase. It provides code intelligence, relationship awareness, and self-improvement capabilities through a chat-based interface.

This document provides detailed instructions on how to effectively use the DevChat Interpreter Model.

## Core Capabilities

The DevChat Interpreter Model offers the following key capabilities:

1. **Dynamic Code Mapping**: Continuously parses and indexes all source files in the project
2. **Relationship Awareness**: Captures and represents how modules interact
3. **Realtime Updates**: Automatically detects code changes and updates the internal map
4. **Code Intelligence Memory**: Stores code relationships in a vector database for semantic access
5. **Integration Interface**: Provides a chat-based interface to query the live system map
6. **Self-Improvement**: Proposes and implements code improvements

## Interacting with DevChat

### Through the DevChat Interface

The primary way to interact with DevChat is through its dedicated interface:

1. Navigate to the DevChat section in the UI
2. Enter natural language queries about the codebase
3. View visualizations of code relationships
4. Explore impact analyses and other insights

### Through the Chat Interface

You can also access DevChat capabilities through the main Chat interface:

```
Ask DevChat: [your code-related query]
```

## Query Types and Examples

DevChat understands various types of queries about the codebase:

### Impact Analysis

To understand the impact of changing a file:

```
What modules are impacted if I change auth.py?
```

or

```
What would break if I modify the User class?
```

DevChat will:
1. Identify the file or component
2. Analyze direct and transitive dependencies
3. Present a comprehensive impact report

### Function and Method Queries

To find where functions are defined or used:

```
Where is the function process_query defined?
```

or

```
Show me all places where save_user_data is called
```

DevChat will:
1. Locate the function definition
2. Find all references and calls
3. Present the results with file locations and line numbers

### Database Interaction Queries

To understand database usage:

```
Show me all functions that write to the database
```

or

```
Which modules interact with the users table?
```

DevChat will:
1. Identify database operations in the code
2. Categorize them by type (read, write, etc.)
3. Present a list of functions with their locations

### Code Structure Queries

To understand the structure of the codebase:

```
Explain the architecture of the RAG memory system
```

or

```
How is the authentication flow implemented?
```

DevChat will:
1. Analyze relevant code components
2. Identify relationships and patterns
3. Generate a high-level explanation with key components

### Semantic Code Search

To find code based on functionality:

```
Find code that handles file uploads
```

or

```
Where is the error handling for API requests?
```

DevChat will:
1. Perform semantic search across the codebase
2. Rank results by relevance
3. Present the most pertinent code sections

## Advanced Features

### Code Map Visualization

To visualize code relationships:

```
Show me a map of the code
```

or

```
Visualize dependencies for the database module
```

DevChat will generate a visual representation of code relationships that you can explore interactively.

### Code Quality Analysis

To identify potential improvements:

```
Analyze code quality in auth.py
```

or

```
Find potential performance issues in the codebase
```

DevChat will:
1. Analyze the specified code
2. Identify potential issues or improvements
3. Provide recommendations with explanations

### Self-Improvement Proposals

DevChat can propose improvements to the codebase:

```
Suggest improvements for the error handling in api_routes.py
```

or

```
How can we optimize the database queries in user_service.py?
```

DevChat will:
1. Analyze the current implementation
2. Generate specific improvement suggestions
3. Provide code examples for implementation

### Implementation Assistance

DevChat can help implement changes:

```
Help me implement the suggested improvements for error handling
```

or

```
Create a test case for the user authentication function
```

DevChat will:
1. Generate implementation code
2. Explain the changes
3. Provide step-by-step guidance

## Development Environment Integration

### Code Scanning

To scan the entire codebase:

```
Scan the project
```

DevChat will:
1. Parse all source files
2. Build the code graph
3. Update its internal representation
4. Provide statistics about the scan

### Watching for Changes

DevChat automatically watches for file changes, but you can control this behavior:

```
Stop watching for changes
```

or

```
Start watching for changes
```

### Focused Analysis

To analyze specific parts of the codebase:

```
Focus analysis on the backend directory
```

or

```
Analyze only Python files
```

## Best Practices

1. **Be specific**: When asking about code, provide specific file names or function names
2. **Start broad, then narrow**: Begin with high-level queries, then drill down into details
3. **Use for planning**: Consult DevChat before making significant code changes
4. **Verify suggestions**: Always review and test code suggestions before implementation
5. **Provide feedback**: If DevChat misunderstands code relationships, provide clarification
6. **Regular scanning**: Periodically trigger a full scan after major code changes

## Troubleshooting

If you encounter issues with DevChat:

1. **Outdated information**: Try rescanning the project
2. **Missing files**: Ensure the files are in the project directory
3. **Incorrect relationships**: Provide feedback and request a rescan
4. **Performance issues**: Try focusing analysis on specific directories
5. **Query misunderstandings**: Rephrase with more specific terms

## Examples

### Example 1: Impact Analysis

User: "What modules are impacted if I change the authentication middleware?"

DevChat:
```
Impact Analysis for authentication middleware (auth_middleware.py):

Direct Dependents:
- api_routes.py
- user_controller.py
- admin_routes.py

Transitive Dependents:
- dashboard_service.py (via api_routes.py)
- notification_service.py (via user_controller.py)

Total Impact: 5 files

The authentication middleware is a critical component with moderate coupling. Changes should be carefully tested, particularly the token validation logic which is used by all dependent modules.
```

### Example 2: Code Structure Explanation

User: "Explain how the RAG memory system works"

DevChat:
```
RAG Memory System Architecture:

The RAG (Retrieval-Augmented Generation) memory system is implemented across several files:

1. rag.py - Core implementation
   - Contains the RAGMemory class that manages the memory store
   - Implements embedding generation using nomic-embed-text
   - Handles retrieval and ranking of relevant context

2. memory_store.py
   - Implements the vector database interface using ChromaDB
   - Manages memory persistence and indexing
   - Handles memory segmentation and pruning

3. context_processor.py
   - Processes retrieved memories into usable context
   - Implements relevance scoring algorithms
   - Handles context integration into prompts

Key Workflows:
1. When a user query is received, it's embedded using the embedding model
2. The embedding is used to search the vector database for similar memories
3. Retrieved memories are ranked by relevance and recency
4. Top memories are processed into context
5. Context is integrated into the prompt for the LLM

The system uses a multi-tier approach with short-term, long-term, and knowledge base memories, each with different retention policies.
```

### Example 3: Finding Database Interactions

User: "Show me all functions that write to the database"

DevChat:
```
Database Write Operations:

1. user_service.py:
   - create_user(username, email, password) - Line 45
   - update_user_profile(user_id, profile_data) - Line 78
   - delete_user(user_id) - Line 112

2. knowledge_base.py:
   - add_entry(topic, content, metadata) - Line 34
   - update_entry(entry_id, content) - Line 67
   - delete_entry(entry_id) - Line 89

3. conversation_store.py:
   - save_message(conversation_id, role, content) - Line 56
   - mark_conversation_complete(conversation_id) - Line 103

4. task_manager.py:
   - create_task(description, priority) - Line 28
   - update_task_status(task_id, status) - Line 61

All write operations use parameterized queries and transaction management for data integrity.
```
