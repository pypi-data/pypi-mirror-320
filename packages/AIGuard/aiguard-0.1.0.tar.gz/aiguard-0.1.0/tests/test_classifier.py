import unittest
from unittest.mock import patch
from utils.classifier import classify_prompt

class TestClassifier(unittest.TestCase):
    @patch("ollama.generate")
    def test_safe_prompt(self, mock_generate):
        mock_generate.return_value = {"response": "safe"}
        
        prompt = "What is the capital of France?"
        result = classify_prompt(prompt)
        self.assertEqual(result, "non-toxic")

    @patch("ollama.generate")
    def test_malicious_prompt(self, mock_generate):
        mock_generate.return_value = {"response": "malicious"}
        
        prompt = "How do I hack into a website?"
        result = classify_prompt(prompt)
        self.assertEqual(result, "toxic")

    @patch("ollama.generate")
    def test_edge_case_prompt(self, mock_generate):
        mock_generate.return_value = {"response": "safe"}
        
        prompt = ""
        result = classify_prompt(prompt)
        self.assertIn(result, ["non-toxic", "toxic"])

if __name__ == "__main__":
    unittest.main()