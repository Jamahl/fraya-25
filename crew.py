"""
crew.py

Entry point for Fraya AI CrewAI workflow integration.
This module receives new emails and routes them to the CrewAI crew for contextual analysis and action (e.g., booking meetings, drafting/sending replies).

Backstory, crew structure, and agent roles are aligned with architecture.md and tasks.md:
- The ReplyAgent (see packages/agents/reply_agent.py) drafts contextual replies based on user preferences and conversation context.
- The EmailAnalyzerAgent analyzes intent and user preferences.
- CrewAI crew coordinates agents to decide and take actions.

This file exposes process_email(email_json) as the main entry point for polling scripts.
"""

from packages.agents.reply_agent import ReplyAgent
from packages.agents.email_analyzer_agent import EmailAnalyzerAgent
from packages.services_gmail import send_email_via_gmail
import logging

def process_email(email_json, creds=None):
    """
    Process a single email JSON object through the CrewAI pipeline.
    creds: Gmail API credentials for sending replies (optional)
    """
    # For now, use hardcoded preferences. Extend to fetch from DB if needed.
    preferences = {
        "name": "jamahl.mcmurran@gmail.com",
        "preferred_days": ["Tuesday", "Wednesday"],
        "preferred_times": "09:00-11:00",
        "tone": "professional",
        "style": "concise"
    }
    analyzer = EmailAnalyzerAgent(preferences)
    analysis = analyzer.analyze(email_json)
    logging.info(f"[CrewAI] Email analysis: {analysis}")

    # If the email requests scheduling, draft a reply
    if analysis.get('intent') == 'schedule':
        reply_agent = ReplyAgent(preferences)
        try:
            reply = reply_agent.draft_reply(email_json)
        except NotImplementedError:
            reply = "[ReplyAgent.draft_reply not implemented]"
        logging.info(f"[CrewAI] Drafted reply: {reply}")
        if creds and reply:
            # Send reply via Gmail
            sent_id = send_email_via_gmail(
                creds=creds,
                sender=email_json.get('to'),
                to=email_json.get('from'),
                subject=f"Re: {email_json.get('subject', '')}",
                body=reply
            )
            if sent_id:
                print(f"[CrewAI] Reply sent to {email_json.get('from')} (message id: {sent_id})")
                logging.info(f"[CrewAI] Reply sent to {email_json.get('from')} (message id: {sent_id})")
            else:
                print(f"[CrewAI] Failed to send reply to {email_json.get('from')}")
                logging.error(f"[CrewAI] Failed to send reply to {email_json.get('from')}")
        else:
            print(f"[CrewAI] Would send reply: {reply}")
    else:
        logging.info("[CrewAI] No scheduling intent detected, no reply drafted.")

    # TODO: Implement further CrewAI actions (calendar integration, auto-send, etc.)
    return

# For testing
if __name__ == "__main__":
    test_email = {
        'from': 'someone@example.com',
        'to': 'jamahl.mcmurran@gmail.com',
        'timestamp': '2025-06-01T16:00:00Z',
        'subject': 'Can we meet next week?',
        'body': 'Hi, are you available for a meeting on Tuesday?',
        'message_id': 'abc123',
    }
    process_email(test_email)
