from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

class GmailWebhookTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('gmail-webhook')

    def test_gmail_webhook_valid(self):
        payload = {
            "sender": "test@example.com",
            "subject": "Let's schedule a meeting",
            "body": "Are you free next week?",
            "to": ["me@example.com"],
            "cc": [],
            "time": "2025-06-01T00:00:00Z"
        }
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('decision', response.data)

    def test_email_receipt_triggers_agent_flow(self):
        """Test that posting a valid email triggers the agent and returns a structured decision."""
        payload = {
            "sender": "test@example.com",
            "subject": "Schedule a meeting",
            "body": "Let's meet tomorrow at 10am.",
            "to": ["fraya@ai.com"],
            "cc": [],
            "time": "2025-06-01T12:00:00Z"
        }
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('decision', response.data)
        self.assertIn('intent', response.data['decision'])
        self.assertIn('entities', response.data['decision'])

    def test_gmail_webhook_invalid(self):
        payload = {
            "sender": "test@example.com",
            "subject": "Missing required fields"
            # Missing 'body', 'to', 'time'
        }
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
