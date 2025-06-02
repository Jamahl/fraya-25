import requests
from typing import List, Dict, Any

API_URL = "http://localhost:8000/api/calendar/events/"

from crewai.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
from functions import (
    mcp1_google_calendar_create_detailed_event,
    mcp1_google_calendar_find_event,
    mcp1_google_calendar_delete_event,
    mcp1_google_calendar_update_event,
    mcp1_google_calendar_find_multiple_events
)

class MCPGoogleCalendarFindEventInput(BaseModel):
    calendarid: str = Field(..., description="Google Calendar ID")
    search_term: str = Field(..., description="Search term for event lookup")

# Local mock for development/testing only
# Remove all MCP tool wrappers and Tool objects

def find_calendar_event_via_mcp(*args, **kwargs):
    print("[MOCK] find_calendar_event_via_mcp called with:", args, kwargs)
    return {"status": "mocked", "args": args, "kwargs": kwargs}

    """
    Find Google Calendar events using the Composio MCP Google Calendar integration.
    Args:
        calendarid (str): Google Calendar ID.
        search_term (str): Search term for event lookup.
    Returns:
        dict: Result from MCP endpoint.
    """
    return mcp1_google_calendar_find_event(calendarid=calendarid, instructions=f"Find events for search: {search_term}")




    name="Find Google Calendar Event via MCP",
    description="Find Google Calendar events using the Composio MCP Google Calendar integration.",
    func=find_calendar_event_via_mcp,
    args_schema=MCPGoogleCalendarFindEventInput
)

class MCPGoogleCalendarFindMultipleEventsInput(BaseModel):
    calendarid: str = Field(..., description="Google Calendar ID")
    start_time: Optional[str] = Field(default=None, description="RFC3339 lower bound for event end time (optional)")
    end_time: Optional[str] = Field(default=None, description="RFC3339 upper bound for event start time (optional)")
    search_term: str = Field("", description="Search term for event lookup (optional)")

def find_multiple_calendar_events_via_mcp(*args, **kwargs):
    print("[MOCK] find_multiple_calendar_events_via_mcp called with:", args, kwargs)
    return {"status": "mocked", "args": args, "kwargs": kwargs}

    """
    Find multiple Google Calendar events using the Composio MCP Google Calendar integration.
    Args:
        calendarid (str): Google Calendar ID.
        start_time (str): RFC3339 lower bound for event end time (optional).
        end_time (str): RFC3339 upper bound for event start time (optional).
        search_term (str): Search term for event lookup (optional).
    Returns:
        dict: Result from MCP endpoint.
    """
    return mcp1_google_calendar_find_multiple_events(
        calendarid=calendarid,
        start_time=start_time,
        end_time=end_time,
        search_term=search_term,
        instructions=f"Find multiple events for search: {search_term}"
    )


    name="Find Multiple Google Calendar Events via MCP",
    description="Find multiple Google Calendar events using the Composio MCP Google Calendar integration.",
    func=find_multiple_calendar_events_via_mcp,
    args_schema=MCPGoogleCalendarFindMultipleEventsInput
)


class MCPGoogleCalendarCreateEventInput(BaseModel):
    calendarid: str = Field(..., description="Google Calendar ID")
    start__dateTime: str = Field(..., description="Event start time, RFC3339 format")
    end__dateTime: str = Field(..., description="Event end time, RFC3339 format")
    summary: str = Field(..., description="Event summary/title")
    description: str = Field("", description="Event description (optional)")
    location: str = Field("", description="Event location (optional)")

