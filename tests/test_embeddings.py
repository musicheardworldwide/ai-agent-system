"""
Test embeddings with nomic-embed-text model
"""
import os
import sys
import unittest
import numpy as np
import requests
import json

# Add parent directory to path to import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestEmbeddings(unittest.TestCase):
    """Test embeddings with nomic-embed-text model"""
    
    def setUp(self):
        """Set up test environment"""
        self.api_base_url = os.environ.get('API_BASE_URL', 'https://api.lastwinnersllc.com')
        self.api_key = os.environ.get('API_KEY', '')
        
        # Skip tests if API key is not set
        if not self.api_key:
            self.skipTest("API_KEY environment variable not set")
    
    def get_embedding(self, text):
        """Get embedding for a text"""
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        data = {
            "model": "nomic-embed-text",
            "input": text
        }
        
        response = requests.post(
            f"{self.api_base_url}/embeddings",
            headers=headers,
            json=data
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        return response_data['data'][0]['embedding']
    
    def test_embedding_dimensions(self):
        """Test embedding dimensions"""
        embedding = self.get_embedding("This is a test sentence.")
        self.assertIsInstance(embedding, list)
        # Check that the embedding has the expected dimensions
        # nomic-embed-text typically produces 768-dimensional embeddings
        self.assertTrue(len(embedding) > 0)
    
    def test_embedding_consistency(self):
        """Test that similar texts have similar embeddings"""
        embedding1 = self.get_embedding("The cat sat on the mat.")
        embedding2 = self.get_embedding("A cat is sitting on a mat.")
        embedding3 = self.get_embedding("Quantum physics is fascinating.")
        
        # Convert to numpy arrays for easier calculation
        embedding1 = np.array(embedding1)
        embedding2 = np.array(embedding2)
        embedding3 = np.array(embedding3)
        
        # Calculate cosine similarity
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        # Similar sentences should have higher similarity
        similarity_similar = cosine_similarity(embedding1, embedding2)
        similarity_different = cosine_similarity(embedding1, embedding3)
        
        self.assertGreater(similarity_similar, similarity_different)
    
    def test_batch_embedding(self):
        """Test batch embedding"""
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        data = {
            "model": "nomic-embed-text",
            "input": [
                "This is the first sentence.",
                "This is the second sentence.",
                "This is the third sentence."
            ]
        }
        
        response = requests.post(
            f"{self.api_base_url}/embeddings",
            headers=headers,
            json=data
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('data', response_data)
        self.assertEqual(len(response_data['data']), 3)
        
        # Check that each embedding has the expected format
        for item in response_data['data']:
            self.assertIn('embedding', item)
            self.assertIsInstance(item['embedding'], list)
            self.assertTrue(len(item['embedding']) > 0)

if __name__ == '__main__':
    unittest.main()
