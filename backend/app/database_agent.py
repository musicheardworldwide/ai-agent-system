"""
Database agent for the AI Agent System
"""
import json
import sqlalchemy
from sqlalchemy import text
from .models import Conversation, Tool, Task, KnowledgeBase, EnvironmentVariable

class DatabaseAgent:
    """
    Database agent that provides an interface for the interpreter to interact with the database.
    This agent handles database operations, schema management, and knowledge base construction.
    """
    
    def __init__(self, db_session=None):
        """Initialize the database agent"""
        self.db_session = db_session
    
    def execute_query(self, query, params=None, read_only=True):
        """
        Execute a SQL query against the database
        
        Args:
            query (str): SQL query to execute
            params (dict, optional): Parameters for the query
            read_only (bool): Whether the query is read-only (SELECT)
            
        Returns:
            dict: Query results or status
        """
        try:
            # Check if query is read-only if required
            if read_only:
                query_lower = query.lower().strip()
                if not query_lower.startswith(('select', 'with')):
                    return {"error": "Only read-only queries are allowed in read_only mode"}
            
            # Execute query
            if params:
                result = self.db_session.execute(text(query), params)
            else:
                result = self.db_session.execute(text(query))
            
            # If query modifies data, commit changes
            if not read_only:
                self.db_session.commit()
                return {"status": "Query executed successfully"}
            
            # For read-only queries, return results
            columns = result.keys()
            rows = []
            
            for row in result:
                rows.append({column: value for column, value in zip(columns, row)})
            
            return {"results": rows, "count": len(rows)}
        
        except Exception as e:
            # Rollback transaction on error
            self.db_session.rollback()
            return {"error": str(e)}
    
    def get_schema(self):
        """
        Get the database schema
        
        Returns:
            dict: Database schema information
        """
        try:
            # Get table information
            tables = {}
            
            # Get all tables
            inspector = sqlalchemy.inspect(self.db_session.bind)
            
            for table_name in inspector.get_table_names():
                columns = []
                
                # Get columns for each table
                for column in inspector.get_columns(table_name):
                    columns.append({
                        "name": column["name"],
                        "type": str(column["type"]),
                        "nullable": column["nullable"],
                        "default": str(column["default"]) if column["default"] else None
                    })
                
                # Get primary key
                pk = inspector.get_pk_constraint(table_name)
                
                # Get foreign keys
                fks = []
                for fk in inspector.get_foreign_keys(table_name):
                    fks.append({
                        "constrained_columns": fk["constrained_columns"],
                        "referred_table": fk["referred_table"],
                        "referred_columns": fk["referred_columns"]
                    })
                
                # Add table info
                tables[table_name] = {
                    "columns": columns,
                    "primary_key": pk["constrained_columns"] if pk else [],
                    "foreign_keys": fks
                }
            
            return {"tables": tables}
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_table_data(self, table_name, limit=100, offset=0):
        """
        Get data from a table
        
        Args:
            table_name (str): Name of the table
            limit (int): Maximum number of rows to return
            offset (int): Offset for pagination
            
        Returns:
            dict: Table data
        """
        try:
            query = f"SELECT * FROM {table_name} LIMIT :limit OFFSET :offset"
            params = {"limit": limit, "offset": offset}
            
            return self.execute_query(query, params)
        
        except Exception as e:
            return {"error": str(e)}
    
    def create_knowledge_entry(self, question, answer, source=None, confidence=None):
        """
        Create a new knowledge base entry
        
        Args:
            question (str): Question for the knowledge entry
            answer (str): Answer for the knowledge entry
            source (str, optional): Source of the knowledge
            confidence (int, optional): Confidence score (0-100)
            
        Returns:
            dict: Status and entry ID
        """
        try:
            # Create new entry
            entry = KnowledgeBase(
                question=question,
                answer=answer,
                source=source,
                confidence=confidence
            )
            
            self.db_session.add(entry)
            self.db_session.commit()
            
            return {"status": "Knowledge entry created successfully", "entry_id": entry.id}
        
        except Exception as e:
            self.db_session.rollback()
            return {"error": str(e)}
    
    def extract_qa_pairs(self, conversation_id=None, limit=10):
        """
        Extract question-answer pairs from conversations to build knowledge base
        
        Args:
            conversation_id (int, optional): Specific conversation ID to extract from
            limit (int): Maximum number of conversations to process
            
        Returns:
            dict: Extracted QA pairs and status
        """
        try:
            # Query conversations
            if conversation_id:
                conversations = self.db_session.query(Conversation).filter_by(id=conversation_id).all()
            else:
                conversations = self.db_session.query(Conversation).order_by(
                    Conversation.created_at.desc()
                ).limit(limit).all()
            
            qa_pairs = []
            
            for conv in conversations:
                # Extract question from query
                question = conv.query.strip()
                
                # Extract answer from response
                answer = conv.response.strip()
                
                # Skip if either is empty
                if not question or not answer:
                    continue
                
                # Add to QA pairs
                qa_pairs.append({
                    "question": question,
                    "answer": answer,
                    "conversation_id": conv.id,
                    "timestamp": conv.created_at.isoformat()
                })
            
            return {"qa_pairs": qa_pairs, "count": len(qa_pairs)}
        
        except Exception as e:
            return {"error": str(e)}
    
    def build_knowledge_base(self, conversation_limit=50, confidence=70):
        """
        Build knowledge base from conversations
        
        Args:
            conversation_limit (int): Maximum number of conversations to process
            confidence (int): Confidence score to assign (0-100)
            
        Returns:
            dict: Status and count of entries created
        """
        try:
            # Extract QA pairs
            result = self.extract_qa_pairs(limit=conversation_limit)
            
            if "error" in result:
                return result
            
            qa_pairs = result["qa_pairs"]
            created_count = 0
            
            # Create knowledge entries
            for qa in qa_pairs:
                # Check if similar question already exists
                existing = self.db_session.query(KnowledgeBase).filter_by(
                    question=qa["question"]
                ).first()
                
                if existing:
                    continue
                
                # Create new entry
                entry = KnowledgeBase(
                    question=qa["question"],
                    answer=qa["answer"],
                    source=f"Conversation #{qa['conversation_id']}",
                    confidence=confidence
                )
                
                self.db_session.add(entry)
                created_count += 1
            
            self.db_session.commit()
            
            return {
                "status": "Knowledge base built successfully",
                "entries_created": created_count,
                "total_qa_pairs": len(qa_pairs)
            }
        
        except Exception as e:
            self.db_session.rollback()
            return {"error": str(e)}
    
    def get_environment_variable(self, key, default=None):
        """
        Get an environment variable
        
        Args:
            key (str): Environment variable key
            default: Default value if not found
            
        Returns:
            str: Environment variable value or default
        """
        try:
            env_var = self.db_session.query(EnvironmentVariable).filter_by(key=key).first()
            
            if env_var:
                return env_var.value
            
            return default
        
        except Exception as e:
            return default
    
    def set_environment_variable(self, key, value, is_secret=False):
        """
        Set an environment variable
        
        Args:
            key (str): Environment variable key
            value (str): Environment variable value
            is_secret (bool): Whether the variable is secret
            
        Returns:
            dict: Status
        """
        try:
            # Check if variable exists
            env_var = self.db_session.query(EnvironmentVariable).filter_by(key=key).first()
            
            if env_var:
                # Update existing variable
                env_var.value = value
                env_var.is_secret = is_secret
            else:
                # Create new variable
                env_var = EnvironmentVariable(
                    key=key,
                    value=value,
                    is_secret=is_secret
                )
                self.db_session.add(env_var)
            
            self.db_session.commit()
            
            return {"status": "Environment variable set successfully"}
        
        except Exception as e:
            self.db_session.rollback()
            return {"error": str(e)}
    
    def generate_database_report(self):
        """
        Generate a report on database statistics
        
        Returns:
            dict: Database statistics
        """
        try:
            stats = {}
            
            # Count records in each table
            stats["conversations"] = self.db_session.query(Conversation).count()
            stats["tools"] = self.db_session.query(Tool).count()
            stats["tasks"] = self.db_session.query(Task).count()
            stats["knowledge_entries"] = self.db_session.query(KnowledgeBase).count()
            stats["environment_variables"] = self.db_session.query(EnvironmentVariable).count()
            
            # Get task statistics
            task_stats = {}
            task_stats["pending"] = self.db_session.query(Task).filter_by(status="pending").count()
            task_stats["completed"] = self.db_session.query(Task).filter_by(status="completed").count()
            stats["task_stats"] = task_stats
            
            # Get recent activity
            recent_conversations = self.db_session.query(Conversation).order_by(
                Conversation.created_at.desc()
            ).limit(5).all()
            
            stats["recent_activity"] = [
                {
                    "type": "conversation",
                    "id": conv.id,
                    "query": conv.query,
                    "timestamp": conv.created_at.isoformat()
                }
                for conv in recent_conversations
            ]
            
            return stats
        
        except Exception as e:
            return {"error": str(e)}
