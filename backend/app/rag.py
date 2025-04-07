"""
RAG (Retrieval-Augmented Generation) memory system for the AI Agent System
"""
import json
import numpy as np
from chromadb import Client, Settings
import requests
from datetime import datetime
from .config import Config

class RAGMemorySystem:
    """
    Memory system that uses vector embeddings for semantic search and retrieval
    to enhance the context for the interpreter.
    """
    
    def __init__(self, app=None):
        """Initialize the RAG memory system"""
        self.app = app
        self.api_base_url = Config.API_BASE_URL
        self.api_key = Config.API_KEY
        self.embedding_model = Config.EMBEDDING_MODEL
        
        # Initialize ChromaDB
        self.chroma = Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=Config.VECTOR_DB_PATH
        ))
        
        # Create collections if they don't exist
        self.conversations_collection = self.chroma.get_or_create_collection("conversations")
        self.knowledge_collection = self.chroma.get_or_create_collection("knowledge_base")
        self.tasks_collection = self.chroma.get_or_create_collection("tasks")
    
    def generate_embedding(self, text):
        """Generate embeddings using the specified model via API"""
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        data = {
            "model": self.embedding_model,
            "input": text
        }
        
        response = requests.post(
            f"{self.api_base_url}/v1/embeddings",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"Error generating embeddings: {response.text}")
        
        return response.json()["data"][0]["embedding"]
    
    def store_conversation(self, query, response, metadata=None):
        """Store conversation with embeddings in both vector DB and SQL DB"""
        # Generate embedding for the conversation
        combined_text = f"Query: {query}\nResponse: {response}"
        embedding = self.generate_embedding(combined_text)
        
        # Create metadata if not provided
        if metadata is None:
            metadata = {}
        
        metadata["timestamp"] = datetime.utcnow().isoformat()
        metadata["type"] = "conversation"
        
        # Store in vector DB
        self.conversations_collection.add(
            ids=[f"conv_{datetime.utcnow().timestamp()}"],
            embeddings=[embedding],
            documents=[combined_text],
            metadatas=[metadata]
        )
        
        # Return the embedding for SQL storage
        return embedding
    
    def store_knowledge(self, question, answer, source=None, confidence=None):
        """Store knowledge base entry with embeddings"""
        # Generate embedding for the knowledge
        combined_text = f"Question: {question}\nAnswer: {answer}"
        embedding = self.generate_embedding(combined_text)
        
        # Create metadata
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "knowledge",
            "source": source,
            "confidence": confidence
        }
        
        # Store in vector DB
        self.knowledge_collection.add(
            ids=[f"know_{datetime.utcnow().timestamp()}"],
            embeddings=[embedding],
            documents=[combined_text],
            metadatas=[metadata]
        )
        
        # Return the embedding for SQL storage
        return embedding
    
    def store_task(self, description, priority=1):
        """Store task with embeddings"""
        # Generate embedding for the task
        embedding = self.generate_embedding(description)
        
        # Create metadata
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "task",
            "priority": priority,
            "status": "pending"
        }
        
        # Store in vector DB
        self.tasks_collection.add(
            ids=[f"task_{datetime.utcnow().timestamp()}"],
            embeddings=[embedding],
            documents=[description],
            metadatas=[metadata]
        )
        
        # Return the embedding for SQL storage
        return embedding
    
    def retrieve_context(self, query, n_results=5, include_metadata=True):
        """Retrieve relevant context based on query"""
        # Generate embedding for the query
        query_embedding = self.generate_embedding(query)
        
        # Search in conversations
        conv_results = self.conversations_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Search in knowledge base
        know_results = self.knowledge_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Search in tasks
        task_results = self.tasks_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Combine and format results
        results = []
        
        # Add conversation results
        for i in range(len(conv_results["ids"][0])):
            result = {
                "content": conv_results["documents"][0][i],
                "score": conv_results["distances"][0][i],
                "type": "conversation"
            }
            if include_metadata:
                result["metadata"] = conv_results["metadatas"][0][i]
            results.append(result)
        
        # Add knowledge results
        for i in range(len(know_results["ids"][0])):
            result = {
                "content": know_results["documents"][0][i],
                "score": know_results["distances"][0][i],
                "type": "knowledge"
            }
            if include_metadata:
                result["metadata"] = know_results["metadatas"][0][i]
            results.append(result)
        
        # Add task results
        for i in range(len(task_results["ids"][0])):
            result = {
                "content": task_results["documents"][0][i],
                "score": task_results["distances"][0][i],
                "type": "task"
            }
            if include_metadata:
                result["metadata"] = task_results["metadatas"][0][i]
            results.append(result)
        
        # Sort by score (lower is better)
        results.sort(key=lambda x: x["score"])
        
        # Return top n_results
        return results[:n_results]
    
    def format_context_for_prompt(self, context_results):
        """Format context results for inclusion in a prompt"""
        if not context_results:
            return "No relevant context found."
        
        formatted_context = "Relevant context:\n\n"
        
        for i, result in enumerate(context_results):
            formatted_context += f"[{i+1}] {result['type'].upper()}: {result['content']}\n\n"
        
        return formatted_context
    
    def augment_query(self, query):
        """Augment query with relevant context for the interpreter"""
        context_results = self.retrieve_context(query)
        formatted_context = self.format_context_for_prompt(context_results)
        
        return f"{formatted_context}\n\nUser query: {query}"
