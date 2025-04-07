# AI Agent System - Manual Testing Guide

This guide provides instructions for manually testing the AI Agent System through the browser interface.

## Prerequisites

Before testing, ensure you have:

1. Set up your API key in the `.env` file
2. Installed all dependencies
3. Built the frontend
4. Started the application

## Starting the System for Testing

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/yourusername/ai-agent-system.git
cd ai-agent-system

# Create and edit .env file
cp .env.example .env
# Edit the .env file to add your API key

# Install dependencies and start the system
./setup.sh
python run.py
```

## Testing Procedure

### 1. Core Chat Functionality

1. Navigate to http://localhost:5000/chat
2. Enter a test query like "What can you help me with?"
3. Verify that the system responds appropriately
4. Try a more complex query that might require code execution, like "Calculate the factorial of 5"
5. Verify that the system executes the code and returns the correct result

### 2. Tools Management

1. Navigate to http://localhost:5000/tools
2. Click "Add Tool" to create a new tool
3. Enter the following information:
   - Name: "Calculator"
   - Description: "A simple calculator tool"
   - Code: 
     ```python
     def calculator(operation, a, b):
         """
         Perform basic arithmetic operations
         
         Args:
             operation (str): The operation to perform (add, subtract, multiply, divide)
             a (float): First number
             b (float): Second number
             
         Returns:
             float: Result of the operation
         """
         if operation == "add":
             return a + b
         elif operation == "subtract":
             return a - b
         elif operation == "multiply":
             return a * b
         elif operation == "divide":
             if b == 0:
                 return "Error: Division by zero"
             return a / b
         else:
             return "Error: Invalid operation"
     ```
4. Click "Register Tool"
5. Verify that the tool appears in the tools list
6. Go back to the Chat interface and test the tool with a query like "Use the calculator tool to multiply 7 and 8"

### 3. Tasks Management

1. Navigate to http://localhost:5000/tasks
2. Click "Create Task"
3. Enter a description like "Analyze recent conversations for common themes"
4. Set a priority
5. Click "Create Task"
6. Verify that the task appears in the task list
7. Click "Execute" on the task
8. Verify that the task status changes to "completed" after execution

### 4. Logging Interface

1. Navigate to http://localhost:5000/logs
2. Check that system logs are displayed
3. Switch between different log categories (System, API, Interpreter, Database)
4. Click on "Details" for a log entry to view more information
5. Test the "Download" button to download logs

### 5. Code Development Agent

1. Navigate to http://localhost:5000/dev-agent
2. Click "Start Development Agent"
3. Wait for the agent to analyze the codebase and propose a change
4. Review the proposed change
5. Test both "Accept" and "Reject" buttons

### 6. DevChat Interface

1. Navigate to http://localhost:5000/dev-chat
2. Verify that codebase statistics are displayed
3. Enter a query like "What modules are impacted if I change rag.py?"
4. Verify that the system returns an impact analysis
5. Try another query like "Show me all functions that write to the database"
6. Verify that the system returns a list of database interactions
7. Click "View Code Map" to see the code structure

### 7. Environment Variables

1. Use the Chat interface to test environment variable management
2. Try a query like "Set an environment variable API_TEST with value test123"
3. Then try "Get the value of environment variable API_TEST"
4. Verify that the system correctly stores and retrieves the variable

## Testing the API Directly

You can also test the API endpoints directly using tools like curl or Postman:

```bash
# Test the chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, what can you do?"}'

# Test the tools endpoint
curl -X GET http://localhost:5000/api/tools

# Test the dev-chat query endpoint
curl -X POST http://localhost:5000/api/dev-chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What modules are impacted if I change rag.py?"}'
```

## Recording Test Results

When recording your tests:

1. Capture the full browser window to show the interface
2. Demonstrate both successful operations and error handling
3. Show the system's responses to various types of queries
4. Demonstrate the logging functionality to show success/failure of actions
5. Test all major components of the system

## Common Testing Issues

- If the API doesn't respond, check that your API key is correctly set in the .env file
- If the frontend doesn't load properly, ensure you've built it with `npm run build`
- If tools don't register, check the browser console for JavaScript errors
- If the DevChat features don't work, ensure the system has permission to read the codebase files
