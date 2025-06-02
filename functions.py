"""
Mock MCP functions for local development only.
This file allows agent code to import MCP tool functions (e.g., mcp2_GMAIL_SEND_EMAIL)
without raising ImportError. These mocks do NOT perform any real actions.
Remove or ignore this file when running in Cascade or MCP-injected environments.
"""

def mcp2_GMAIL_SEND_EMAIL(recipient_email, body, subject, is_html=False, **kwargs):
    print(f"[MOCK] Sending Gmail: to={recipient_email}, subject={subject}")
    return {"status": "mock_sent", "recipient": recipient_email, "subject": subject}

def mcp1_google_calendar_create_detailed_event(**kwargs):
    print(f"[MOCK] Creating Google Calendar event: {kwargs}")
    return {"status": "mock_event_created", "event": kwargs}

def mcp1_google_calendar_find_event(**kwargs):
    print(f"[MOCK] Finding Google Calendar event: {kwargs}")
    return {"status": "mock_event_found", "events": []}

def mcp1_google_calendar_find_multiple_events(**kwargs):
    print(f"[MOCK] Finding multiple Google Calendar events: {kwargs}")
    return {"status": "mock_multiple_events_found", "events": []}

def mcp1_google_calendar_delete_event(**kwargs):
    print(f"[MOCK] Deleting Google Calendar event: {kwargs}")
    return {"status": "mock_event_deleted", "event": kwargs}

def mcp1_google_calendar_update_event(**kwargs):
    print(f"[MOCK] Updating Google Calendar event: {kwargs}")
    return {"status": "mock_event_updated", "event": kwargs}
