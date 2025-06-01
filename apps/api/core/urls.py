from django.urls import path
from .views import GmailWebhookView, StoreGoogleTokenView, PreferencesView, CalendarEventsView, SendEmailView

urlpatterns = [
    path('gmail/webhook/', GmailWebhookView.as_view(), name='gmail-webhook'),
    path('store-google-token/', StoreGoogleTokenView.as_view(), name='store-google-token'),
    path('preferences/', PreferencesView.as_view(), name='preferences'),
    path('calendar/events/', CalendarEventsView.as_view(), name='calendar-events'),
    path('send-email/', SendEmailView.as_view(), name='send-email'),
]
