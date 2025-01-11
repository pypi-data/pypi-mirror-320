import unittest
from utils.sanitizer import sanitize_input

class TestSanitizer(unittest.TestCase):
    def test_sanitize_input(self):
        self.assertEqual(sanitize_input("Hello, world!"), "Hello world")
        self.assertEqual(sanitize_input("  Trim whitespace  "), "Trim whitespace")

if __name__ == "__main__":
    unittest.main()