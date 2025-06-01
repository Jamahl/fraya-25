from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import logging

def send_email_via_gmail(creds, sender, to, subject, body):
    """
    Send an email using the Gmail API.
    creds: google.oauth2.credentials.Credentials
    sender: str (email address)
    to: str or list of str
    subject: str
    body: str
    """
    if isinstance(to, list):
        to = ', '.join(to)
    message = MIMEText(body)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service = build('gmail', 'v1', credentials=creds)
    try:
        sent = service.users().messages().send(userId='me', body={'raw': raw}).execute()
        logging.info(f"Email sent to {to}: {sent.get('id')}")
        return sent.get('id')
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return None
