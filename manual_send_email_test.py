import uuid
import logging

# Mock User model and SendEmailView logic for standalone test
class MockUser:
    def __init__(self, id, email, google_refresh_token):
        self.id = id
        self.email = email
        self.google_refresh_token = google_refresh_token

# Simulate a user database
mock_users = {}

def get_user(user_id):
    return mock_users.get(user_id)

# Simulate SendEmailView logic
def send_email(user_id, to, subject, body):
    if not user_id or not to or not subject or not body:
        return {'error': 'Missing required fields'}, 400
    user = get_user(user_id)
    if not user:
        return {'error': 'User not found'}, 404
    logging.info(f"[MOCK SEND EMAIL] to={to}, subject={subject}, body={body}, user_id={user_id}")
    return {
        'status': 'sent',
        'to': to,
        'subject': subject,
        'body': body,
        'user_id': user_id
    }, 200

if __name__ == "__main__":
    # Setup: create a mock user
    user_id = str(uuid.uuid4())
    mock_users[user_id] = MockUser(user_id, "standalone@example.com", "mocktoken")

    # Test: valid send
    result, code = send_email(user_id, "recipient@example.com", "Hello", "Test email body.")
    print(f"Valid send (should be 200): {code}")
    print(result)

    # Test: missing fields
    result, code = send_email(user_id, "recipient@example.com", None, "Test email body.")
    print(f"Missing subject (should be 400): {code}")
    print(result)

    # Test: user not found
    result, code = send_email("nonexistent-id", "recipient@example.com", "Hello", "Test email body.")
    print(f"User not found (should be 404): {code}")
    print(result)
