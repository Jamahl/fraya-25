import os
import django
import logging
import sys
import time
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import agentops
from crew import process_email

agentops.init(
    api_key='067103c2-e2d0-4954-9b1d-707b36aa534f',
    default_tags=['crewai']
)

# Setup Django environment
import sys
import os
print('PYTHONPATH before insert:', sys.path)
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'apps', 'api'))
print('PYTHONPATH after insert:', sys.path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.api.api.settings')
import django
django.setup()

print('poll_gmail_and_process.py: Script started and Django initialized.')

from core.models import User, Preference
from packages.agents.email_analyzer_agent import EmailAnalyzerAgent

# Replace these with your actual Google API client credentials
GOOGLE_CLIENT_ID = '929092708820-g2ib79ieckdme5r9aot3qegqgeojm1gq.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'

logging.basicConfig(level=logging.INFO)

def get_preferences_for_user(user):
    try:
        pref = Preference.objects.get(user=user)
        return {
            'name': user.email,
            'preferred_days': pref.preferred_days or [],
            'preferred_times': pref.preferred_times or '',
            'tone': pref.tone or 'professional',
            'style': pref.style or 'concise',
        }
    except Preference.DoesNotExist:
        return {
            'name': user.email,
            'preferred_days': [],
            'preferred_times': '',
            'tone': 'professional',
            'style': 'concise',
        }

def process_new_emails_for_user(user):
    if not user.google_refresh_token:
        return None
    creds = Credentials(
        None,
        refresh_token=user.google_refresh_token,
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token"
    )
    return creds

def process_new_emails_for_user(user):
    if not user.google_refresh_token:
        print(f"No Gmail credentials for user {user.email}")
        return
    creds = Credentials(
        None,
        refresh_token=user.google_refresh_token,
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token"
    )
    service = build('gmail', 'v1', credentials=creds)
    # Track last processed email timestamp persistently
    ts_file = f".last_email_timestamp_{user.email.replace('@', '_').replace('.', '_')}"
    last_ts = 0
    if os.path.exists(ts_file):
        with open(ts_file, 'r') as f:
            try:
                last_ts = int(f.read().strip())
            except Exception:
                last_ts = 0
    results = service.users().messages().list(
        userId='me', labelIds=['INBOX'], q='category:primary is:unread', maxResults=10
    ).execute()
    messages = results.get('messages', [])
    if not messages:
        print(f"No unread emails for user {user.email} in INBOX.")
        logging.info(f"No unread emails for user={user.email} in INBOX.")
        return
    # Gather all unread emails with their internalDate
    msg_details = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        internal_date = int(msg_data.get('internalDate', '0'))
        msg_details.append((internal_date, msg_data))
    # Sort by internalDate ascending (oldest to newest)
    msg_details.sort(key=lambda x: x[0])
    newest_processed_ts = last_ts
    for internal_date, msg_data in msg_details:
        if internal_date <= last_ts:
            continue  # Already processed
        msg_id = msg_data['id']
        headers = {h['name']: h['value'] for h in msg_data['payload'].get('headers', [])}
        email_json = {
            'from': headers.get('From', ''),
            'to': headers.get('To', ''),
            'timestamp': datetime.utcfromtimestamp(internal_date / 1000).isoformat() + 'Z',
            'subject': headers.get('Subject', ''),
            'body': msg_data['snippet'],
            'message_id': msg_id
        }
        logging.info(f"[NEW EMAIL] user={user.email}: {email_json}")
        print("\n===== New Email Detected in Primary Inbox =====")
        print(f"From:      {email_json['from']}")
        print(f"To:        {email_json['to']}")
        print(f"Timestamp: {email_json['timestamp']}")
        print(f"\033[92m[NEW EMAIL]\033[0m {email_json['from']} -> {email_json['to']} | Subject: {email_json['subject']} | Date: {email_json['timestamp']}")
        print(f"\033[96m{email_json['body']}\033[0m\n")
        # Process email with CrewAI crew
        process_email(email_json, creds)
        # Mark as read after processing
        service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()
        logging.info(f"Marked email as read for user={user.email}, message_id={msg_id}")
        newest_processed_ts = max(newest_processed_ts, internal_date)
    # Save the timestamp of the latest processed email
    if newest_processed_ts > last_ts:
        with open(ts_file, 'w') as f:
            f.write(str(newest_processed_ts))

def main():
    POLL_INTERVAL_SECONDS = 30
    while True:
        users = User.objects.exclude(google_refresh_token__isnull=True).exclude(google_refresh_token='')
        print(f'Polling: Found {users.count()} users with refresh tokens.')
        for user in users:
            print(f'Processing user: {user.email}')
            process_new_emails_for_user(user)
        print(f'Polling complete. Sleeping {POLL_INTERVAL_SECONDS} seconds...')
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
