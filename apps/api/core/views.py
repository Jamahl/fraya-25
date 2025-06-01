from django.shortcuts import render
from django.db import models

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

logger = logging.getLogger(__name__)

# Create your views here.

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
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        pref, _ = Preference.objects.get_or_create(user=user)
        data = {
            'preferred_days': pref.preferred_days or [],
            'preferred_times': pref.preferred_times or [],
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
        pref.preferred_days = request.data.get('preferred_days', pref.preferred_days)
        pref.preferred_times = request.data.get('preferred_times', pref.preferred_times)
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
        # Example: parse Gmail Pub/Sub payload
        email_event = request.data
        # TODO: Add actual Gmail event parsing logic
        # For now, just log and echo
        logger.info(f"Received Gmail webhook event: {email_event}")
        # Convert to JSON structure expected by CrewAI
        email_json = {
            'sender': email_event.get('sender'),
            'subject': email_event.get('subject'),
            'body': email_event.get('body'),
            'to': email_event.get('to'),
            'cc': email_event.get('cc'),
            'time': email_event.get('time'),
        }
        # Stub call to CrewAI agent
        # from .crew_agents import EmailAnalyzer
        # result = EmailAnalyzer.analyze(email_json)
        logger.info(f"Passing to CrewAI agent: {email_json}")
        return Response({'status': 'received', 'email_json': email_json}, status=status.HTTP_200_OK)
