import unittest
from flask import Flask, request, Response
from webhook.voice_agent import app

class WebhookTestCase(unittest.TestCase):
    def setUp(self):
        # Set up the Flask test client
        self.app = app.test_client()
        self.app.testing = True

    def test_webhook(self):
        # Simulate a POST request to the /webhook endpoint
        response = self.app.post("/webhook", data={
            "From": "+1234567890",
            "To": "+0987654321",
            "CallSid": "CA1234567890abcdef"
        })

        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/xml")
        self.assertIn("<Response></Response>", response.data.decode())

if __name__ == "__main__":
    unittest.main()