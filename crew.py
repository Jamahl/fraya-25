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

from crewai import Agent, Task, Crew
from crewai_tools import MCPServerAdapter
from agent_prompts import EMAIL_ANALYZER_PROMPT, REPLY_AGENT_PROMPT, REPLY_TEMPLATE
import logging

VERBOSE = True  # Toggle verbose debug output here


def process_email(email_json, mcp_tools, creds=None):
    """
    Process a single email JSON object through the CrewAI pipeline.
    creds: Gmail API credentials for sending replies (optional)
    mcp_tools: List of tools loaded from MCPServerAdapter
    """
    preferences = {
        "name": "jamahl.mcmurran@gmail.com",
        "preferred_days": ["Tuesday", "Wednesday"],
        "preferred_times": "09:00-11:00",
        "tone": "professional",
        "style": "concise",
        # Hardcoded Supabase user_id for jamahl.mcmurran@gmail.com
        "user_id": "2c6926f5-5a1b-4a69-902b-7621348a9147"
    }
    # Define CrewAI agents
    analyzer_agent = Agent(
        role="Email Analyzer - you are a professional Executive Assistant and Email Analyser, your job is to understand the intent of the email you are receiving.",
        goal="Analyze emails, extract intent and pass along your findings.",
        backstory=EMAIL_ANALYZER_PROMPT,
        tools=mcp_tools,
        verbose=True,
    )
    reply_agent = Agent(
        role="Reply Agent - you are a professional Executive Assistant. ",
        goal="Draft email replies using preferences and calendar availability.",
        backstory=REPLY_AGENT_PROMPT,
        tools=mcp_tools,
        verbose=True,
    )
    # Define tasks
    analyze_task = Task(
        description="Analyze the incoming email and extract scheduling intent.",
        expected_output="Intent, entities, and calendar events.",
        agent=analyzer_agent
    )
    reply_task = Task(
        description="Draft a reply if the intent is scheduling, this includes rearranging a meeting or cancelling a meeting.",
        expected_output="Drafted reply. Always end with Fraya - Jamahl's AI Executive Assistant. Always refer to the participants by their names, do not make them up or guess.",
        agent=reply_agent
    )
    # Create the crew
    crew = Crew(
        agents=[analyzer_agent, reply_agent],
        tasks=[analyze_task, reply_task],
        verbose=True,
        step_callback=print
    )
    # Run the crew
    result = crew.kickoff(email_json)
    print("[CrewAI] FINAL OUTPUT:", result)
    logging.info(f"[CrewAI] Final output: {result}")

    # No direct orchestration of tools: agents will call tools themselves.
    return

import requests
API_URL = "http://localhost:8000/api/calendar/events/"

def search_calendar_events(user_id, query):
    resp = requests.get(API_URL, params={"user_id": user_id, "query": query})
    resp.raise_for_status()
    return resp.json().get("events", [])

def delete_calendar_event(user_id, event_id):
    url = f"{API_URL}{event_id}/"
    resp = requests.delete(url, params={"user_id": user_id})
    resp.raise_for_status()
    return resp.json() if resp.content else {"status": "deleted", "event_id": event_id}

def reschedule_calendar_event(user_id, event_id, new_time):
    url = f"{API_URL}{event_id}/"
    resp = requests.patch(url, json={"user_id": user_id, "new_time": new_time})
    resp.raise_for_status()
    return resp.json()

def schedule_calendar_event(user_id, event_data):
    resp = requests.post(API_URL, json={"user_id": user_id, **event_data})
    resp.raise_for_status()
    return resp.json()

# For testing and script entry
if __name__ == "__main__":
    # Configure your MCP server params here (SSE, HTTP, or Stdio)
    server_params = [
        {"url": "https://mcp.composio.dev/partner/composio/gmail?customerId=YOUR_ID&transport=sse", "transport": "sse"},
        {"url": "https://mcp.composio.dev/partner/composio/googlecalendar?customerId=YOUR_ID&transport=sse", "transport": "sse"},
    ]
    test_email = {
        'from': 'someone@example.com',
        'to': 'jamahl.mcmurran@gmail.com',
        'timestamp': '2025-06-01T16:00:00Z',
        'subject': 'Can we meet next week?',
        'body': 'Hi, are you available for a meeting on Tuesday?',
        'message_id': 'abc123',
    }
    with MCPServerAdapter(server_params) as mcp_tools:
        print(f"Loaded MCP tools: {[tool.name for tool in mcp_tools]}")
        process_email(test_email, mcp_tools)
