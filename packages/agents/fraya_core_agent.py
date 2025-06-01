class FrayaCoreAgent:
    """
    The orchestrator agent. Delegates tasks to specialized agents (email, calendar, reply), manages state, and coordinates multi-step AI workflows for the user.
    """
    def __init__(self, preferences: dict):
        """
        Initialize the core agent with user preferences from the Supabase database.
        Generate a personalized backstory and task for the LLM.
        """
        self.preferences = preferences
        name = preferences.get('name', 'Unknown')
        days = ', '.join(preferences.get('preferred_days', [])) or 'not set'
        times = preferences.get('preferred_times', 'not set')
        tone = preferences.get('tone', 'professional')
        style = preferences.get('style', 'concise')
        self.backstory = (
            f"You are FrayaCore, the central orchestrator agent for Fraya, an AI executive assistant. "
            f"Your user is {name}. "
            f"Their preferred meeting days are {days}. "
            f"Their preferred times are {times}. "
            f"Your user prefers a {tone} tone and {style} communication style. "
            "You are highly organized, strategic, and excel at breaking down complex goals into actionable steps. "
            "You coordinate specialized agents and ensure seamless, effective execution of user requests."
        )
        self.task = (
            "Receive high-level user requests, decompose them into tasks, and delegate to the appropriate specialized agent. "
            "Track state, ensure completion, and handle multi-agent workflows for a flawless executive assistant experience."
        )

    def delegate(self, task_type: str, data: dict):
        """
        Delegate a task to the appropriate agent based on type, always considering user preferences.
        """
        pass
