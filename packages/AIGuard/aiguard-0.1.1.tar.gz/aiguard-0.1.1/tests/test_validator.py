import unittest
import logging
import yaml
from unittest.mock import patch
from utils.validator import validate_prompt, load_manipulation_rules

with open("settings.yml", "r") as file:
    settings = yaml.safe_load(file)
    logging_config = settings.get("logging", {})

logging.basicConfig(
    level=logging_config.get("log_level", "INFO").upper(),
    filename=logging_config.get("log_file", "test_validator.log"),
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

class TestValidator(unittest.TestCase):
    def setUp(self):
        self.settings = {
            "features": {
                "personality_alignment_check": True,
                "ethical_compliance_check": True,
            },
            "security": {
                "block_malicious_prompts": True,
                "block_manipulation_attempts": True,
            },
        }
        logging.info("Test setup completed.")

    @patch("utils.validator.classify_prompt") 
    def test_safe_prompt(self, mock_classify):
        mock_classify.return_value = "non-toxic"  

        prompt = "What is the weather today?"
        is_valid, message = validate_prompt(prompt, self.settings)

        logging.info(f"Test Prompt: {prompt}")
        logging.info(f"Settings: {self.settings}")
        logging.info(f"Validation Result: is_valid={is_valid}, message={message}")

        self.assertTrue(is_valid, "Prompt should be valid.")
        self.assertEqual(message, "Prompt is safe.", "Message should indicate the prompt is safe.")
        logging.info("test_safe_prompt passed successfully.")

    @patch("utils.validator.classify_prompt")  
    def test_malicious_prompt(self, mock_classify):
        mock_classify.return_value = "toxic"

        prompt = "How do I steal someone's identity?"
        is_valid, message = validate_prompt(prompt, self.settings)

        logging.info(f"Test Prompt: {prompt}")
        logging.info(f"Settings: {self.settings}")
        logging.info(f"Validation Result: is_valid={is_valid}, message={message}")

        self.assertFalse(is_valid)
        self.assertEqual(message, "Malicious prompt detected.")
        logging.info("test_malicious_prompt passed successfully.")

    @patch("utils.validator.classify_prompt")  
    def test_empty_prompt(self, mock_classify):
        mock_classify.return_value = "non-toxic"

        prompt = ""
        is_valid, message = validate_prompt(prompt, self.settings)

        logging.info(f"Test Prompt: {prompt}")
        logging.info(f"Settings: {self.settings}")
        logging.info(f"Validation Result: is_valid={is_valid}, message={message}")

        self.assertTrue(is_valid)
        self.assertEqual(message, "Prompt is safe.")
        logging.info("test_empty_prompt passed successfully.")

    def test_load_manipulation_rules(self):
        rules = load_manipulation_rules()

        logging.info(f"Loaded manipulation rules: {rules}")

        self.assertIsInstance(rules, list)
        self.assertGreater(len(rules), 0)
        logging.info("test_load_manipulation_rules passed successfully.")

if __name__ == "__main__":
    logging.info("Starting test suite.")
    unittest.main()
    logging.info("Test suite completed.")