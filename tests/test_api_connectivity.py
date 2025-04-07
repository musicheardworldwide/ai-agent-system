"""
Test API connectivity with lastwinnersllc.com
"""
import os
import sys
import unittest
import requests
import json

# Add parent directory to path to import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestAPIConnectivity(unittest.TestCase):
    """Test API connectivity with lastwinnersllc.com"""
    
    def setUp(self):
        """Set up test environment"""
        self.api_base_url = os.environ.get('API_BASE_URL', 'https://api.lastwinnersllc.com')
        self.api_key = os.environ.get('API_KEY', '')
        
        # Skip tests if API key is not set
        if not self.api_key:
            self.skipTest("API_KEY environment variable not set")
    
    def test_api_connectivity(self):
        """Test basic API connectivity"""
        response = requests.get(f"{self.api_base_url}/health")
        self.assertEqual(response.status_code, 200)
    
    def test_llama_model_availability(self):
        """Test llama3.2 model availability"""
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        data = {
            "model": "llama3.2",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, are you available?"}
            ]
        }
        
        response = requests.post(
            f"{self.api_base_url}/chat/completions",
            headers=headers,
            json=data
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('choices', response_data)
        self.assertTrue(len(response_data['choices']) > 0)
    
    def test_embedding_model_availability(self):
        """Test nomic-embed-text model availability"""
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        data = {
            "model": "nomic-embed-text",
            "input": "This is a test sentence for embedding."
        }
        
        response = requests.post(
            f"{self.api_base_url}/embeddings",
            headers=headers,
            json=data
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('data', response_data)
        self.assertTrue(len(response_data['data']) > 0)
        self.assertIn('embedding', response_data['data'][0])
        
        # Check that we get a proper embedding vector
        embedding = response_data['data'][0]['embedding']
        self.assertIsInstance(embedding, list)
        self.assertTrue(len(embedding) > 0)

if __name__ == '__main__':
    unittest.main()
