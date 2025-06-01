from packages.agents.email_analyzer_agent import EmailAnalyzerAgent

# Test with friendly tone and preferences
preferences1 = {
    'name': 'Test User',
    'preferred_days': ['Monday', 'Wednesday'],
    'preferred_times': 'morning',
    'tone': 'friendly',
    'style': 'concise'
}
agent1 = EmailAnalyzerAgent(preferences1)
email_data = {
    'sender': 'someone@example.com',
    'subject': "Let's schedule a meeting",
    'body': 'Are you free next week for a meeting?',
    'to': ['me@example.com'],
    'cc': [],
    'time': '2025-06-01T00:00:00Z'
}
result1 = agent1.analyze(email_data)
print('Friendly tone with preferences:')
print(result1)

# Test with professional tone and no preferences
preferences2 = {
    'name': 'Test User',
    'preferred_days': [],
    'preferred_times': '',
    'tone': 'professional',
    'style': 'concise'
}
agent2 = EmailAnalyzerAgent(preferences2)
result2 = agent2.analyze(email_data)
print('\nProfessional tone, no preferences:')
print(result2)
