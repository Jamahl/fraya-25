from django.urls import path
from .views import GmailWebhookView, StoreGoogleTokenView, PreferencesView

urlpatterns = [
    path('gmail/webhook/', GmailWebhookView.as_view(), name='gmail-webhook'),
    path('store-google-token/', StoreGoogleTokenView.as_view(), name='store-google-token'),
    path('preferences/', PreferencesView.as_view(), name='preferences'),
]
