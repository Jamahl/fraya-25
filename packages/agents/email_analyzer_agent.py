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
        """
        pass
