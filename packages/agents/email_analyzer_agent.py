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
        Analyze an email and return structured intent and entities, considering user preferences.
        Logs input and output for traceability. Replace dummy logic with real analysis as needed.
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"EmailAnalyzerAgent input: {email_data}")
        # Dummy logic: Always returns category 'schedule' if 'meeting' in subject/body, else 'general'.
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        if 'meeting' in subject or 'meeting' in body:
            summary = "User may want to schedule a meeting."
            # Add tone
            tone = self.preferences.get('tone', 'professional')
            if tone == 'friendly':
                summary += " Please respond in a friendly manner."
            # Add preferred days/times
            preferred_days = self.preferences.get('preferred_days')
            if preferred_days:
                summary += f" Preferred days: {', '.join(preferred_days)}."
            preferred_times = self.preferences.get('preferred_times')
            if preferred_times:
                summary += f" Preferred times: {preferred_times}."
            result = {
                "intent": "schedule",
                "action": "propose_time",
                "entities": [],
                "summary": summary
            }
        else:
            result = {
                "intent": "general",
                "action": "analyze",
                "entities": [],
                "summary": "No scheduling intent detected."
            }
        logger.info(f"EmailAnalyzerAgent output: {result}")
        return result
