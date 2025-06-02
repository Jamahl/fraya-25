# Fraya AI – MCP-Native CrewAI Integration

Fraya AI is an executive assistant platform that leverages CrewAI agents, Composio MCP servers, and dynamic tool orchestration to automate Gmail and Google Calendar workflows.

## Features
- MCP-native integration: No manual tool wrappers, all Gmail/Calendar actions via MCPServerAdapter
- CrewAI agent orchestration for email analysis, reply, and scheduling
- Robust, future-proof, and secure architecture

## Prerequisites
- Python 3.11+
- pip3 (Python package manager)
- [Composio](https://composio.dev/) account with MCP access (get your customerId)
- Google Cloud project for OAuth (for Gmail/Calendar access)
- (Optional) Node.js, npm for frontend development

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd fraya
```

### 2. Create a Python virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip3 install --upgrade pip
pip3 install -r apps/api/requirements.txt
```

### 4. Set environment variables
Create a `.env` file in the root or set these in your shell:
```
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
```

### 5. Configure MCP Server URLs
The project is pre-configured for Composio MCP with your customerId. If you need to update, edit `poll_gmail_and_process.py`:
```
server_params = [
    {"url": "https://mcp.composio.dev/partner/composio/gmail?customerId=<your-id>&transport=sse", "transport": "sse"},
    {"url": "https://mcp.composio.dev/partner/composio/googlecalendar?customerId=<your-id>&transport=sse", "transport": "sse"},
]
```

### 6. Django setup (for backend API)
```bash
cd apps/api
python3 manage.py migrate
python3 manage.py createsuperuser  # (optional)
python3 manage.py runserver
```

### 7. Running the Email Poller
From the project root:
```bash
python3 poll_gmail_and_process.py
```
This will poll Gmail for unread emails for all users in your Django database with a Google refresh token, process them with CrewAI, and mark them as read.

## Notes
- **Do NOT add `mcp` to requirements.txt** – MCP support is provided by `crewai-tools[mcp]`.
- All MCP tools are dynamically loaded; do not import tool functions directly.
- For local development, you may use mock tool functions (see code comments).
- For production, ensure all MCP endpoints and credentials are correct.

## Troubleshooting
- If you see `ImportError: Failed to install mcp package`, ensure you have `crewai-tools[mcp]` installed and do not list `mcp` in requirements.txt.
- If MCP tools are not found, check your customerId and MCP server URLs.
- For any other issues, check logs or contact the maintainers.

## Useful Links
- [Composio MCP Docs](https://docs.composio.dev/)
- [CrewAI Tools](https://github.com/joaomdmoura/crewai-tools)
- [CrewAI MCP Demo](https://github.com/joaomdmoura/crewai-mcp-demo)

---

If you need help or want to extend Fraya, open an issue or contact the maintainers.
