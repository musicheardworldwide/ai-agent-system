# Chat Agent System Instructions

## Overview

The Chat Agent is the primary interface for interacting with the AI Agent System. It provides a conversational interface that allows users to:

1. Ask questions and receive intelligent responses
2. Execute code and perform computations
3. Use custom tools and functions
4. Store and retrieve information from the knowledge base
5. Manage environment variables and secrets

This document provides detailed instructions on how to effectively use the Chat Agent.

## Basic Interaction

The Chat Agent responds to natural language queries entered in the chat interface. You can:

- Ask factual questions
- Request code generation
- Ask for explanations of concepts
- Request data analysis
- Perform system management tasks

## Code Execution

The Chat Agent can execute code in various programming languages. To run code:

1. Simply ask the agent to write code for a specific task
2. The agent will generate the code and execute it automatically
3. Results will be displayed in the chat

Example prompts:
- "Calculate the factorial of 10 using Python"
- "Create a function to convert Celsius to Fahrenheit"
- "Generate a random password with 12 characters"

## Memory System

The Chat Agent has a sophisticated memory system that allows it to:

1. Remember information from the current conversation
2. Recall information from past conversations
3. Store important information in the knowledge base

To use the memory system:

- To store information: "Remember that my project deadline is May 15th"
- To recall information: "What do you know about my project deadline?"
- To update information: "Update my project deadline to May 20th"

## Using Custom Tools

The Chat Agent can use custom tools that have been registered in the system. To use a tool:

1. Request the tool by name or describe what you want to accomplish
2. Provide any required parameters
3. The agent will execute the tool and return the results

Example prompts:
- "Use the calculator tool to multiply 123.45 by 67.89"
- "Generate an image of a mountain landscape"
- "Analyze the sentiment of this text: 'I really enjoyed the movie'"

## Knowledge Base Integration

The Chat Agent can store and retrieve information from the knowledge base:

1. To add information: "Add this to the knowledge base: [information]"
2. To query information: "What does the knowledge base contain about [topic]?"
3. To update information: "Update the knowledge base entry about [topic]"

## Environment Variable Management

The Chat Agent can manage environment variables and secrets:

1. To set a variable: "Set environment variable API_KEY to 'abc123'"
2. To get a variable: "What is the value of environment variable API_KEY?"
3. To delete a variable: "Delete environment variable API_KEY"

Note: For security reasons, sensitive variables will be masked in the chat interface.

## Advanced Features

### RAG (Retrieval-Augmented Generation)

The Chat Agent uses RAG to enhance responses with relevant information:

1. It automatically retrieves relevant information from the knowledge base
2. It incorporates this information into responses
3. It cites sources when information is retrieved from the knowledge base

### Context Management

The Chat Agent maintains context throughout the conversation:

1. It remembers previous messages in the current session
2. It can refer back to earlier parts of the conversation
3. It can maintain multiple conversation threads

To manage context:
- To start a new context: "Let's start a new conversation"
- To refer to previous context: "Regarding what we discussed earlier about [topic]..."

### Tool Creation

The Chat Agent can help create new tools:

1. Ask: "Create a new tool that [description of functionality]"
2. The agent will guide you through defining the tool's:
   - Name and description
   - Parameters
   - Implementation code
   - Example usage

## Best Practices

1. **Be specific**: The more specific your request, the better the response.
2. **Provide context**: When asking follow-up questions, include relevant context.
3. **Use code blocks**: For code-related queries, use code blocks (```).
4. **Break down complex tasks**: For complex tasks, break them down into smaller steps.
5. **Verify outputs**: Always verify generated code or critical information.

## Troubleshooting

If you encounter issues with the Chat Agent:

1. **Unclear responses**: Ask for clarification or rephrase your question.
2. **Code errors**: Ask for debugging help or provide more details about the error.
3. **Tool failures**: Check that all required parameters are provided correctly.
4. **Memory issues**: If the agent doesn't recall information, try providing more context.

## Examples

### Example 1: Code Generation and Execution

User: "Write a Python function to calculate the Fibonacci sequence up to n terms"

Agent: *Generates and executes code, showing the result*

### Example 2: Using the Memory System

User: "Remember that my favorite programming language is Python"
Agent: "I'll remember that your favorite programming language is Python."

User: "What's my favorite programming language?"
Agent: "Your favorite programming language is Python."

### Example 3: Using Custom Tools

User: "Use the weather tool to check the forecast for New York"
Agent: *Executes weather tool and displays forecast*

### Example 4: Knowledge Base Integration

User: "Add this to the knowledge base: The company meeting is scheduled for Friday at 2 PM"
Agent: "Added to knowledge base: The company meeting is scheduled for Friday at 2 PM"

User: "When is the company meeting?"
Agent: "According to the knowledge base, the company meeting is scheduled for Friday at 2 PM."
