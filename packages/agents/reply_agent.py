class ReplyAgent:
    """
    Drafts contextual, personalized replies to emails based on user preferences and conversation context.
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
            f"You are the Reply Agent for Fraya, an AI executive assistant. "
            f"Your user is {name}. "
            f"Their preferred meeting days are {days}. "
            f"Their preferred times are {times}. "
            f"Your user prefers a {tone} tone and {style} communication style. "
            "You are a master communicator, skilled at crafting clear, effective, and personalized responses. "
            "You adapt your style to the user's tone and goals, and always maintain professionalism."
        )
        self.task = (
            "Given an email context and the user's preferences, draft a reply that is contextually appropriate, "
            "personalized, and aligns with the user's communication style."
        )

    def draft_reply(self, email_context: dict) -> str:
        """
        Draft a reply to an email, using the agent's user preferences for tone, style, and context.
        """
        subject = email_context.get("subject", "your inquiry")
        sender = email_context.get("from", "there")
        tone = self.preferences.get("tone", "professional")
        name = self.preferences.get("name", "Fraya AI")
        if tone == "friendly":
            greeting = f"Hi {sender.split('@')[0]},"
            body = f"Thanks so much for reaching out about '{subject}'. I'd love to help you!"
            closing = f"Best,\n{name}"
        else:
            greeting = f"Hello {sender.split('@')[0]},"
            body = f"Thank you for your email regarding '{subject}'. I will review it and get back to you soon."
            closing = f"Regards,\n{name}"
        return f"{greeting}\n\n{body}\n\n{closing}"
