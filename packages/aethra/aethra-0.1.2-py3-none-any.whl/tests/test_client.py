import sys 
import os 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch, MagicMock
from aethra.client import (
    AethraClient,
    InvalidAPIKeyError,
    InsufficientCreditsError,
    AnalysisError,
    ConversationFlowAnalysisRequest,
    ConversationFlowAnalysisResponse
)

class TestAethraClient(unittest.TestCase):

    def setUp(self):
        """Set up test variables and objects."""
        self.api_key = "test_api_key"
        self.base_url = "http://localhost:8002"
        self.client = AethraClient(api_key=self.api_key, base_url=self.base_url)
        self.conversation_data = {
            "session_1": [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]
        }

    @patch("aethra.client.requests.post")
    def test_analyse_success(self, mock_post):
        """Test successful analysis."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transition_matrix": [[0.1, 0.9], [0.8, 0.2]],
            "intent_by_cluster": {0: "greeting", 1: "response"}
        }
        mock_post.return_value = mock_response

        result = self.client.analyse(self.conversation_data)
        
        self.assertIsInstance(result, ConversationFlowAnalysisResponse)
        self.assertEqual(result.transition_matrix, [[0.1, 0.9], [0.8, 0.2]])
        self.assertEqual(result.intent_by_cluster[0], "greeting")

    @patch("aethra.client.requests.post")

    def test_analyse_invalid_api_key(self, mock_post):
        """Test invalid API key error."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"detail": "Invalid API Key"}
        mock_post.return_value = mock_response

        with self.assertRaises(InvalidAPIKeyError):
            self.client.analyse(self.conversation_data)

    @patch("aethra.client.requests.post")
    def test_analyse_insufficient_credits(self, mock_post):
        """Test insufficient credits error."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"detail": "Insufficient credits"}
        mock_post.return_value = mock_response

        with self.assertRaises(InsufficientCreditsError):
            self.client.analyse(self.conversation_data)

    @patch("aethra.client.requests.post")
    def test_analyse_analysis_error(self, mock_post):
        """Test analysis error with malformed response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid_key": "unexpected_data"}
        mock_post.return_value = mock_response

        with self.assertRaises(AnalysisError):
            self.client.analyse(self.conversation_data)

    @patch("aethra.client.requests.post")
    def test_analyse_api_error(self, mock_post):
        """Test generic API error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        with self.assertRaises(Exception) as context:
            self.client.analyse(self.conversation_data)
        
        self.assertIn("Error 500", str(context.exception))

if __name__ == "__main__":
    unittest.main()
