class EmailAnalyzerAgent:
    """
    Analyzes incoming emails to determine user intent, extract entities, and summarize content for downstream agents.
    """
    def __init__(self, preferences: dict):
        """
        Initialize the agent with user preferences from the Supabase database.
        Generate a personalized backstory and task for the LLM.
        """
        self.preferences = preferences
        name = preferences.get('name', 'Unknown')
        days = ', '.join(preferences.get('preferred_days', [])) or 'not set'
        times = preferences.get('preferred_times', 'not set')
        tone = preferences.get('tone', 'professional')
        style = preferences.get('style', 'concise')
        self.backstory = (
            f"You are the Email Analyzer Agent for Fraya, an AI executive assistant. "
            f"Your user is {name}. "
            f"Your name is Fraya and you sign off emails as Fraya - Jamahl's AI EA."
            f"Their preferred meeting days are {days}. "
            f"Their preferred times are {times}. "
            f"Your user prefers a {tone} tone and {style} communication style. "
            "You are an expert at understanding email context, extracting key entities, and summarizing intent. "
            "You are fast, accurate, and always maintain strict privacy and professionalism."
        )
        self.task = (
            "Given an incoming email and the user's preferences, extract the user's intent (e.g., schedule, reply, forward), "
            "identify important entities (people, dates, topics), and summarize the message for other agents."
        )

    def analyze(self, email_data: dict) -> dict:
        """
        Analyze an email and return structured intent, action, and all required fields for orchestration.
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"EmailAnalyzerAgent input: {email_data}")
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        reply = None
        # Extract entities and intent
        result = {
            "intent": None,
            "action": None,
            "entities": [],
            "summary": "",
        }
        # Schedule intent
        if 'meeting' in subject or 'meeting' in body or 'schedule' in subject or 'schedule' in body:
            result["intent"] = "schedule"
            result["action"] = "propose_time"
            result["summary"] = "User may want to schedule a meeting."
            try:
                from .calendar_utils import get_calendar_events
                user_id = self.preferences.get('user_id') or self.preferences.get('id')
                calendar_events = get_calendar_events(user_id) if user_id else []
            except Exception as e:
                logger.exception("Failed to fetch calendar events")
                calendar_events = []
            result["calendar_events"] = calendar_events
        # Search intent
        elif 'search' in subject or 'search' in body:
            result["intent"] = "search"
            result["action"] = "search_events"
            # Dummy extraction for query
            result["query"] = email_data.get('query', 'meeting')
            result["summary"] = "User requested a search for calendar events."
        # Delete intent
        elif 'cancel' in subject or 'cancel' in body or 'delete' in subject or 'delete' in body:
            result["intent"] = "delete"
            result["action"] = "delete_event"
            # Dummy extraction for event_id
            result["event_id"] = email_data.get('event_id', 'dummy_event_id')
            result["summary"] = "User requested to delete/cancel a meeting."
        # Reschedule intent
        elif 'reschedule' in subject or 'reschedule' in body or 'move' in subject or 'move' in body:
            result["intent"] = "reschedule"
            result["action"] = "reschedule_event"
            result["event_id"] = email_data.get('event_id', 'dummy_event_id')
            result["new_time"] = email_data.get('new_time', '2025-06-10T10:00:00Z')
            result["summary"] = "User requested to reschedule a meeting."
        # Create/schedule event intent
        elif 'book' in subject or 'book' in body or 'create' in subject or 'create' in body:
            result["intent"] = "create"
            result["action"] = "schedule_event"
            result["event_data"] = email_data.get('event_data', {'title': 'Meeting', 'start_time': '2025-06-10T10:00:00Z', 'end_time': '2025-06-10T11:00:00Z'})
            result["summary"] = "User requested to book/schedule a meeting."
        # Reply intent (fallback)
        elif 'reply' in subject or 'reply' in body or 'respond' in subject or 'respond' in body:
            result["intent"] = "reply"
            result["action"] = "reply_email"
            reply = email_data.get('reply', 'Thank you for your message.')
            result["reply"] = reply
            result["summary"] = "User requested a reply to this email."
        else:
            result["intent"] = "general"
            result["action"] = "analyze"
            result["summary"] = "No specific scheduling/search/delete/reschedule intent detected."
        logger.info(f"EmailAnalyzerAgent output: {result}")
        return result
