class CalendarAgent:
    """
    Handles all calendar-related tasks: scheduling, rescheduling, and deleting meetings, as well as checking availability.
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
            f"You are the Calendar Agent for Fraya, an AI executive assistant. "
            f"Your user is {name}. "
            f"Their preferred meeting days are {days}. "
            f"Their preferred times are {times}. "
            f"Your user prefers a {tone} tone and {style} communication style. "
            "You are detail-oriented, efficient, and have deep expertise in managing schedules and logistics. "
            "You always respect user preferences and organizational priorities."
        )
        self.task = (
            "Given a scheduling request and the user's preferences, check availability, schedule, reschedule, or delete meetings as needed, "
            "and communicate outcomes to the user and other agents."
        )

    def schedule_event(self, event_data: dict) -> dict:
        """
        Schedule a new event and return confirmation, considering user preferences.
        """
        pass

    def reschedule_event(self, event_id: str, new_time: str) -> dict:
        """
        Reschedule an existing event and return result, considering user preferences.
        """
        pass

    def delete_event(self, event_id: str) -> dict:
        """
        Delete an event and return result, considering user preferences.
        """
        pass
