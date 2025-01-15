# tests/test_model.py
import unittest
from mytextlib import analyze_text

class TestMyTextLib(unittest.TestCase):
    def test_analyze_text(self):
        text = "This is a great product!"
        result = analyze_text(text, model_dir="./model_files")
        self.assertTrue(isinstance(result, list))
        self.assertTrue("label" in result[0])
        #self.assertIn(result[0]["label"], ["positive", "negative", "neutral"])  # Adjust as per your model's labels


if __name__ == "__main__":
    unittest.main()