def create_calendar_event_via_mcp(*args, **kwargs):
    print("[MOCK] create_calendar_event_via_mcp called with:", args, kwargs)
    return {"status": "mocked", "args": args, "kwargs": kwargs}

    Create a Google Calendar event using the Composio MCP Google Calendar integration.
    Args:
        calendarid (str): Google Calendar ID.
        start__dateTime (str): Event start time (RFC3339).
        end__dateTime (str): Event end time (RFC3339).
        summary (str): Event summary/title.
        description (str): Event description (optional).
        location (str): Event location (optional).
    Returns:
        dict: Result from MCP endpoint.
    """
    return mcp1_google_calendar_create_detailed_event(
        calendarid=calendarid,
        start__dateTime=start__dateTime,
        end__dateTime=end__dateTime,
        summary=summary,
        description=description,
        location=location,
        instructions=f"Create event: {summary}"
    )


    name="Create Google Calendar Event via MCP",
    description="Create a Google Calendar event using the Composio MCP Google Calendar integration.",
    func=create_calendar_event_via_mcp,
    args_schema=MCPGoogleCalendarCreateEventInput
)


class MCPGoogleCalendarDeleteEventInput(BaseModel):
    calendarid: str = Field(..., description="Google Calendar ID")
    eventid: str = Field(..., description="Event ID to delete")

def delete_calendar_event_via_mcp(*args, **kwargs):
    print("[MOCK] delete_calendar_event_via_mcp called with:", args, kwargs)
    return {"status": "mocked", "args": args, "kwargs": kwargs}

    """
    Delete a Google Calendar event using the Composio MCP Google Calendar integration.
    Args:
        calendarid (str): Google Calendar ID.
        eventid (str): Event ID to delete.
    Returns:
        dict: Result from MCP endpoint.
    """
    return mcp1_google_calendar_delete_event(calendarid=calendarid, eventid=eventid)


    name="Delete Google Calendar Event via MCP",
    description="Delete a Google Calendar event using the Composio MCP Google Calendar integration.",
    func=delete_calendar_event_via_mcp,
    args_schema=MCPGoogleCalendarDeleteEventInput
)


class MCPGoogleCalendarUpdateEventInput(BaseModel):
    calendarid: str = Field(..., description="Google Calendar ID")
    eventid: str = Field(..., description="Event ID to update")
    start__dateTime: str = Field(None, description="Event start time, RFC3339 format (optional)")
    end__dateTime: str = Field(None, description="Event end time, RFC3339 format (optional)")
    summary: str = Field(None, description="Event summary/title (optional)")
    description: str = Field(None, description="Event description (optional)")
    location: str = Field(None, description="Event location (optional)")

def update_calendar_event_via_mcp(*args, **kwargs):
    print("[MOCK] update_calendar_event_via_mcp called with:", args, kwargs)
    return {"status": "mocked", "args": args, "kwargs": kwargs}

    """
    Update (reschedule or edit) a Google Calendar event using the Composio MCP Google Calendar integration.
    Args:
        calendarid (str): Google Calendar ID.
        eventid (str): Event ID to update.
        start__dateTime (str): Event start time (optional).
        end__dateTime (str): Event end time (optional).
        summary (str): Event summary/title (optional).
        description (str): Event description (optional).
        location (str): Event location (optional).
    Returns:
        dict: Result from MCP endpoint.
    """
    return mcp1_google_calendar_update_event(
        calendarid=calendarid,
        eventid=eventid,
        start__dateTime=start__dateTime,
        end__dateTime=end__dateTime,
        summary=summary,
        description=description,
        location=location,
        instructions=f"Update event {eventid}"
    )


    name="Update Google Calendar Event via MCP",
    description="Update (reschedule or edit) a Google Calendar event using the Composio MCP Google Calendar integration.",
    func=update_calendar_event_via_mcp,
    args_schema=MCPGoogleCalendarUpdateEventInput
)

from pydantic import BaseModel, Field

class SearchCalendarEventsInput(BaseModel):
    user_id: str = Field(..., description="The user's unique identifier.")
    query: str = Field(..., description="Search query string.")

def search_calendar_events_tool(user_id: str, query: str):
    """
    Search for calendar events matching a query for a given user_id.
    Args:
        user_id (str): The user's unique identifier.
        query (str): Search query string.
    Returns:
        list: List of matching event dicts.
    """
    resp = requests.get(API_URL, params={"user_id": user_id, "query": query})
    resp.raise_for_status()
    return resp.json().get("events", [])

class DeleteCalendarEventInput(BaseModel):
    user_id: str = Field(..., description="The user's unique identifier.")
    event_id: str = Field(..., description="The event's unique identifier.")

def delete_calendar_event_tool(user_id: str, event_id: str):
    """
    Delete a calendar event for a given user_id and event_id.
    Args:
        user_id (str): The user's unique identifier.
        event_id (str): The event's unique identifier.
    Returns:
        dict: Status of deletion.
    """
    url = f"{API_URL}{event_id}/"
    resp = requests.delete(url, params={"user_id": user_id})
    resp.raise_for_status()
    return resp.json() if resp.content else {"status": "deleted", "event_id": event_id}

class RescheduleCalendarEventInput(BaseModel):
    user_id: str = Field(..., description="The user's unique identifier.")
    event_id: str = Field(..., description="The event's unique identifier.")
    new_time: str = Field(..., description="The new time in ISO format.")

def reschedule_calendar_event_tool(user_id: str, event_id: str, new_time: str):
    """
    Reschedule a calendar event to a new time.
    Args:
        user_id (str): The user's unique identifier.
        event_id (str): The event's unique identifier.
        new_time (str): The new time in ISO format.
    Returns:
        dict: Updated event data.
    """
    url = f"{API_URL}{event_id}/"
    resp = requests.patch(url, json={"user_id": user_id, "new_time": new_time})
    resp.raise_for_status()
    return resp.json()

class MCPGoogleCalendarCreateEventInput(BaseModel):
    calendarid: str = Field(..., description="Google Calendar ID")
    start__dateTime: str = Field(..., description="Event start time, RFC3339 format")
    end__dateTime: str = Field(..., description="Event end time, RFC3339 format")
    summary: str = Field(..., description="Event summary/title")

def create_calendar_event_via_mcp(calendarid: str, start__dateTime: str, end__dateTime: str, summary: str):
    """
    Create a Google Calendar event using the Composio MCP Google Calendar integration.
    Args:
        calendarid (str): Google Calendar ID.
        start__dateTime (str): Event start time (RFC3339).
        end__dateTime (str): Event end time (RFC3339).
        summary (str): Event summary/title.
    Returns:
        dict: Result from MCP endpoint.
    """
    return mcp1_google_calendar_create_detailed_event(
        calendarid=calendarid,
        start__dateTime=start__dateTime,
        end__dateTime=end__dateTime,
        summary=summary,
        instructions=f"Create event: {summary}"
    )
