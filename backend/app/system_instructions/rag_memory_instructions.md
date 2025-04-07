# RAG Memory System Instructions

## Overview

The RAG (Retrieval-Augmented Generation) Memory System is a sophisticated component of the AI Agent System that enhances the interpreter's responses by retrieving relevant context from past conversations and stored knowledge. It serves as the system's contextual memory, allowing for more informed and personalized interactions.

This document provides detailed instructions on how to effectively use and configure the RAG Memory System.

## Core Functionality

The RAG Memory System performs the following key functions:

1. **Context Retrieval**: Automatically retrieves relevant information based on user queries
2. **Semantic Search**: Uses embeddings to find semantically similar content
3. **Memory Prioritization**: Ranks retrieved information by relevance and recency
4. **Context Integration**: Seamlessly incorporates retrieved context into responses
5. **Memory Management**: Maintains and organizes the memory store for efficient retrieval

## Memory Levels

The RAG Memory System operates on multiple levels:

### Level 1: Short-term Conversation Memory
- Maintains the current conversation context
- Typically includes the last 10-20 messages
- Automatically included in every query
- No special commands needed to access

### Level 2: Long-term Conversation Memory
- Stores important information from past conversations
- Automatically retrieved when relevant to current query
- Can be explicitly accessed with memory commands
- Persists across sessions

### Level 3: Knowledge Base Integration
- Connects with the Database Agent's knowledge store
- Retrieves factual information and learned knowledge
- Provides citations and sources for retrieved information
- Can be explicitly queried or automatically integrated

## Using the RAG Memory System

### Implicit Memory Usage

The RAG Memory System works automatically in the background:

1. When you ask a question, the system:
   - Analyzes your query
   - Retrieves relevant context from all memory levels
   - Incorporates this context into the response generation
   - Provides a more informed and contextually appropriate answer

No special commands are needed for this basic functionality.

### Explicit Memory Commands

You can explicitly interact with the memory system using these commands:

#### Retrieving Memories

```
What do you remember about [topic]?
```

or

```
Recall our previous discussion about [topic]
```

The system will:
1. Search all memory levels for information about the topic
2. Return the most relevant memories
3. Indicate when and where the information was originally discussed

#### Saving Important Information

```
Remember this for later: [information]
```

or

```
This is important to remember: [information]
```

The system will:
1. Mark this information as high priority
2. Ensure it's retained in long-term memory
3. Confirm the information has been saved

#### Forgetting Information

```
Forget what I said about [topic]
```

The system will:
1. Remove or deprioritize the specified information
2. Confirm what has been forgotten
3. No longer use this information in future responses

#### Memory Summarization

```
Summarize what you remember about [topic]
```

The system will:
1. Collect all memories related to the topic
2. Generate a concise summary
3. Present the key points in chronological order

## Advanced Configuration

### Memory Depth Control

You can control how far back the system searches for relevant context:

```
Use shallow memory for this conversation
```
- Limits retrieval to recent interactions
- Useful for focused, present-oriented discussions

```
Use deep memory for this conversation
```
- Expands retrieval to include older interactions
- Useful when historical context is important

### Relevance Threshold Adjustment

You can adjust how selective the system is when retrieving memories:

```
Set memory relevance threshold to [high/medium/low]
```
- High: Only very closely related memories are retrieved
- Medium: Moderately related memories are retrieved (default)
- Low: Even loosely related memories are retrieved

### Memory Weighting

You can emphasize different types of memories:

```
Prioritize factual memories for this conversation
```
- Emphasizes verified information from the knowledge base

```
Prioritize personal memories for this conversation
```
- Emphasizes user-specific information and preferences

## Memory Analytics

You can analyze the system's memory usage:

```
Show memory statistics
```
- Displays metrics about memory usage and retrieval effectiveness

```
Show memory retrieval for last response
```
- Shows what memories were used to generate the previous response

## Best Practices

1. **Be specific**: When explicitly querying memory, use specific topics or keywords
2. **Highlight importance**: Explicitly mark important information you want remembered
3. **Check understanding**: Periodically ask the system to summarize what it remembers
4. **Manage context**: For new topics, consider starting fresh or explicitly directing memory focus
5. **Provide feedback**: If irrelevant memories are being used, provide feedback to improve retrieval

## Troubleshooting

If you encounter issues with the RAG Memory System:

1. **Irrelevant context**: Try increasing the relevance threshold
2. **Missing information**: Try lowering the relevance threshold or explicitly asking for the topic
3. **Outdated information**: Ask the system to update its knowledge about the topic
4. **Conflicting memories**: Ask for clarification and provide the correct information
5. **Performance issues**: Consider using shallow memory for faster responses

## Examples

### Example 1: Implicit Memory Usage

User: "What programming language should I use for data analysis?"
Agent: *Provides general advice about Python, R, and other languages*

User: "Which one would be best for my web scraping project?"
Agent: *Remembers the context is data analysis for web scraping and tailors the response accordingly*

### Example 2: Explicit Memory Retrieval

User: "What do you remember about my project deadlines?"
Agent: "Based on our previous conversations, I remember that:
1. Your data analysis project is due on May 15th (mentioned 3 days ago)
2. The web scraping component needs to be completed by April 30th (mentioned yesterday)
3. You want to present preliminary findings next week (mentioned today)"

### Example 3: Memory Management

User: "Remember this is important: The client meeting has been moved to Thursday at 2 PM"
Agent: "I've saved this important information: The client meeting has been moved to Thursday at 2 PM. I'll remember this for future reference."

User: "When is our client meeting scheduled?"
Agent: "The client meeting is scheduled for Thursday at 2 PM. This was noted as important information in our earlier conversation."
