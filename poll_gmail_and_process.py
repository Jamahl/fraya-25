import os
from dotenv import load_dotenv
load_dotenv()
import django
import logging
import sys
import time
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import agentops
from crew import process_email
from crewai_tools import MCPServerAdapter

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
# Requires environment variables: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

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

def get_tool(mcp_tools, name):
    for tool in mcp_tools:
        if tool.name == name or tool.name.lower() == name.lower():
            return tool
    raise ValueError(f"Tool {name} not found in MCP tools")

def process_new_emails_for_user(user, mcp_tools):
    """
    Poll unread emails for the user using MCP-native Gmail fetch, process with CrewAI, and mark as read.
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        fetch_emails_tool = get_tool(mcp_tools, "GMAIL_FETCH_EMAILS")
        move_to_trash_tool = get_tool(mcp_tools, "GMAIL_MOVE_TO_TRASH")
    except Exception as lookup_exc:
        logger.error(f"Could not find required MCP tools: {lookup_exc}")
        return

    # Use MCP-native tool to fetch unread emails for the user
    try:
        logger.info(f"Using Tool: {fetch_emails_tool.name}")
        emails_response = fetch_emails_tool.run(
            user_id=user.email,
            label_ids=["INBOX", "UNREAD"],
            max_results=10,
            include_payload=True
        )
        logger.info(f"Raw tool response: {repr(emails_response)}")
        # Ensure emails_response is a dict, not a JSON string
        if isinstance(emails_response, str):
            import json
            try:
                emails_response = json.loads(emails_response)
            except Exception:
                logger.error(f"Tool returned non-JSON string: {emails_response}")
                return
        emails = emails_response.get("messages", [])
        if not emails:
            logger.info(f"No unread emails for user={user.email} in INBOX.")
            return
        for email in emails:
            payload = email.get("payload", {})
            headers = {h['name']: h['value'] for h in payload.get('headers', [])}
            internal_date = int(email.get('internalDate', '0'))
            email_json = {
                'from': headers.get('From', ''),
                'to': headers.get('To', ''),
                'timestamp': datetime.utcfromtimestamp(internal_date / 1000).isoformat() + 'Z',
                'subject': headers.get('Subject', ''),
                'body': email.get('snippet', ''),
                'message_id': email.get('id', ''),
                'thread_id': email.get('threadId', '')
            }
            logger.info(f"[NEW EMAIL][MCP] user={user.email}: {email_json}")
            print("\n===== New Email Detected in Primary Inbox (MCP) =====")
            print(f"From:      {email_json['from']}")
            print(f"To:        {email_json['to']}")
            print(f"Timestamp: {email_json['timestamp']}")
            print(f"\033[92m[NEW EMAIL]\033[0m {email_json['from']} -> {email_json['to']} | Subject: {email_json['subject']} | Date: {email_json['timestamp']}")
            print(f"\033[96m{email_json['body']}\033[0m\n")
            # Process email with CrewAI crew
            process_email(email_json, mcp_tools)
            # Mark as read after processing
            try:
                move_to_trash_tool.run(
                    message_id=email_json['message_id'],
                    user_id=user.email
                )
                logger.info(f"Marked email as read (moved to trash) for user={user.email}, message_id={email_json['message_id']}")
            except Exception as mark_exc:
                logger.warning(f"Failed to mark email as read for user={user.email}, message_id={email_json['message_id']}: {mark_exc}")
    except Exception as exc:
        import traceback
        logger.error(f"MCP Gmail fetch failed for user={user.email}: {repr(exc)}")
        logger.error(traceback.format_exc())
        return

import anyio
from mcp.shared.exceptions import McpError

def resilient_main():
    POLL_INTERVAL_SECONDS = 30
    RECONNECT_SLEEP_SECONDS = 60
    server_params = [
        {"url": "https://mcp.composio.dev/partner/composio/gmail?customerId=9467730e-5b69-44c9-9b26-4e0c67893c96&transport=sse", "transport": "sse"},
        {"url": "https://mcp.composio.dev/partner/composio/googlecalendar?customerId=9467730e-5b69-44c9-9b26-4e0c67893c96&transport=sse", "transport": "sse"},
    ]
    import logging
    logger = logging.getLogger(__name__)
    while True:
        try:
            with MCPServerAdapter(server_params) as mcp_tools:
                users = User.objects.exclude(google_refresh_token__isnull=True).exclude(google_refresh_token='')
                logger.info(f'Polling: Found {users.count()} users with refresh tokens.')
                for user in users:
                    logger.info(f'Processing user: {user.email}')
                    process_new_emails_for_user(user, mcp_tools)
            logger.info(f'Polling complete. Sleeping {POLL_INTERVAL_SECONDS} seconds...')
            time.sleep(POLL_INTERVAL_SECONDS)
        except (anyio.ClosedResourceError, McpError) as e:
            logger.error(f"MCP connection closed, reconnecting in {RECONNECT_SLEEP_SECONDS} seconds... {e}")
            time.sleep(RECONNECT_SLEEP_SECONDS)
        except Exception as e:
            import traceback
            logger.error(f"Unexpected error, reconnecting in {RECONNECT_SLEEP_SECONDS} seconds... {e}")
            logger.error(traceback.format_exc())
            time.sleep(RECONNECT_SLEEP_SECONDS)


if __name__ == "__main__":
    resilient_main()
