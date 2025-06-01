from django.shortcuts import render
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
import jsonschema
from jsonschema import validate, ValidationError
from agents.email_analyzer_agent import EmailAnalyzerAgent

logger = logging.getLogger(__name__)

from .models import User, Preference

class PreferencesView(APIView):
    """
    GET: Return or create user preferences.
    POST: Update or create user preferences.
    """
    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id') or request.data.get('user_id')
        if not user_id:
            return Response({'error': 'Missing user_id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            # Try to get email from request, fallback to blank
            email = request.GET.get('email') or request.data.get('email') or ''
            user = User.objects.create(id=user_id, email=email)
        # Always create default preferences if missing
        pref, created = Preference.objects.get_or_create(user=user, defaults={
            'preferred_days': [],
            'preferred_times': '',
            'buffer_minutes': 15,
            'tone': 'professional',
            'style': 'concise',
        })
        data = {
            'preferred_days': pref.preferred_days or [],
            'preferred_times': pref.preferred_times or '',
            'buffer_minutes': pref.buffer_minutes or 15,
            'tone': pref.tone or 'professional',
            'style': pref.style or 'concise',
        }
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'Missing user_id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        pref, _ = Preference.objects.get_or_create(user=user)
        # Sanitize array fields: convert empty string to empty list
        preferred_days = request.data.get('preferred_days', pref.preferred_days)
        if preferred_days == '':
            preferred_days = []
        pref.preferred_days = preferred_days
        preferred_times = request.data.get('preferred_times', pref.preferred_times)
        if preferred_times == '':
            preferred_times = []
        pref.preferred_times = preferred_times
        pref.buffer_minutes = request.data.get('buffer_minutes', pref.buffer_minutes)
        pref.tone = request.data.get('tone', pref.tone)
        pref.style = request.data.get('style', pref.style)
        pref.save()
        data = {
            'preferred_days': pref.preferred_days or [],
            'preferred_times': pref.preferred_times or [],
            'buffer_minutes': pref.buffer_minutes or 15,
            'tone': pref.tone or 'professional',
            'style': pref.style or 'concise',
        }
        return Response(data, status=status.HTTP_200_OK)

from .models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json

@method_decorator(csrf_exempt, name='dispatch')
class StoreGoogleTokenView(APIView):
    """
    Receives user_id and refresh_token, updates User.google_refresh_token.
    """
    def post(self, request, *args, **kwargs):
        import uuid
        data = request.data
        user_id = data.get('user_id')
        refresh_token = data.get('refresh_token')
        if not user_id or not refresh_token:
            logger.error(f"Missing user_id or refresh_token: {data}")
            return Response({'error': 'Missing user_id or refresh_token'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_uuid = uuid.UUID(user_id)
        except Exception as e:
            logger.error(f"Invalid user_id format: {user_id} ({e})")
            return Response({'error': 'Invalid user_id format'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_uuid)
            user.google_refresh_token = refresh_token
            user.save()
            return Response({'status': 'refresh_token stored'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # Try to get email if provided
            email = data.get('email', None)
            try:
                user = User.objects.create(id=user_uuid, email=email, google_refresh_token=refresh_token)
                return Response({'status': 'new user created and refresh_token stored'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.exception(f"Error creating new user {user_id}: {e}")
                return Response({'error': 'Internal server error (user creation)'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.exception(f"Error saving refresh token for user {user_id}: {e}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class GmailWebhookView(APIView):
    """
    Receives Gmail webhook events, parses and passes email JSON to CrewAI agent.
    """
    def post(self, request, *args, **kwargs):
        # Parse Gmail webhook payload
        email_event = request.data
        logger.info(f"Received Gmail webhook event: {email_event}")
        email_json = {
            'sender': email_event.get('sender'),
            'subject': email_event.get('subject'),
            'body': email_event.get('body'),
            'to': email_event.get('to'),
            'cc': email_event.get('cc'),
            'time': email_event.get('time'),
        }
        # Email event schema for validation
        EMAIL_EVENT_SCHEMA = {
            "type": "object",
            "properties": {
                "sender": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "to": {"type": ["string", "array"]},
                "cc": {"type": ["string", "array", "null"]},
                "time": {"type": "string"},
            },
            "required": ["sender", "subject", "body", "to", "time"],
        }
        try:
            validate(instance=email_json, schema=EMAIL_EVENT_SCHEMA)
        except ValidationError as e:
            logger.error(f"Malformed email event: {e.message}")
            return Response({"error": f"Malformed email event: {e.message}"}, status=status.HTTP_400_BAD_REQUEST)
        # --- CrewAI Integration ---
        try:
            user = User.objects.get(email=email_json['sender'])
        except User.DoesNotExist:
            user = User.objects.create(email=email_json['sender'])
        try:
            pref = Preference.objects.get(user=user)
        except Preference.DoesNotExist:
            pref, created = Preference.objects.get_or_create(user=user, defaults={
                'preferred_days': [],
                'preferred_times': [],
                'buffer_minutes': 15,
                'tone': 'professional',
                'style': 'concise',
            })
        preferences = {
            'name': user.email,
            'preferred_days': pref.preferred_days or [],
            'preferred_times': pref.preferred_times or [],
            'buffer_minutes': pref.buffer_minutes or 15,
            'tone': pref.tone or 'professional',
            'style': pref.style or 'concise',
        }
        # Call EmailAnalyzerAgent with validated email_json
        try:
            agent = EmailAnalyzerAgent(preferences)
            logger.info(f"Passing email to EmailAnalyzerAgent: {email_json}")
            decision = agent.analyze(email_json)
            logger.info(f"Agent decision: {decision}")
            return Response({'status': 'processed', 'decision': decision}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Agent processing error")
            return Response({'error': f'Agent processing error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# End of GmailWebhookView

class CalendarEventsView(APIView):
    """
    GET: Return a mock list of Google Calendar events for the user.
    """
    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id')
        if not user_id:
            return Response({'error': 'Missing user_id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        # In production, use user.google_refresh_token to fetch real events
        events = [
            {"summary": "Meeting with Bob", "start": "2025-06-01T10:00:00Z", "end": "2025-06-01T11:00:00Z"}
        ]
        return Response({"events": events}, status=status.HTTP_200_OK)

class SendEmailView(APIView):
    """
    POST: Send an email (mocked). Requires user_id, to, subject, body.
    """
    def post(self, request, *args, **kwargs):
        data = request.data
        user_id = data.get('user_id')
        to = data.get('to')
        subject = data.get('subject')
        body = data.get('body')
        if not user_id or not to or not subject or not body:
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        # In production, use user.google_refresh_token to send via Gmail API
        logger.info(f"[MOCK SEND EMAIL] to={to}, subject={subject}, body={body}, user_id={user_id}")
        return Response({
            'status': 'sent',
            'to': to,
            'subject': subject,
            'body': body,
            'user_id': user_id
        }, status=status.HTTP_200_OK)
