import unittest
from lumbni_client.client import LumbniClient
from lumbni_client.exceptions import LumbniApiError

class TestLumbniClient(unittest.TestCase):

    def setUp(self):
        self.client = LumbniClient(api_key="YOUR_API_KEY")

    def test_generate_text(self):
        response = self.client.generate_text(prompt="Tell me a joke.")
        self.assertIn('data', response)
        self.assertEqual(response['status'], 'success')

    def test_invalid_api_key(self):
        client = LumbniClient(api_key="INVALID_API_KEY")
        with self.assertRaises(LumbniApiError):
            client.generate_text(prompt="Tell me a joke.")