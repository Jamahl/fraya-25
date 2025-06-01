import os
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_ID = "929092708820-g2ib79ieckdme5r9aot3qegqgeojm1gq.apps.googleusercontent.com"
CLIENT_SECRET = "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"
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify"
]

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    },
    SCOPES
)

"""
Run this script to obtain a Gmail OAuth refresh token for polling Gmail.
If you get 'Refresh Token: None', go to https://myaccount.google.com/permissions, remove this app's access, and run the script again.
"""

creds = flow.run_local_server(
    port=8080,
    redirect_uri_trailing_slash=True,
    authorization_prompt_message='Please visit this URL: {url}',
    success_message='Authentication complete. You may close this window.',
    open_browser=True,
    extra_authorize_params={
        'access_type': 'offline',
        'prompt': 'consent',
        'include_granted_scopes': 'true'
    }
)
print("Access Token:", creds.token)
if creds.refresh_token:
    print("Refresh Token:", creds.refresh_token)
    # Try to get email from id_token, else prompt
    email = None
    if creds.id_token and creds.id_token.get('email'):
        email = creds.id_token.get('email')
    else:
        email = input("Enter your Gmail address to save refresh token to DB: ").strip()
    # Save to Django DB
    try:
        import sys, os
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.api.api.settings')
        import django
        django.setup()
        from core.models import User
        user, created = User.objects.get_or_create(email=email)
        user.google_refresh_token = creds.refresh_token
        user.save()
        print(f"Refresh token saved to user {user.email} in Django DB.")
    except Exception as e:
        print(f"WARNING: Could not save to Django DB: {e}")
else:
    print("WARNING: No refresh token received. Go to https://myaccount.google.com/permissions, remove this app's access, and run again.")
