import unittest
from fckafde_shortener import shorten_url, de_shorten_url, generate_forward_url

class TestFckafdeShortener(unittest.TestCase):
    def test_shorten_url(self):
        # Replace with a mock server or a valid test case
        result = shorten_url("https://example.com")
        self.assertIsNotNone(result)

    def test_de_shorten_url(self):
        # Replace with a valid test case or mock response
        result = de_shorten_url("https://fckaf.de/Xkp")
        self.assertIsNotNone(result)

    def test_generate_forward_url(self):
        # Replace with appropriate test cases
        forward_url = generate_forward_url("https://fckaf.de/Xkp", "info")
        self.assertIsNotNone(forward_url)
        self.assertIn("?info=", forward_url)

if __name__ == "__main__":
    unittest.main()
