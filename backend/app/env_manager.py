"""
Environment functions for API/secrets management for the AI Agent System
"""
import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .models import EnvironmentVariable

class EnvironmentManager:
    """
    Environment manager that handles API keys, secrets, and environment variables.
    This component provides secure storage and access to sensitive information.
    """
    
    def __init__(self, db_session=None, master_key=None):
        """Initialize the environment manager"""
        self.db_session = db_session
        self.env_cache = {}
        self.master_key = master_key or os.environ.get('MASTER_KEY', 'default-dev-key-not-for-production')
        self.cipher_suite = self._initialize_encryption()
        self.load_env_from_db()
    
    def _initialize_encryption(self):
        """Initialize encryption for secrets"""
        # Generate a key from the master key
        salt = b'ai_agent_system_salt'  # In production, this should be stored securely
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)
    
    def load_env_from_db(self):
        """Load environment variables from the database"""
        if not self.db_session:
            return
        
        env_vars = self.db_session.query(EnvironmentVariable).all()
        for var in env_vars:
            if var.is_secret:
                # Decrypt secret values
                try:
                    decrypted_value = self.decrypt_value(var.value)
                    self.env_cache[var.key] = decrypted_value
                except Exception:
                    # If decryption fails, store as is (might be unencrypted)
                    self.env_cache[var.key] = var.value
            else:
                self.env_cache[var.key] = var.value
    
    def encrypt_value(self, value):
        """
        Encrypt a value
        
        Args:
            value (str): Value to encrypt
            
        Returns:
            str: Encrypted value
        """
        return self.cipher_suite.encrypt(value.encode()).decode()
    
    def decrypt_value(self, encrypted_value):
        """
        Decrypt a value
        
        Args:
            encrypted_value (str): Encrypted value
            
        Returns:
            str: Decrypted value
        """
        return self.cipher_suite.decrypt(encrypted_value.encode()).decode()
    
    def get_env(self, key, default=None):
        """
        Get an environment variable
        
        Args:
            key (str): Environment variable key
            default: Default value if not found
            
        Returns:
            str: Environment variable value or default
        """
        # Check cache first
        if key in self.env_cache:
            return self.env_cache[key]
        
        # Check database if available
        if self.db_session:
            env_var = self.db_session.query(EnvironmentVariable).filter_by(key=key).first()
            
            if env_var:
                value = env_var.value
                
                # Decrypt if secret
                if env_var.is_secret:
                    try:
                        value = self.decrypt_value(value)
                    except Exception:
                        # If decryption fails, use as is
                        pass
                
                # Cache for future use
                self.env_cache[key] = value
                return value
        
        # Check system environment variables
        if key in os.environ:
            self.env_cache[key] = os.environ[key]
            return os.environ[key]
        
        return default
    
    def set_env(self, key, value, is_secret=False):
        """
        Set an environment variable
        
        Args:
            key (str): Environment variable key
            value (str): Environment variable value
            is_secret (bool): Whether the variable is secret
            
        Returns:
            dict: Status
        """
        # Encrypt if secret
        stored_value = value
        if is_secret:
            stored_value = self.encrypt_value(value)
        
        # Update cache
        self.env_cache[key] = value
        
        # Store in database if available
        if self.db_session:
            try:
                # Check if variable exists
                env_var = self.db_session.query(EnvironmentVariable).filter_by(key=key).first()
                
                if env_var:
                    # Update existing variable
                    env_var.value = stored_value
                    env_var.is_secret = is_secret
                else:
                    # Create new variable
                    env_var = EnvironmentVariable(
                        key=key,
                        value=stored_value,
                        is_secret=is_secret
                    )
                    self.db_session.add(env_var)
                
                self.db_session.commit()
                
                return {"success": True, "message": "Environment variable set successfully"}
            
            except Exception as e:
                self.db_session.rollback()
                return {"success": False, "error": str(e)}
        
        return {"success": True, "message": "Environment variable set in memory only"}
    
    def delete_env(self, key):
        """
        Delete an environment variable
        
        Args:
            key (str): Environment variable key
            
        Returns:
            dict: Status
        """
        # Remove from cache
        if key in self.env_cache:
            del self.env_cache[key]
        
        # Remove from database if available
        if self.db_session:
            try:
                env_var = self.db_session.query(EnvironmentVariable).filter_by(key=key).first()
                
                if env_var:
                    self.db_session.delete(env_var)
                    self.db_session.commit()
                    
                    return {"success": True, "message": "Environment variable deleted successfully"}
                
                return {"success": False, "error": "Environment variable not found"}
            
            except Exception as e:
                self.db_session.rollback()
                return {"success": False, "error": str(e)}
        
        return {"success": True, "message": "Environment variable deleted from memory only"}
    
    def list_env(self, include_secrets=False):
        """
        List all environment variables
        
        Args:
            include_secrets (bool): Whether to include secret values
            
        Returns:
            dict: Environment variables
        """
        result = {}
        
        # Get from database if available
        if self.db_session:
            env_vars = self.db_session.query(EnvironmentVariable).all()
            
            for var in env_vars:
                if var.is_secret and not include_secrets:
                    result[var.key] = "********"
                else:
                    value = var.value
                    
                    # Decrypt if secret and include_secrets is True
                    if var.is_secret and include_secrets:
                        try:
                            value = self.decrypt_value(value)
                        except Exception:
                            # If decryption fails, use as is
                            pass
                    
                    result[var.key] = value
        else:
            # Use cache if no database
            for key, value in self.env_cache.items():
                result[key] = value
        
        return result
    
    def get_api_key(self, service_name, default=None):
        """
        Get an API key for a specific service
        
        Args:
            service_name (str): Service name
            default: Default value if not found
            
        Returns:
            str: API key or default
        """
        # Try service-specific naming conventions
        key_formats = [
            f"{service_name.upper()}_API_KEY",
            f"{service_name.upper()}_KEY",
            f"{service_name}_api_key",
            f"{service_name}_key",
            service_name
        ]
        
        for key_format in key_formats:
            api_key = self.get_env(key_format)
            if api_key:
                return api_key
        
        return default
    
    def configure_api_credentials(self, service_name, credentials):
        """
        Configure API credentials for a service
        
        Args:
            service_name (str): Service name
            credentials (dict): Credentials dictionary
            
        Returns:
            dict: Status
        """
        results = {}
        
        for key, value in credentials.items():
            env_key = f"{service_name.upper()}_{key.upper()}"
            result = self.set_env(env_key, value, is_secret=True)
            results[env_key] = result
        
        return {
            "success": all(result.get("success", False) for result in results.values()),
            "results": results
        }
    
    def export_env_to_dotenv(self, file_path=".env", include_secrets=True):
        """
        Export environment variables to a .env file
        
        Args:
            file_path (str): Path to .env file
            include_secrets (bool): Whether to include secrets
            
        Returns:
            dict: Status
        """
        try:
            env_vars = self.list_env(include_secrets=include_secrets)
            
            with open(file_path, "w") as f:
                for key, value in env_vars.items():
                    # Skip masked secret values
                    if value == "********":
                        continue
                    
                    # Escape special characters
                    value = value.replace("\"", "\\\"")
                    
                    # Write to file
                    f.write(f'{key}="{value}"\n')
            
            return {"success": True, "message": f"Environment variables exported to {file_path}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def import_env_from_dotenv(self, file_path=".env"):
        """
        Import environment variables from a .env file
        
        Args:
            file_path (str): Path to .env file
            
        Returns:
            dict: Status
        """
        try:
            if not os.path.exists(file_path):
                return {"success": False, "error": f"File not found: {file_path}"}
            
            imported = 0
            
            with open(file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith("#"):
                        continue
                    
                    # Parse key-value pair
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        
                        # Set environment variable
                        self.set_env(key, value)
                        imported += 1
            
            return {"success": True, "message": f"Imported {imported} environment variables"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
